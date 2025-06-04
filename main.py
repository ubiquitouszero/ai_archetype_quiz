from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import os
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel

# Pydantic models
class QuizResponse(BaseModel):
    responses: Dict[str, str]

class QuizResult(BaseModel):
    session_id: str
    primary_archetype: str
    scores: Dict[str, int]
    archetype_data: Dict

# Load configuration
def load_json_file(filepath: str) -> dict:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filepath} not found. Using empty dict.")
        return {}

ARCHETYPES = load_json_file('data/archetypes.json')
QUESTIONS_DATA = load_json_file('data/questions.json')
QUESTIONS = QUESTIONS_DATA.get('questions', [])
ANSWER_MAPPING = QUESTIONS_DATA.get('mapping', {})

app = FastAPI(
    title="AI Archetype Quiz",
    description="Discover how you approach AI in the workplace",
    version="1.0.0"
)

# Middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# OAuth setup
oauth = OAuth()
if os.getenv('GOOGLE_CLIENT_ID'):
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

# Database initialization
def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('data/quiz.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            responses TEXT NOT NULL,
            primary_archetype TEXT NOT NULL,
            scores TEXT NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completion_time REAL,
            user_agent TEXT,
            ip_address TEXT,
            referrer TEXT
        )
    ''')
    
    # Create indexes for better query performance
    conn.execute('CREATE INDEX IF NOT EXISTS idx_primary_archetype ON submissions(primary_archetype)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_completed_at ON submissions(completed_at)')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def calculate_archetype_scores(responses: Dict[str, str]) -> Dict[str, int]:
    """Calculate archetype scores based on quiz responses"""
    scores = {archetype: 0 for archetype in ARCHETYPES.keys()}
    
    for question_id, answer in responses.items():
        if answer in ANSWER_MAPPING:
            archetype = ANSWER_MAPPING[answer]
            if archetype in scores:
                scores[archetype] += 1
    
    # Convert to percentages
    total = len(responses)
    if total > 0:
        percentages = {k: round((v / total) * 100) for k, v in scores.items()}
    else:
        percentages = {k: 0 for k in scores.keys()}
    
    return percentages

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('data/quiz.db')

# Authentication helper
async def get_current_user(request: Request):
    """Get current authenticated user"""
    user = request.session.get('user')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main quiz page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "archetypes": ARCHETYPES,
        "questions": QUESTIONS
    })

@app.get("/api/quiz/data")
async def get_quiz_data():
    """Get quiz questions and archetype data"""
    return {
        "questions": QUESTIONS,
        "archetypes": ARCHETYPES,
        "mapping": ANSWER_MAPPING
    }

@app.post("/api/quiz/submit")
async def submit_quiz(request: Request, quiz_data: QuizResponse):
    """Submit quiz responses and calculate results"""
    try:
        scores = calculate_archetype_scores(quiz_data.responses)
        primary_archetype = max(scores, key=scores.get) if scores else "Pioneer"
        session_id = str(uuid.uuid4())
        
        # Get additional metadata
        user_agent = request.headers.get("user-agent", "")
        ip_address = request.client.host if request.client else ""
        referrer = request.headers.get("referer", "")
        
        # Save to database
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO submissions 
                (session_id, responses, primary_archetype, scores, user_agent, ip_address, referrer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                json.dumps(quiz_data.responses),
                primary_archetype,
                json.dumps(scores),
                user_agent,
                ip_address,
                referrer
            ))
            conn.commit()
        finally:
            conn.close()
        
        return QuizResult(
            session_id=session_id,
            primary_archetype=primary_archetype,
            scores=scores,
            archetype_data=ARCHETYPES.get(primary_archetype, {})
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing quiz: {str(e)}")

@app.get("/results/{session_id}", response_class=HTMLResponse)
async def get_results(request: Request, session_id: str):
    """Display results page for a specific session"""
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            'SELECT primary_archetype, scores, completed_at FROM submissions WHERE session_id = ?',
            (session_id,)
        )
        result = cursor.fetchone()
    finally:
        conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Results not found")
    
    primary_archetype, scores_json, completed_at = result
    scores = json.loads(scores_json)
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "session_id": session_id,
        "primary_archetype": primary_archetype,
        "scores": scores,
        "archetype_data": ARCHETYPES.get(primary_archetype, {}),
        "all_archetypes": ARCHETYPES,
        "completed_at": completed_at
    })

@app.get("/summary", response_class=HTMLResponse)
async def public_summary(request: Request):
    """Public summary page showing aggregated statistics"""
    conn = get_db_connection()
    try:
        # Get archetype distribution
        cursor = conn.execute('''
            SELECT 
                primary_archetype, 
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM submissions), 1) as percentage
            FROM submissions 
            GROUP BY primary_archetype
            ORDER BY count DESC
        ''')
        
        stats = []
        total_submissions = 0
        for row in cursor.fetchall():
            archetype, count, percentage = row
            stats.append({
                "archetype": archetype,
                "count": count,
                "percentage": percentage,
                "data": ARCHETYPES.get(archetype, {})
            })
            total_submissions += count
        
        # Get recent activity (last 7 days)
        cursor = conn.execute('''
            SELECT COUNT(*) 
            FROM submissions 
            WHERE completed_at > datetime('now', '-7 days')
        ''')
        recent_count = cursor.fetchone()[0]
        
    finally:
        conn.close()
    
    return templates.TemplateResponse("summary.html", {
        "request": request,
        "stats": stats,
        "total_submissions": total_submissions,
        "recent_count": recent_count,
        "archetypes": ARCHETYPES
    })

# Admin OAuth routes
@app.get("/admin/login")
async def admin_login(request: Request):
    """Initiate OAuth login"""
    if not oauth.google:
        return JSONResponse({"error": "OAuth not configured"}, status_code=500)
    
    redirect_uri = request.url_for('admin_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/admin/callback")
async def admin_callback(request: Request):
    """Handle OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')
        if user:
            request.session['user'] = dict(user)
        return RedirectResponse(url='/admin/dashboard')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")

@app.get("/admin/logout")
async def admin_logout(request: Request):
    """Logout admin user"""
    request.session.clear()
    return RedirectResponse(url='/')

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, user=Depends(get_current_user)):
    """Admin dashboard page"""
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user
    })

@app.get("/api/admin/stats")
async def admin_stats(user=Depends(get_current_user)):
    """Get admin statistics"""
    conn = get_db_connection()
    try:
        # Archetype distribution
        cursor = conn.execute('''
            SELECT primary_archetype, COUNT(*) 
            FROM submissions 
            GROUP BY primary_archetype
            ORDER BY COUNT(*) DESC
        ''')
        distribution = dict(cursor.fetchall())
        
        # Recent submissions (last 50)
        cursor = conn.execute('''
            SELECT primary_archetype, completed_at, completion_time, session_id
            FROM submissions 
            ORDER BY completed_at DESC 
            LIMIT 50
        ''')
        recent = [
            {
                "archetype": row[0],
                "completed_at": row[1],
                "completion_time": row[2],
                "session_id": row[3]
            }
            for row in cursor.fetchall()
        ]
        
        # Total stats
        cursor = conn.execute('SELECT COUNT(*) FROM submissions')
        total = cursor.fetchone()[0]
        
        # Daily submissions (last 7 days)
        cursor = conn.execute('''
            SELECT DATE(completed_at) as date, COUNT(*) as count
            FROM submissions 
            WHERE completed_at > datetime('now', '-7 days')
            GROUP BY DATE(completed_at)
            ORDER BY date
        ''')
        daily_stats = dict(cursor.fetchall())
        
        # Average completion time
        cursor = conn.execute('''
            SELECT AVG(completion_time) 
            FROM submissions 
            WHERE completion_time IS NOT NULL
        ''')
        avg_time = cursor.fetchone()[0] or 0
        
    finally:
        conn.close()
    
    return {
        "total_submissions": total,
        "archetype_distribution": distribution,
        "recent_submissions": recent,
        "daily_stats": daily_stats,
        "average_completion_time": round(avg_time, 1),
        "archetype_data": ARCHETYPES
    }

@app.get("/api/admin/export")
async def export_data(user=Depends(get_current_user), format: str = "json"):
    """Export quiz data"""
    conn = get_db_connection()
    try:
        cursor = conn.execute('''
            SELECT session_id, responses, primary_archetype, scores, completed_at, completion_time
            FROM submissions 
            ORDER BY completed_at DESC
        ''')
        
        data = []
        for row in cursor.fetchall():
            data.append({
                "session_id": row[0],
                "responses": json.loads(row[1]),
                "primary_archetype": row[2],
                "scores": json.loads(row[3]),
                "completed_at": row[4],
                "completion_time": row[5]
            })
    finally:
        conn.close()
    
    if format == "csv":
        # TODO: Implement CSV export
        pass
    
    return {"data": data, "total": len(data)}

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
