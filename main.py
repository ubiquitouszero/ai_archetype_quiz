"""
AI Archetype Quiz with Analytics + Results Persistence
For acceleratinghumans.com podcast insights
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

app = FastAPI(title="AI Archetype Quiz")

# Database setup
DB_PATH = Path("data/quiz.db")
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    """Initialize database with analytics and results tables"""
    conn = sqlite3.connect(DB_PATH)
    
    # Results table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            primary_archetype TEXT NOT NULL,
            archetype_name TEXT NOT NULL,
            all_scores TEXT NOT NULL,
            responses TEXT NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completion_time REAL,
            user_agent TEXT,
            ip_address TEXT
        )
    ''')
    
    # Analytics table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            session_id TEXT,
            event_data TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    conn.execute('CREATE INDEX IF NOT EXISTS idx_results_archetype ON results(primary_archetype)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_results_completed ON results(completed_at)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics(event_type)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_analytics_created ON analytics(created_at)')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Pydantic models
class QuizSubmission(BaseModel):
    responses: Dict[str, str]
    completion_time: Optional[float] = None

class AnalyticsEvent(BaseModel):
    event_type: str
    session_id: Optional[str] = None
    data: Optional[Dict] = None

# Quiz data (embedded for reliability)
QUIZ_DATA = {
    "questions": [
        {
            "id": 1,
            "question": "When your company announces a new AI initiative, you:",
            "answers": {
                "A": "Volunteer to be a beta tester—why not?",
                "B": "Ask for a business case and expected outcomes.",
                "C": "Feel anxious—does this mean my job is at risk?",
                "D": "Worry about the ethics of moving too fast.",
                "E": "Think, 'These things never last.'",
                "F": "See a chance to make a name for yourself.",
                "G": "Ask how it will affect support staff and junior employees."
            }
        },
        {
            "id": 2,
            "question": "A colleague uses AI to finish a project in half the time. Your reaction?",
            "answers": {
                "A": "Ask them to show you how!",
                "B": "Wonder if the output quality was measured.",
                "C": "Secretly worry you can't keep up.",
                "D": "Raise questions about data privacy.",
                "E": "Feel skeptical about relying on a tool.",
                "F": "Brainstorm how to automate even more.",
                "G": "Check if anyone was left out or missed a chance to learn."
            }
        },
        {
            "id": 3,
            "question": "How do you keep up with AI trends?",
            "answers": {
                "A": "Subscribe to newsletters/podcasts, experiment often.",
                "B": "Wait for official company updates or reports.",
                "C": "Read headlines but feel overwhelmed.",
                "D": "Follow AI ethics forums or regulatory news.",
                "E": "Trust your usual industry publications.",
                "F": "Attend 'future of work' events and hackathons.",
                "G": "Watch for stories on AI's social impact."
            }
        },
        {
            "id": 4,
            "question": "Your leadership says AI will require 'reskilling.' You:",
            "answers": {
                "A": "Look up training courses right away.",
                "B": "Want a timeline, metrics, and job guarantees.",
                "C": "Worry you'll be left behind.",
                "D": "Want to ensure training is voluntary and fair.",
                "E": "Assume it's a passing phase.",
                "F": "Suggest creating new roles for AI strategists.",
                "G": "Volunteer to mentor those most at risk."
            }
        },
        {
            "id": 5,
            "question": "What's your biggest question about AI?",
            "answers": {
                "A": "How can I use it to work smarter?",
                "B": "How will we measure its success?",
                "C": "Will it replace my job?",
                "D": "What are the risks for us?",
                "E": "Is this just another management fad?",
                "F": "How can it help us beat competitors?",
                "G": "Who might be left behind?"
            }
        },
        {
            "id": 6,
            "question": "You're assigned to an AI implementation team. What's your role?",
            "answers": {
                "A": "Early adopter, hands-on tester.",
                "B": "Project manager, tracking results.",
                "C": "Quiet observer, taking it all in.",
                "D": "Policy checker, flagging concerns.",
                "E": "Reluctant participant.",
                "F": "Idea generator, pushing for more change.",
                "G": "Team advocate, focusing on inclusion."
            }
        },
        {
            "id": 7,
            "question": "How do you feel about 'AI replacing jobs?'",
            "answers": {
                "A": "It's a chance to move up or into new areas.",
                "B": "Only acceptable if it clearly benefits the business.",
                "C": "Anxious and uncertain.",
                "D": "It should be tightly controlled and monitored.",
                "E": "Unlikely—these changes are always overstated.",
                "F": "Opportunity to reinvent our organization.",
                "G": "Worrisome unless everyone is supported."
            }
        },
        {
            "id": 8,
            "question": "When a new AI policy is announced, you:",
            "answers": {
                "A": "Read it and look for ways to leverage it.",
                "B": "Study the details and ask for clarification.",
                "C": "Wait to see how it impacts you.",
                "D": "Check for privacy or bias safeguards.",
                "E": "Hope it doesn't change daily routines.",
                "F": "Argue for faster rollout.",
                "G": "Survey coworkers about their comfort level."
            }
        },
        {
            "id": 9,
            "question": "Your team faces a tight deadline. What's your approach?",
            "answers": {
                "A": "Use every tool, including AI, to get results.",
                "B": "Weigh risks vs. benefits before changing workflow.",
                "C": "Prefer to stick with what you know works.",
                "D": "Only use tools that have been vetted for fairness/ethics.",
                "E": "Avoid new tools under pressure.",
                "F": "Suggest splitting the work—humans + AI for speed.",
                "G": "Make sure no one gets left out under stress."
            }
        },
        {
            "id": 10,
            "question": "What's your ideal relationship with AI at work?",
            "answers": {
                "A": "Collaborator—side by side, learning and growing.",
                "B": "Consultant—advice only, with final say by people.",
                "C": "Support—only as needed, never front and center.",
                "D": "Watchdog—monitor, question, and keep it in check.",
                "E": "Minimal—keep AI out of the core.",
                "F": "Accelerator—push the boundaries and redefine work.",
                "G": "Equalizer—help level the playing field for all."
            }
        }
    ],
    "archetypes": {
        "A": {
            "name": "The Pioneer",
            "description": "Eager adopter who sees AI as adventure and advantage.",
            "characteristics": [
                "First to test new AI tools",
                "Vocal about AI wins and successes",
                "Energized by possibilities",
                "Natural experimenter"
            ],
            "approach": "Give them early access to AI tools and spotlight their successes to encourage others.",
            "icon": "🚀",
            "podcast_insight": "Pioneers are your early adopters - they'll drive AI momentum in organizations."
        },
        "B": {
            "name": "The Analyst",
            "description": "Wants evidence, ROI, and a plan before acting.",
            "characteristics": [
                "Asks for data and KPIs",
                "Cautious about adoption",
                "Values proven results",
                "Methodical decision-maker"
            ],
            "approach": "Provide clear data, success metrics, and run structured pilots to demonstrate value.",
            "icon": "📊",
            "podcast_insight": "Analysts need concrete evidence - focus on ROI and measurable outcomes."
        },
        "C": {
            "name": "The Worrier",
            "description": "Feels threatened or uncertain about AI's impact on their role.",
            "characteristics": [
                "Quiet and anxious about change",
                "Asks about job security",
                "Prefers familiar processes",
                "Needs reassurance"
            ],
            "approach": "Offer reassurance, clear upskilling paths, and emotional support throughout the transition.",
            "icon": "😰",
            "podcast_insight": "Worriers need empathy and support - address job security concerns directly."
        },
        "D": {
            "name": "The Guardian",
            "description": "Prioritizes caution, ethics, and minimizing risk or harm.",
            "characteristics": [
                "Raises ethical concerns",
                "Checks for compliance",
                "Values safety protocols",
                "Thoughtful about implications"
            ],
            "approach": "Involve them in risk assessment, policy development, and ethical guideline creation.",
            "icon": "🛡️",
            "podcast_insight": "Guardians ensure responsible AI - include them in governance discussions."
        },
        "E": {
            "name": "The Traditionalist",
            "description": "Prefers the old way—sees AI as unnecessary or overhyped.",
            "characteristics": [
                "Dismisses new tools",
                "Values established methods",
                "Skeptical of trends",
                "Prefers consistency"
            ],
            "approach": "Demonstrate AI value through small, relevant wins that directly benefit their work.",
            "icon": "📚",
            "podcast_insight": "Traditionalists need proof of practical value - start with small, clear benefits."
        },
        "F": {
            "name": "The Opportunist",
            "description": "Sees AI as a way to leap ahead, disrupt, or win.",
            "characteristics": [
                "High-energy 'let's go' attitude",
                "Risk-taker and disruptor",
                "Competitive mindset",
                "Innovation-focused"
            ],
            "approach": "Channel their energy toward competitive advantage while managing their risk appetite responsibly.",
            "icon": "⚡",
            "podcast_insight": "Opportunists drive rapid adoption - help them balance speed with responsibility."
        },
        "G": {
            "name": "The Humanitarian",
            "description": "Focuses on equity, fairness, and team wellbeing.",
            "characteristics": [
                "Asks about people impact",
                "Values inclusive culture",
                "Considers team morale",
                "Advocates for fairness"
            ],
            "approach": "Involve them in change management processes and culture-building initiatives.",
            "icon": "🤝",
            "podcast_insight": "Humanitarians ensure AI benefits everyone - engage them in inclusive design."
        }
    }
}

# Helper functions
def get_client_info(request: Request) -> Dict[str, str]:
    """Extract client information from request"""
    return {
        'user_agent': request.headers.get("user-agent", ""),
        'ip_address': request.client.host if request.client else "",
    }

def log_analytics(event_type: str, session_id: str = None, event_data: Dict = None, 
                 ip_address: str = "", user_agent: str = ""):
    """Log analytics event to database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            INSERT INTO analytics (event_type, session_id, event_data, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            event_type,
            session_id,
            json.dumps(event_data) if event_data else None,
            ip_address,
            user_agent
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Analytics logging error: {e}")

def calculate_scores(responses: Dict[str, str]) -> Dict[str, int]:
    """Calculate archetype scores from responses"""
    counts = {}
    for answer in responses.values():
        counts[answer] = counts.get(answer, 0) + 1
    
    total = len(responses)
    percentages = {}
    for letter in 'ABCDEFG':
        count = counts.get(letter, 0)
        percentages[letter] = round((count / total) * 100) if total > 0 else 0
    
    return percentages

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main quiz page with enhanced analytics"""
    
    # Log page view
    client_info = get_client_info(request)
    log_analytics("page_view", event_data={"page": "home"}, **client_info)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Archetype Quiz - Accelerating Humans</title>
        <meta name="description" content="Discover your AI workplace personality with our comprehensive archetype quiz from the Accelerating Humans podcast.">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
                line-height: 1.6;
                color: #2c3e50;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            
            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .quiz-card {{
                background: white;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
                padding: 40px;
                width: 100%;
                max-width: 700px;
                animation: slideIn 0.4s ease-out;
            }}
            
            @keyframes slideIn {{
                from {{
                    opacity: 0;
                    transform: translateY(20px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            h1 {{
                font-size: 2.5rem;
                font-weight: 700;
                text-align: center;
                margin-bottom: 1rem;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .subtitle {{
                text-align: center;
                font-size: 1.2rem;
                color: #5a6c7d;
                margin-bottom: 2rem;
            }}
            
            .badge {{
                display: inline-block;
                background: #f0f3ff;
                color: #667eea;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 500;
                margin-bottom: 2rem;
            }}
            
            .progress-container {{
                margin-bottom: 2rem;
            }}
            
            .progress-text {{
                text-align: center;
                margin-bottom: 8px;
                font-weight: 600;
                color: #667eea;
            }}
            
            .progress-bar {{
                width: 100%;
                height: 8px;
                background: #e9ecef;
                border-radius: 4px;
                overflow: hidden;
            }}
            
            .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                border-radius: 4px;
                transition: width 0.3s ease;
                width: 0%;
            }}
            
            .question {{
                margin-bottom: 2rem;
            }}
            
            .question-text {{
                font-size: 1.3rem;
                font-weight: 600;
                margin-bottom: 2rem;
                text-align: center;
                line-height: 1.5;
            }}
            
            .option {{
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: flex-start;
                gap: 1rem;
            }}
            
            .option:hover {{
                border-color: #667eea;
                background: #f0f3ff;
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
            }}
            
            .option.selected {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-color: #667eea;
                color: white;
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            }}
            
            .option-letter {{
                font-weight: 700;
                font-size: 1.1rem;
                min-width: 24px;
                height: 24px;
                background: #667eea;
                color: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }}
            
            .option.selected .option-letter {{
                background: white;
                color: #667eea;
            }}
            
            .btn {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                min-width: 120px;
            }}
            
            .btn:hover:not(:disabled) {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            }}
            
            .btn:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }}
            
            .btn-secondary {{
                background: #6c757d;
            }}
            
            .nav-buttons {{
                display: flex;
                justify-content: space-between;
                gap: 1rem;
                margin-top: 2rem;
            }}
            
            .results {{
                text-align: center;
            }}
            
            .archetype-icon {{
                font-size: 4rem;
                margin-bottom: 1rem;
            }}
            
            .archetype-name {{
                font-size: 2rem;
                margin-bottom: 1rem;
                color: #667eea;
            }}
            
            .characteristics {{
                text-align: left;
                margin: 2rem 0;
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 12px;
            }}
            
            .characteristics ul {{
                list-style: none;
            }}
            
            .characteristics li {{
                padding: 0.5rem 0;
                position: relative;
                padding-left: 2rem;
            }}
            
            .characteristics li:before {{
                content: "✓";
                position: absolute;
                left: 0;
                color: #667eea;
                font-weight: bold;
            }}
            
            .share-link {{
                background: #f0f3ff;
                border: 1px solid #667eea;
                border-radius: 8px;
                padding: 1rem;
                margin: 1rem 0;
                font-family: monospace;
                word-break: break-all;
                font-size: 0.9rem;
            }}
            
            .hidden {{
                display: none;
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    padding: 10px;
                }}
                
                .quiz-card {{
                    padding: 20px;
                }}
                
                h1 {{
                    font-size: 2rem;
                }}
                
                .nav-buttons {{
                    flex-direction: column;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="quiz-card">
                <!-- Welcome Screen -->
                <div id="welcome" class="screen">
                    <h1>AI Archetype Quiz</h1>
                    <p class="subtitle">Discover your approach to AI adoption in the workplace</p>
                    <div style="text-align: center;">
                        <span class="badge">From the Accelerating Humans Podcast</span>
                    </div>
                    <p style="margin-bottom: 2rem;">This quiz will help you understand your unique AI personality and how you approach artificial intelligence in professional settings.</p>
                    <div style="text-align: center;">
                        <button class="btn" onclick="startQuiz()" style="font-size: 1.1rem; padding: 15px 30px;">Start Your Quiz</button>
                    </div>
                    <div style="text-align: center; margin-top: 2rem;">
                        <a href="/summary" style="color: #667eea; text-decoration: none;">View Summary Statistics</a>
                    </div>
                </div>
                
                <!-- Quiz Screen -->
                <div id="quiz" class="screen hidden">
                    <div class="progress-container">
                        <div class="progress-text" id="progress-text">Question 1 of 10</div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill"></div>
                        </div>
                    </div>
                    
                    <div id="question-container"></div>
                    
                    <div class="nav-buttons">
                        <button class="btn btn-secondary" id="prev-btn" onclick="previousQuestion()" disabled>Previous</button>
                        <button class="btn" id="next-btn" onclick="nextQuestion()" disabled>Next</button>
                    </div>
                </div>
                
                <!-- Results Screen -->
                <div id="results" class="screen hidden">
                    <div class="results">
                        <div class="archetype-icon" id="result-icon"></div>
                        <h2 class="archetype-name" id="result-name"></h2>
                        <p id="result-description" style="font-size: 1.1rem; margin-bottom: 2rem;"></p>
                        
                        <div class="characteristics">
                            <h3 style="margin-bottom: 1rem;">Key Characteristics:</h3>
                            <ul id="result-characteristics"></ul>
                        </div>
                        
                        <div style="background: #f0f3ff; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0;">
                            <h4 style="color: #667eea; margin-bottom: 1rem;">How to work with this archetype:</h4>
                            <p id="result-approach"></p>
                        </div>
                        
                        <div id="share-section" class="hidden">
                            <h4 style="margin-bottom: 1rem;">Share your results:</h4>
                            <div class="share-link" id="share-url"></div>
                        </div>
                        
                        <div class="nav-buttons" style="justify-content: center;">
                            <button class="btn btn-secondary" onclick="restartQuiz()">Take Again</button>
                            <button class="btn" onclick="shareResults()">Get Share Link</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const quizData = {json.dumps(QUIZ_DATA)};
            let currentQuestion = 0;
            let answers = {{}};
            let startTime = null;
            let sessionId = null;
            
            function startQuiz() {{
                currentQuestion = 0;
                answers = {{}};
                startTime = Date.now();
                sessionId = null;
                
                // Log quiz start
                logAnalytics('quiz_started');
                
                showScreen('quiz');
                showQuestion();
            }}
            
            function showScreen(screenId) {{
                document.querySelectorAll('.screen').forEach(screen => {{
                    screen.classList.add('hidden');
                }});
                document.getElementById(screenId).classList.remove('hidden');
            }}
            
            function showQuestion() {{
                const question = quizData.questions[currentQuestion];
                const progress = ((currentQuestion + 1) / quizData.questions.length) * 100;
                
                document.getElementById('progress-fill').style.width = progress + '%';
                document.getElementById('progress-text').textContent = 
                    `Question ${{currentQuestion + 1}} of ${{quizData.questions.length}}`;
                
                let html = `<div class="question">
                    <div class="question-text">${{question.question}}</div>`;
                
                for (const [key, text] of Object.entries(question.answers)) {{
                    const isSelected = answers[question.id] === key ? 'selected' : '';
                    html += `<div class="option ${{isSelected}}" onclick="selectAnswer('${{key}}', this)">
                        <div class="option-letter">${{key}}</div>
                        <div>${{text}}</div>
                    </div>`;
                }}
                
                html += '</div>';
                document.getElementById('question-container').innerHTML = html;
                
                updateNavigation();
            }}
            
            function selectAnswer(answer, element) {{
                answers[quizData.questions[currentQuestion].id] = answer;
                
                document.querySelectorAll('.option').forEach(opt => {{
                    opt.classList.remove('selected');
                }});
                element.classList.add('selected');
                
                // Log answer selection
                logAnalytics('answer_selected', {{
                    question_id: quizData.questions[currentQuestion].id,
                    answer: answer,
                    question_number: currentQuestion + 1
                }});
                
                updateNavigation();
            }}
            
            function updateNavigation() {{
                const prevBtn = document.getElementById('prev-btn');
                const nextBtn = document.getElementById('next-btn');
                const currentQuestionData = quizData.questions[currentQuestion];
                
                prevBtn.disabled = currentQuestion === 0;
                nextBtn.disabled = !answers[currentQuestionData.id];
                
                if (currentQuestion === quizData.questions.length - 1) {{
                    nextBtn.textContent = 'See Results';
                }} else {{
                    nextBtn.textContent = 'Next';
                }}
            }}
            
            function previousQuestion() {{
                if (currentQuestion > 0) {{
                    currentQuestion--;
                    showQuestion();
                }}
            }}
            
            function nextQuestion() {{
                if (currentQuestion < quizData.questions.length - 1) {{
                    currentQuestion++;
                    showQuestion();
                }} else {{
                    submitQuiz();
                }}
            }}
            
            async function submitQuiz() {{
                const completionTime = startTime ? (Date.now() - startTime) / 1000 / 60 : null;
                
                try {{
                    const response = await fetch('/api/submit', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            responses: answers,
                            completion_time: completionTime
                        }})
                    }});
                    
                    if (response.ok) {{
                        const result = await response.json();
                        sessionId = result.session_id;
                        displayResults(result);
                    }} else {{
                        // Fallback to local calculation
                        displayLocalResults();
                    }}
                }} catch (error) {{
                    console.error('Submit error:', error);
                    displayLocalResults();
                }}
            }}
            
            function displayResults(result) {{
                const archetype = result ? quizData.archetypes[result.primary_archetype] : null;
                
                if (archetype) {{
                    document.getElementById('result-icon').textContent = archetype.icon;
                    document.getElementById('result-name').textContent = archetype.name;
                    document.getElementById('result-description').textContent = archetype.description;
                    document.getElementById('result-approach').textContent = archetype.approach;
                    
                    const charList = document.getElementById('result-characteristics');
                    charList.innerHTML = '';
                    archetype.characteristics.forEach(char => {{
                        const li = document.createElement('li');
                        li.textContent = char;
                        charList.appendChild(li);
                    }});
                    
                    // Log completion
                    logAnalytics('quiz_completed', {{
                        archetype: result.primary_archetype,
                        archetype_name: archetype.name,
                        completion_time: result.completion_time
                    }});
                }} else {{
                    displayLocalResults();
                }}
                
                showScreen('results');
            }}
            
            function displayLocalResults() {{
                // Fallback local calculation
                const counts = {{}};
                Object.values(answers).forEach(answer => {{
                    counts[answer] = (counts[answer] || 0) + 1;
                }});
                
                const primaryLetter = Object.keys(counts).reduce((a, b) => 
                    counts[a] > counts[b] ? a : b);
                const archetype = quizData.archetypes[primaryLetter];
                
                document.getElementById('result-icon').textContent = archetype.icon;
                document.getElementById('result-name').textContent = archetype.name;
                document.getElementById('result-description').textContent = archetype.description;
                document.getElementById('result-approach').textContent = archetype.approach;
                
                const charList = document.getElementById('result-characteristics');
                charList.innerHTML = '';
                archetype.characteristics.forEach(char => {{
                    const li = document.createElement('li');
                    li.textContent = char;
                    charList.appendChild(li);
                }});
                
                showScreen('results');
            }}
            
            function shareResults() {{
                if (sessionId) {{
                    const shareUrl = `${{window.location.origin}}/results/${{sessionId}}`;
                    document.getElementById('share-url').textContent = shareUrl;
                    document.getElementById('share-section').classList.remove('hidden');
                    
                    // Copy to clipboard
                    navigator.clipboard.writeText(shareUrl).then(() => {{
                        alert('Share link copied to clipboard!');
                    }});
                    
                    logAnalytics('result_shared', {{ session_id: sessionId }});
                }} else {{
                    alert('Please retake the quiz to get a shareable link.');
                }}
            }}
            
            function restartQuiz() {{
                showScreen('welcome');
            }}
            
            async function logAnalytics(eventType, data = {{}}) {{
                try {{
                    await fetch('/api/analytics', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            event_type: eventType,
                            session_id: sessionId,
                            data: data
                        }})
                    }});
                }} catch (error) {{
                    console.warn('Analytics error:', error);
                }}
            }}
        </script>
    </body>
    </html>
    """)

@app.post("/api/submit")
async def submit_quiz(request: Request, submission: QuizSubmission):
    """Submit quiz and save results"""
    try:
        # Calculate scores
        scores = calculate_scores(submission.responses)
        primary_letter = max(scores, key=scores.get)
        archetype = QUIZ_DATA["archetypes"][primary_letter]
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Get client info
        client_info = get_client_info(request)
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            INSERT INTO results 
            (session_id, primary_archetype, archetype_name, all_scores, responses, 
             completion_time, user_agent, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            primary_letter,
            archetype["name"],
            json.dumps(scores),
            json.dumps(submission.responses),
            submission.completion_time,
            client_info["user_agent"],
            client_info["ip_address"]
        ))
        conn.commit()
        conn.close()
        
        # Log analytics
        log_analytics("quiz_submitted", session_id, {
            "archetype": primary_letter,
            "archetype_name": archetype["name"],
            "completion_time": submission.completion_time
        }, **client_info)
        
        return {
            "session_id": session_id,
            "primary_archetype": primary_letter,
            "archetype_name": archetype["name"],
            "scores": scores,
            "completion_time": submission.completion_time
        }
        
    except Exception as e:
        print(f"Submit error: {e}")
        raise HTTPException(status_code=500, detail="Error processing quiz")

@app.post("/api/analytics")
async def log_analytics_event(request: Request, event: AnalyticsEvent):
    """Log analytics event"""
    try:
        client_info = get_client_info(request)
        log_analytics(event.event_type, event.session_id, event.data, **client_info)
        return {"status": "logged"}
    except Exception as e:
        print(f"Analytics error: {e}")
        return {"status": "error"}

@app.get("/results/{{session_id}}", response_class=HTMLResponse)
async def get_results(session_id: str):
    """Display shared results page"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute('''
            SELECT primary_archetype, archetype_name, all_scores, completed_at, completion_time
            FROM results WHERE session_id = ?
        ''', (session_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Results not found")
        
        primary_letter, archetype_name, scores_json, completed_at, completion_time = result
        scores = json.loads(scores_json)
        archetype = QUIZ_DATA["archetypes"][primary_letter]
        
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{archetype_name}} - AI Archetype Results</title>
            <meta name="description" content="{{archetype['description']}}">
            <meta property="og:title" content="My AI Archetype: {{archetype_name}}">
            <meta property="og:description" content="{{archetype['description']}} Take the AI Archetype Quiz!">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }}
                .result-card {{
                    background: white;
                    border-radius: 16px;
                    padding: 40px;
                    max-width: 600px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
                    text-align: center;
                }}
                .archetype-icon {{
                    font-size: 4rem;
                    margin-bottom: 1rem;
                }}
                .archetype-name {{
                    font-size: 2.5rem;
                    color: #667eea;
                    margin-bottom: 1rem;
                }}
                .characteristics {{
                    text-align: left;
                    background: #f8f9fa;
                    padding: 1.5rem;
                    border-radius: 12px;
                    margin: 2rem 0;
                }}
                .characteristics ul {{
                    list-style: none;
                    margin: 0;
                    padding: 0;
                }}
                .characteristics li {{
                    padding: 0.5rem 0;
                    position: relative;
                    padding-left: 2rem;
                }}
                .characteristics li:before {{
                    content: "✓";
                    position: absolute;
                    left: 0;
                    color: #667eea;
                    font-weight: bold;
                }}
                .btn {{
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 600;
                    text-decoration: none;
                    display: inline-block;
                    margin: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="result-card">
                <div class="archetype-icon">{{archetype['icon']}}</div>
                <h1 class="archetype-name">{{archetype_name}}</h1>
                <p style="font-size: 1.1rem; margin-bottom: 2rem;">{{archetype['description']}}</p>
                
                <div class="characteristics">
                    <h3>Key Characteristics:</h3>
                    <ul>
                        {" ".join(f"<li>{char}</li>" for char in archetype['characteristics'])}
                    </ul>
                </div>
                
                <div style="background: #f0f3ff; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0;">
                    <h4 style="color: #667eea; margin-bottom: 1rem;">How to work with this archetype:</h4>
                    <p>{{archetype['approach']}}</p>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 2rem; margin-top: 2rem;">
                    <p style="color: #666; margin-bottom: 1rem;">From the Accelerating Humans Podcast</p>
                    <a href="/" class="btn">Take the Quiz Yourself</a>
                </div>
            </div>
        </body>
        </html>
        """)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Results page error: {e}")
        raise HTTPException(status_code=500, detail="Server error")

@app.get("/summary", response_class=HTMLResponse)
async def summary_page():
    """Public summary with analytics for podcast insights"""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Get archetype distribution
        cursor = conn.execute('''
            SELECT primary_archetype, archetype_name, COUNT(*) as count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM results), 1) as percentage
            FROM results 
            GROUP BY primary_archetype, archetype_name
            ORDER BY count DESC
        ''')
        distribution = cursor.fetchall()
        
        # Get total submissions
        cursor = conn.execute('SELECT COUNT(*) FROM results')
        total = cursor.fetchone()[0]
        
        # Get recent activity (last 7 days)
        cursor = conn.execute('''
            SELECT COUNT(*) FROM results 
            WHERE completed_at > datetime('now', '-7 days')
        ''')
        recent = cursor.fetchone()[0]
        
        # Get average completion time
        cursor = conn.execute('''
            SELECT AVG(completion_time) FROM results 
            WHERE completion_time IS NOT NULL
        ''')
        avg_time = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Create distribution chart data
        chart_data = []
        for archetype_letter, archetype_name, count, percentage in distribution:
            archetype = QUIZ_DATA["archetypes"][archetype_letter]
            chart_data.append({
                "name": archetype_name,
                "icon": archetype["icon"],
                "count": count,
                "percentage": percentage,
                "insight": archetype.get("podcast_insight", "")
            })
        
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Archetype Quiz - Summary Statistics</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                }}
                .summary-card {{
                    background: white;
                    border-radius: 16px;
                    padding: 40px;
                    margin-bottom: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                }}
                .stat-number {{
                    font-size: 2rem;
                    font-weight: bold;
                    color: #667eea;
                }}
                .archetype-item {{
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    padding: 15px;
                    border-bottom: 1px solid #eee;
                }}
                .archetype-icon {{
                    font-size: 2rem;
                }}
                .archetype-info {{
                    flex: 1;
                }}
                .archetype-bar {{
                    width: 200px;
                    height: 20px;
                    background: #e9ecef;
                    border-radius: 10px;
                    overflow: hidden;
                }}
                .archetype-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #667eea, #764ba2);
                    border-radius: 10px;
                }}
                .podcast-insight {{
                    font-size: 0.9rem;
                    color: #666;
                    font-style: italic;
                    margin-top: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="summary-card">
                    <h1 style="text-align: center; color: #667eea; margin-bottom: 2rem;">
                        AI Archetype Quiz Summary
                    </h1>
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{total}</div>
                            <div>Total Responses</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{recent}</div>
                            <div>This Week</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{avg_time:.1f}</div>
                            <div>Avg. Minutes</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">7</div>
                            <div>Archetypes</div>
                        </div>
                    </div>
                    
                    <h2 style="margin-bottom: 1rem;">Archetype Distribution</h2>
                    <div style="margin-bottom: 2rem;">
                        {"".join(f'''
                        <div class="archetype-item">
                            <div class="archetype-icon">{item["icon"]}</div>
                            <div class="archetype-info">
                                <div style="font-weight: 600;">{item["name"]}</div>
                                <div class="podcast-insight">{item["insight"]}</div>
                            </div>
                            <div style="text-align: right; margin-right: 15px;">
                                <div style="font-weight: 600;">{item["percentage"]}%</div>
                                <div style="font-size: 0.9rem; color: #666;">({item["count"]} responses)</div>
                            </div>
                            <div class="archetype-bar">
                                <div class="archetype-fill" style="width: {item["percentage"]}%;"></div>
                            </div>
                        </div>
                        ''' for item in chart_data)}
                    </div>
                    
                    <div style="text-align: center; border-top: 1px solid #eee; padding-top: 2rem;">
                        <p style="color: #666;">From the Accelerating Humans Podcast</p>
                        <a href="/" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">Take the Quiz</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """)
        
    except Exception as e:
        print(f"Summary page error: {e}")
        raise HTTPException(status_code=500, detail="Server error")

@app.get("/api/stats")
async def get_stats():
    """API endpoint for podcast analytics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Comprehensive stats for podcast insights
        cursor = conn.execute('''
            SELECT primary_archetype, archetype_name, COUNT(*) as count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM results), 1) as percentage
            FROM results 
            GROUP BY primary_archetype, archetype_name
            ORDER BY count DESC
        ''')
        distribution = [
            {
                "archetype": row[0],
                "name": row[1], 
                "count": row[2],
                "percentage": row[3],
                "insight": QUIZ_DATA["archetypes"][row[0]].get("podcast_insight", "")
            }
            for row in cursor.fetchall()
        ]
        
        # Total submissions
        cursor = conn.execute('SELECT COUNT(*) FROM results')
        total = cursor.fetchone()[0]
        
        # Daily submissions (last 30 days)
        cursor = conn.execute('''
            SELECT DATE(completed_at) as date, COUNT(*) as count
            FROM results 
            WHERE completed_at > datetime('now', '-30 days')
            GROUP BY DATE(completed_at)
            ORDER BY date
        ''')
        daily_stats = dict(cursor.fetchall())
        
        # Top events from analytics
        cursor = conn.execute('''
            SELECT event_type, COUNT(*) as count
            FROM analytics 
            WHERE created_at > datetime('now', '-7 days')
            GROUP BY event_type
            ORDER BY count DESC
        ''')
        events = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_submissions": total,
            "archetype_distribution": distribution,
            "daily_submissions": daily_stats,
            "recent_events": events,
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Stats API error: {e}")
        return {"error": "Stats unavailable"}

@app.get("/health")
async def health():
    """Health check with database status"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute('SELECT COUNT(*) FROM results')
        total_results = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "questions": len(QUIZ_DATA["questions"]),
            "total_results": total_results,
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)