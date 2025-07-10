"""
AI Archetype Quiz with Professional Scoring System
Enhanced 10-Question Strategic Version
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
from typing import Dict, Optional, Union, List, Any

app = FastAPI(title="AI Archetype Quiz")

# Database setup
DB_PATH = Path("data/quiz.db")
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    """Initialize database with analytics and results tables"""
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Results table - base schema first
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
        
        # Check if role_demographic column exists, if not add it
        cursor = conn.execute("PRAGMA table_info(results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'role_demographic' not in columns:
            print("Adding role_demographic column...")
            conn.execute('ALTER TABLE results ADD COLUMN role_demographic TEXT')
        
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
        
        # Create indexes - now safe to create the role index since column exists
        conn.execute('CREATE INDEX IF NOT EXISTS idx_results_archetype ON results(primary_archetype)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_results_completed ON results(completed_at)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_results_role ON results(role_demographic)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_analytics_event ON analytics(event_type)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_analytics_created ON analytics(created_at)')
        
        conn.commit()
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

# Initialize database
init_db()

# Pydantic models
class QuizSubmission(BaseModel):
    responses: Dict[str, Any]  # Support both single strings and multi-choice objects
    completion_time: Optional[float] = None

class AnalyticsEvent(BaseModel):
    event_type: str
    session_id: Optional[str] = None
    data: Optional[Dict] = None

# Enhanced Quiz Data - Professional Scoring System
QUIZ_DATA = {
    "version": "3.0-professional",
    "total_questions": 10,
    "estimated_completion_minutes": 5,
    "questions": [
        {
            "id": 1,
            "question": "What's your primary role when it comes to AI decisions in your organization?",
            "type": "demographic",
            "answers": {
                "A": "Individual contributor - I use tools but don't choose them",
                "B": "Team leader - I guide implementation for my team", 
                "C": "Executive - I set strategy and allocate resources",
                "D": "Researcher/Academic - I study and evaluate these technologies",
                "E": "Advisor/Consultant - I help others make informed decisions",
                "F": "Concerned observer - I'm affected but have little formal influence"
            },
            "scoring": {
                # Demographic question - no archetype scoring
            }
        },
        {
            "id": 2,
            "question": "Over the next 2-3 years, AI will most likely...",
            "answers": {
                "A": "Create more valuable work by automating routine tasks",
                "B": "Significantly reduce jobs in knowledge work professions",
                "C": "Enhance existing roles more than replace them",
                "D": "Create economic disruption before long-term benefits emerge",
                "E": "Concentrate power while displacing human expertise",
                "F": "Too uncertain to predict with confidence"
            },
            "scoring": {
                "A": "Innovator",
                "B": "Guardian", 
                "C": "Pragmatist",
                "D": "Guardian",
                "E": "Egalitarian",
                "F": "Scholar"
            }
        },
        {
            "id": 3,
            "question": "When your organization faces new AI opportunities, what's your first instinct?",
            "answers": {
                "A": "Research the evidence and validate the claims",
                "B": "Assess competitive implications and strategic value",
                "C": "Consider the human impact and job implications",
                "D": "Evaluate practical implementation challenges",
                "E": "Examine security risks and compliance requirements",
                "F": "Look for ways to ensure equitable access and benefits",
                "G": "Explore breakthrough potential and innovation opportunities"
            },
            "scoring": {
                "A": "Scholar",
                "B": "Strategist",
                "C": "Humanist",
                "D": "Pragmatist",
                "E": "Guardian",
                "F": "Egalitarian",
                "G": "Innovator"
            }
        },
        {
            "id": 4,
            "question": "What concerns you most about AI implementation in professional settings?",
            "answers": {
                "A": "Loss of human skills and over-dependence on automation",
                "B": "Security vulnerabilities and governance failures",
                "C": "Widening gaps between AI-enabled and traditional workers",
                "D": "Rushing adoption without rigorous validation",
                "E": "Missing competitive opportunities while others advance",
                "F": "Tools that create more problems than they solve",
                "G": "Believing inflated promises instead of realistic expectations"
            },
            "scoring": {
                "A": "Humanist",
                "B": "Guardian",
                "C": "Egalitarian",
                "D": "Scholar",
                "E": "Strategist",
                "F": "Pragmatist",
                "G": "Scholar"
            }
        },
        {
            "id": 5,
            "question": "If you could have an AI 'expert advisor' available 24/7, what would be most valuable?",
            "answers": {
                "A": "Research assistance and evidence-based insights",
                "B": "Strategic analysis and competitive intelligence", 
                "C": "Learning support and skill development guidance",
                "D": "Creative collaboration and idea development",
                "E": "Practical problem-solving for daily challenges",
                "F": "Ensuring decisions consider human impact and ethics",
                "G": "Making expert knowledge accessible to everyone"
            },
            "scoring": {
                "A": "Scholar",
                "B": "Strategist",
                "C": "Humanist",
                "D": "Innovator",
                "E": "Pragmatist",
                "F": "Humanist",
                "G": "Egalitarian"
            }
        },
        {
            "id": 6,
            "question": "What would make you confident in an AI implementation?",
            "answers": {
                "A": "Transparent processes and robust safety measures",
                "B": "Peer-reviewed research and systematic validation",
                "C": "Clear evidence it enhances rather than replaces human work",
                "D": "Demonstrated competitive advantages and ROI",
                "E": "Equitable access and inclusive design principles",
                "F": "Reliable performance in real-world conditions",
                "G": "Breakthrough capabilities that open new possibilities"
            },
            "scoring": {
                "A": "Guardian",
                "B": "Scholar",
                "C": "Humanist",
                "D": "Strategist",
                "E": "Egalitarian",
                "F": "Pragmatist",
                "G": "Innovator"
            }
        },
        {
            "id": 7,
            "question": "How would you approach leading others through AI adoption?",
            "answers": {
                "A": "Start small, learn from experience, scale what works",
                "B": "Invest heavily in training and skill development",
                "C": "Establish clear governance and ethical guidelines first",
                "D": "Focus on tools that amplify human capabilities",
                "E": "Ensure benefits and opportunities reach everyone",
                "F": "Move decisively to capture competitive advantages",
                "G": "Pursue transformative applications that create new value"
            },
            "scoring": {
                "A": "Pragmatist",
                "B": "Humanist",
                "C": "Guardian",
                "D": "Humanist",
                "E": "Egalitarian",
                "F": "Strategist",
                "G": "Innovator"
            }
        },
        {
            "id": 8,
            "question": "When evaluating AI solutions, what do you prioritize first?",
            "answers": {
                "A": "Evidence base and methodological rigor",
                "B": "Security, privacy, and compliance features",
                "C": "Impact on employee experience and job satisfaction",
                "D": "Business case and strategic alignment",
                "E": "Accessibility across different skill levels",
                "F": "Practical integration with existing workflows",
                "G": "Innovation potential and competitive differentiation"
            },
            "scoring": {
                "A": "Scholar",
                "B": "Guardian",
                "C": "Humanist",
                "D": "Strategist",
                "E": "Egalitarian",
                "F": "Pragmatist",
                "G": "Innovator"
            }
        },
        {
            "id": 9,
            "question": "When you encounter AI skepticism or resistance, what's your approach?",
            "answers": {
                "A": "Share research and evidence to address specific concerns",
                "B": "Acknowledge concerns and collaborate on solutions",
                "C": "Demonstrate practical benefits through small experiments",
                "D": "Emphasize human values and ethical safeguards",
                "E": "Show how AI can increase rather than decrease opportunities",
                "F": "Focus on competitive necessity and strategic advantages",
                "G": "Respect their caution - skepticism prevents costly mistakes"
            },
            "scoring": {
                "A": "Scholar",
                "B": "Humanist",
                "C": "Pragmatist",
                "D": "Humanist",
                "E": "Egalitarian",
                "F": "Strategist",
                "G": "Scholar"
            }
        },
        {
            "id": 10,
            "question": "What's your biggest hope for AI's impact on work and society?",
            "answers": {
                "A": "Liberating humans from tedious work to focus on meaningful challenges",
                "B": "Breaking down barriers so talent can flourish regardless of background",
                "C": "Accelerating scientific progress to solve humanity's biggest problems",
                "D": "Creating sustainable competitive advantages and economic growth",
                "E": "Enabling personalized learning and continuous skill development",
                "F": "Making complex problems manageable with better tools",
                "G": "Opening entirely new frontiers of innovation and possibility"
            },
            "scoring": {
                "A": "Humanist",
                "B": "Egalitarian",
                "C": "Scholar",
                "D": "Strategist",
                "E": "Humanist",
                "F": "Pragmatist",
                "G": "Innovator"
            }
        }
    ],
    "archetypes": {
        "Scholar": {
            "name": "The Scholar",
            "description": "Sees AI as a frontier for scientific inquiry and intellectual rigor. Values research, empirical evidence, and robust theoretical frameworks.",
            "characteristics": [
                "Grounds decisions in evidence and analysis",
                "Keeps hype in check with data and systematic study",
                "Fosters continuous learning and improvement",
                "Values peer-reviewed research and validation"
            ],
            "approach": "Engage in pilot design, assessment, and lessons-learned reviews. Leverage their expertise to set up meaningful metrics and success criteria.",
            "change_response": "May delay action while seeking more data. Can struggle with ambiguity or practical constraints.",
            "risks": "Analysis paralysis - seeking perfect data before moving forward.",
            "icon": "📚",
            "color": "#4ECDC4"
        },
        "Strategist": {
            "name": "The Strategist", 
            "description": "Approaches AI through the lens of competitive advantage, business value, and organizational transformation. Focused on aligning AI initiatives with mission, ROI, and market realities.",
            "characteristics": [
                "Drives alignment between AI and business outcomes",
                "Secures resources and executive sponsorship", 
                "Keeps efforts goal-oriented",
                "Focuses on competitive advantage and ROI"
            ],
            "approach": "Involve in roadmap and business case development. Pair with values-driven archetypes to ensure plans are both profitable and principled.",
            "change_response": "May prioritize value over values. Can move too fast for adequate stakeholder buy-in.",
            "risks": "May overlook ethical considerations for business gains; could rush implementation.",
            "icon": "📈",
            "color": "#FF6B35"
        },
        "Humanist": {
            "name": "The Humanist",
            "description": "Centers human wellbeing, agency, and dignity. Sees AI as a tool for human flourishing, not a replacement for human value.",
            "characteristics": [
                "Ensures AI enhances rather than erodes humanity",
                "Champions user experience and emotional impacts",
                "Raises questions about autonomy and meaning of work",
                "Advocates for human-centered design"
            ],
            "approach": "Invite into user research, change management, and communication planning. Recognize their advocacy for meaning and wellbeing.",
            "change_response": "May resist efficiency if it feels dehumanizing. Could overlook technical or business constraints.",
            "risks": "May slow adoption focused on human impact; could resist beneficial automation.",
            "icon": "🤝",
            "color": "#95E1D3"
        },
        "Pragmatist": {
            "name": "The Pragmatist",
            "description": "Values practicality, incremental progress, and evidence-based action. Focused on what works 'on the ground,' not just in theory or vision.",
            "characteristics": [
                "Bridges vision and execution",
                "Surfaces operational risks early",
                "Supports sustainable, manageable rollout",
                "Focuses on practical implementation"
            ],
            "approach": "Make part of implementation, feedback, and continuous improvement cycles. Empower them to surface blockers early.",
            "change_response": "May overlook breakthrough potential in favor of short-term feasibility. Sometimes seen as cautious.",
            "risks": "May miss transformative opportunities by focusing too heavily on incremental improvements.",
            "icon": "🔧",
            "color": "#A8E6CF"
        },
        "Guardian": {
            "name": "The Guardian",
            "description": "Focuses on risk management, safety, security, and governance. Prioritizes regulation, compliance, and robust oversight to prevent harm.",
            "characteristics": [
                "Prevents costly mistakes or scandals",
                "Enforces standards and accountability",
                "Brings holistic view of risk and privacy",
                "Advocates for robust oversight"
            ],
            "approach": "Involve from the start in risk assessment and policy creation. Give them real decision rights in solution-finding.",
            "change_response": "May slow down or block beneficial innovation. Can be perceived as overly rigid.",
            "risks": "Could create overly restrictive policies that hinder beneficial innovation.",
            "icon": "🛡️",
            "color": "#B4A7D6"
        },
        "Egalitarian": {
            "name": "The Egalitarian",
            "description": "Prioritizes fairness, equity, and justice in all aspects of AI. Focused on ensuring access, preventing bias, and protecting the vulnerable.",
            "characteristics": [
                "Brings voice of inclusion and social impact",
                "Highlights bias and advocates for equity",
                "Ensures systems don't amplify inequalities",
                "Focuses on fair benefit sharing"
            ],
            "approach": "Invite to review design, hiring, and deployment plans for inclusion. Use their insights to address bias or access barriers.",
            "change_response": "May see business tradeoffs as insufficiently just. Risk of focusing on edge cases over general progress.",
            "risks": "Could slow deployment over inclusion concerns; may focus on edge cases at expense of broader progress.",
            "icon": "⚖️",
            "color": "#FFE66D"
        },
        "Innovator": {
            "name": "The Innovator",
            "description": "Sees AI as an adventure and a lever for transformative change. Motivated by curiosity, creativity, and the drive to be first.",
            "characteristics": [
                "Sparks momentum and excitement",
                "Rapidly discovers new use cases",
                "Inspires others through visible action",
                "Willing to take risks and experiment"
            ],
            "approach": "Encourage experiments and create space for safe piloting. Pair with operational partners to scale impact.",
            "change_response": "Can overlook implementation realities. May unintentionally leave others behind.",
            "risks": "May move too fast without proper consideration; could overlook practical constraints.",
            "icon": "🚀",
            "color": "#FF8B94"
        },
        "Steward": {
            "name": "The Steward",
            "description": "Guided by environmental and resource stewardship. Focused on ensuring AI is sustainable and ecologically responsible.",
            "characteristics": [
                "Advocates for 'AI for Good' and long-term thinking",
                "Raises questions about energy use and waste",
                "Focuses on ecological impact and sustainability",
                "Champions resource-conscious solutions"
            ],
            "approach": "Include early in decision-making. Let them help shape sustainable policies and evaluate environmental tradeoffs.",
            "change_response": "May be perceived as slowing progress if sustainability isn't prioritized by others.",
            "risks": "May slow adoption over environmental concerns; could limit growth-focused applications.",
            "icon": "🌱",
            "color": "#90EE90"
        },
        "Learner": {
            "name": "The Learner/Educator",
            "description": "Driven by curiosity, upskilling, and the desire to build AI literacy. Acts as a bridge between developers, decision-makers, and end-users.",
            "characteristics": [
                "Helps organizations adapt and stay resilient",
                "Builds trust through transparent communication",
                "Champions realistic self-assessment",
                "Focuses on building AI literacy"
            ],
            "approach": "Engage in onboarding, internal communications, and change management. Recognize efforts to build AI-ready organization.",
            "change_response": "May become frustrated if others resist learning or if upskilling isn't prioritized.",
            "risks": "May focus too heavily on training at expense of immediate implementation needs.",
            "icon": "🎓",
            "color": "#87CEEB"
        },
        "Integrator": {
            "name": "The Integrator/Facilitator",
            "description": "Ensures AI moves from pilot to real-world use. Focuses on implementation, monitoring, and continuous improvement.",
            "characteristics": [
                "Makes change real through integration",
                "Sets up safety nets and feedback loops",
                "Guides ongoing user education",
                "Bridges strategy and operations"
            ],
            "approach": "Empower with authority and cross-functional access. Invite into both planning and rollout phases.",
            "change_response": "May be seen as bureaucratic. Can become bottlenecks if not properly empowered.",
            "risks": "Could slow processes if not given proper authority; may focus too much on process over outcomes.",
            "icon": "🔗",
            "color": "#DDA0DD"
        },
        "Skeptic": {
            "name": "The Skeptic/Resistor",
            "description": "Approaches AI with critical lens, motivated by self-preservation, skepticism, or deep questions about value and risk.",
            "characteristics": [
                "Identifies blind spots in hype and groupthink",
                "Protects team from unintended consequences",
                "Surfaces real risks and concerns",
                "Provides essential critical perspective"
            ],
            "approach": "Acknowledge legitimacy of skepticism. Invite into structured evaluation and provide clear, transparent answers.",
            "change_response": "May default to resistance or disengage entirely. Can discourage experimentation if not engaged thoughtfully.",
            "risks": "Could block beneficial innovations; may discourage necessary experimentation and learning.",
            "icon": "🤔",
            "color": "#F0E68C"
        }
    },
    # Role demographic mapping (Q1 only)
    "role_mapping": {
        "A": "individual_contributor", 
        "B": "team_leader", 
        "C": "executive", 
        "D": "academic", 
        "E": "advisor", 
        "F": "observer"
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

def calculate_scores(responses: Dict[str, Any]) -> tuple:
    """Calculate archetype scores from responses using professional scoring system"""
    scores = {}
    role_demographic = None
    
    for question_id, answer_data in responses.items():
        question_num = int(question_id)
        
        # Find the question in our data
        question = next((q for q in QUIZ_DATA["questions"] if q["id"] == question_num), None)
        if not question:
            continue
            
        # Handle demographic question (Q1) separately
        if question_num == 1:
            if isinstance(answer_data, dict) and 'primary' in answer_data:
                role_demographic = QUIZ_DATA["role_mapping"].get(answer_data['primary'], "unknown")
            elif isinstance(answer_data, str):
                role_demographic = QUIZ_DATA["role_mapping"].get(answer_data, "unknown")
            continue
        
        # Skip if no scoring defined for this question
        if "scoring" not in question or not question["scoring"]:
            continue
            
        # Process scoring based on answer format
        if isinstance(answer_data, dict):
            # Multi-choice format with primary and secondary choices
            primary = answer_data.get('primary')
            secondary = answer_data.get('secondary', [])
            
            # Primary choice gets 3 points
            if primary and primary in question["scoring"]:
                archetype_name = question["scoring"][primary]
                scores[archetype_name] = scores.get(archetype_name, 0) + 3
            
            # Secondary choices get 1 point each
            if isinstance(secondary, list):
                for choice in secondary:
                    if choice in question["scoring"]:
                        archetype_name = question["scoring"][choice]
                        scores[archetype_name] = scores.get(archetype_name, 0) + 1
        else:
            # Single choice format
            if answer_data in question["scoring"]:
                archetype_name = question["scoring"][answer_data]
                scores[archetype_name] = scores.get(archetype_name, 0) + 3  # Treat as primary
    
    return scores, role_demographic

def determine_primary_and_secondary(scores: Dict[str, int]) -> tuple:
    """Determine primary and secondary archetypes from scores"""
    if not scores:
        return "Pragmatist", None  # Default to Pragmatist
    
    # Sort by score (highest first)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    primary = sorted_scores[0][0]
    secondary = None
    
    # Determine secondary if it's significant (within 3 points and at least 4 points total)
    if len(sorted_scores) > 1:
        primary_score = sorted_scores[0][1]
        second_score = sorted_scores[1][1]
        
        if second_score >= 4 and (primary_score - second_score) <= 3:
            secondary = sorted_scores[1][0]
    
    return primary, secondary

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
        <meta name="description" content="Discover your AI workplace personality with our comprehensive 10-question archetype quiz from the Accelerating Humans podcast.">
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
                position: relative;
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
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
                margin: 2rem 0;
            }}
            
            .info-item {{
                text-align: center;
                padding: 1rem;
                background: #f8f9fa;
                border-radius: 8px;
            }}
            
            .info-item strong {{
                display: block;
                color: #667eea;
                font-size: 1.2rem;
                margin-bottom: 0.5rem;
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
                
                .info-grid {{
                    grid-template-columns: repeat(2, 1fr);
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
                    <p class="subtitle">Navigate the AI transformation with clarity and confidence</p>
                    <div style="text-align: center;">
                        <span class="badge">From the Accelerating Humans Podcast</span>
                    </div>
                    <p style="margin-bottom: 2rem; font-size: 1.1rem; line-height: 1.6;">We're living through a paradigm shift. AI is reshaping how we work, but the biggest challenge isn't technological—it's human. Understanding your AI archetype helps you navigate this transformation with purpose, reduce conflict with colleagues, and make decisions that align with your values.</p>
                    
                    <div class="intro-section">
                        <h2 style="color: #667eea; margin-bottom: 1.5rem;">Why AI Archetypes Matter</h2>
                        <p style="margin-bottom: 1.5rem;">People respond to AI according to deep-seated values, motivations, and practical needs. Some see adventure and opportunity. Others see risk and disruption. Most see a complex mix of both.</p>
                        <p style="margin-bottom: 2rem;">Your archetype reveals your natural approach to AI adoption—and more importantly, how to work effectively with people who see things differently. In times of rapid change, this understanding becomes essential for both individual success and organizational harmony.</p>
                        
                        <div class="benefits-grid">
                            <div class="benefit-item">
                                <div class="benefit-icon">🧭</div>
                                <h3>Navigate Change</h3>
                                <p>Understand your instinctive response to AI and make decisions that align with your values</p>
                            </div>
                            <div class="benefit-item">
                                <div class="benefit-icon">🤝</div>
                                <h3>Bridge Differences</h3>
                                <p>Collaborate more effectively with colleagues who have different AI perspectives</p>
                            </div>
                            <div class="benefit-item">
                                <div class="benefit-icon">🎯</div>
                                <h3>Lead with Insight</h3>
                                <p>Anticipate resistance, build better teams, and guide successful AI implementations</p>
                            </div>
                        </div>
                        
                        <div style="background: #f0f3ff; padding: 1.5rem; border-radius: 12px; margin: 2rem 0; border-left: 4px solid #667eea;">
                            <p style="margin: 0; font-style: italic; color: #333;">
                                <strong>Research-Based:</strong> This framework draws from leading research in technology adoption (Rogers, UTAUT), behavioral science, and digital transformation literature. It's designed as both a diagnostic tool for self-understanding and a practical guide for better collaboration.
                            </p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 2rem;">
                        <button class="btn" onclick="startQuiz()" style="font-size: 1.1rem; padding: 15px 30px;">Discover Your AI Archetype</button>
                        <p style="margin-top: 1rem; font-size: 0.9rem; color: #666;">Takes 5 minutes • Research-based insights • No email required</p>
                    </div>
                    
                    <!-- Expandable Archetypes Section -->
                    <div style="text-align: center; margin-top: 2.5rem;">
                        <button onclick="toggleArchetypes()" style="background: none; border: 2px solid #667eea; color: #667eea; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600; margin-bottom: 1rem;">
                            <span id="archetypes-toggle-text">Meet the AI Archetypes</span>
                            <span id="archetypes-toggle-icon" style="margin-left: 8px;">▼</span>
                        </button>
                        <div id="archetypes-preview" class="hidden" style="margin-top: 2rem; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: left;">
                            <h3 style="text-align: center; margin-bottom: 1rem; color: #667eea;">The AI Workplace Archetypes</h3>
                            <p style="text-align: center; margin-bottom: 2rem; color: #666;">From The Innovator who sees adventure to The Guardian who prioritizes safety—each archetype brings essential perspectives to AI adoption.</p>
                            <div class="archetypes-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
                                {"".join(f'''
                                <div class="archetype-preview-card" style="padding: 1.5rem; border: 1px solid #e9ecef; border-radius: 8px; border-left: 4px solid {archetype['color']};">
                                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                                        <span style="font-size: 2rem;">{archetype['icon']}</span>
                                        <h4 style="margin: 0; color: {archetype['color']};">{archetype['name']}</h4>
                                    </div>
                                    <p style="margin-bottom: 1rem; color: #666;">{archetype['description']}</p>
                                    <div style="margin-bottom: 1rem;">
                                        <strong style="color: #333;">Key Traits:</strong>
                                        <ul style="margin: 0.5rem 0 0 1rem; color: #666;">
                                            {"".join(f"<li>{trait}</li>" for trait in archetype['characteristics'][:2])}
                                        </ul>
                                    </div>
                                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; font-size: 0.9rem;">
                                        <strong>Approach:</strong> {archetype['approach'][:100]}...
                                    </div>
                                </div>
                                ''' for name, archetype in QUIZ_DATA['archetypes'].items())}
                            </div>
                        </div>
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
                        <div id="secondary-archetype" class="hidden" style="text-align: center; margin-bottom: 1rem;">
                            <span style="color: #7c3aed; font-weight: 600;">with </span>
                            <span id="secondary-name" style="color: #7c3aed; font-weight: 600;"></span>
                            <span style="color: #7c3aed; font-weight: 600;"> influences</span>
                        </div>
                        <p id="result-description" style="font-size: 1.1rem; margin-bottom: 2rem;"></p>
                        
                        <!-- Radar Chart -->
                        <div style="text-align: center; margin: 2rem 0;">
                            <h3 style="margin-bottom: 1rem;">Your Archetype Profile</h3>
                            <canvas id="radar-chart" width="400" height="400" style="max-width: 100%; height: auto;"></canvas>
                        </div>
                        
                        <div class="characteristics">
                            <h3 style="margin-bottom: 1rem;">Key Characteristics:</h3>
                            <ul id="result-characteristics"></ul>
                        </div>
                        
                        <!-- Secondary Archetype Details -->
                        <div id="secondary-details" class="hidden" style="background: #f8f4ff; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0; border-left: 4px solid #7c3aed;">
                            <h4 style="color: #7c3aed; margin-bottom: 1rem;">Secondary Archetype Influence</h4>
                            <p id="secondary-description"></p>
                            <div style="margin-top: 1rem;">
                                <strong>Additional traits you may exhibit:</strong>
                                <ul id="secondary-characteristics" style="margin-top: 0.5rem;"></ul>
                            </div>
                        </div>
                        
                        <div style="background: #f0f3ff; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0;">
                            <h4 style="color: #667eea; margin-bottom: 1rem;">How to work with this archetype:</h4>
                            <p id="result-approach"></p>
                        </div>
                        
                        <div style="background: #fff5f5; padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0;">
                            <h4 style="color: #e53e3e; margin-bottom: 1rem;">Potential risks to watch:</h4>
                            <p id="result-risks"></p>
                        </div>
                        
                        <!-- All Archetypes Reference -->
                        <div style="margin: 2rem 0;">
                            <button onclick="toggleAllArchetypes()" style="background: none; border: 2px solid #667eea; color: #667eea; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600; width: 100%;">
                                <span id="all-archetypes-toggle-text">Compare with All 11 Archetypes</span>
                                <span id="all-archetypes-toggle-icon" style="margin-left: 8px;">▼</span>
                            </button>
                            <div id="all-archetypes" class="hidden" style="margin-top: 2rem; padding: 2rem; background: #f8f9fa; border-radius: 12px;">
                                <h3 style="text-align: center; margin-bottom: 1rem; color: #667eea;">All 11 AI Workplace Archetypes</h3>
                                <p style="text-align: center; margin-bottom: 2rem; color: #666; font-style: italic;">
                                    Framework based on technology adoption research (Rogers, UTAUT), behavioral science, and digital transformation literature.
                                </p>
                                <div class="archetypes-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
                                    {"".join(f'''
                                    <div class="archetype-preview-card" style="padding: 1.5rem; background: white; border-radius: 8px; border-left: 4px solid {archetype['color']}; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                                            <span style="font-size: 2rem;">{archetype['icon']}</span>
                                            <h4 style="margin: 0; color: {archetype['color']};">{archetype['name']}</h4>
                                        </div>
                                        <p style="margin-bottom: 1rem; color: #666;">{archetype['description']}</p>
                                        <div style="margin-bottom: 1rem;">
                                            <strong style="color: #333;">Key Traits:</strong>
                                            <ul style="margin: 0.5rem 0 0 1rem; color: #666; font-size: 0.9rem;">
                                                {"".join(f"<li>{trait}</li>" for trait in archetype['characteristics'])}
                                            </ul>
                                        </div>
                                        <div style="background: #f8f9fa; padding: 1rem; border-radius: 6px; font-size: 0.9rem;">
                                            <strong>How they work:</strong> {archetype['approach']}
                                        </div>
                                    </div>
                                    ''' for name, archetype in QUIZ_DATA['archetypes'].items())}
                                </div>
                            </div>
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
                
                // Reset selections for new question
                selections = [];
                
                let html = `<div class="question">
                    <div class="question-text">${{question.question}}</div>`;
                
                // Add instructions for multi-choice (skip demographic question)
                if (currentQuestion > 0) {{
                    html += `<div class="question-instructions">
                        Click up to 3 options that resonate with you. Your first choice counts most.
                    </div>`;
                }}
                
                // Check for existing answers
                const existingAnswer = answers[question.id];
                if (existingAnswer) {{
                    if (typeof existingAnswer === 'string') {{
                        // Single choice format (legacy)
                        selections = [{{ answer: existingAnswer, element: null }}];
                    }} else if (existingAnswer.primary || existingAnswer.secondary) {{
                        // Multi-choice format
                        if (existingAnswer.primary) {{
                            selections.push({{ answer: existingAnswer.primary, element: null }});
                        }}
                        if (existingAnswer.secondary && Array.isArray(existingAnswer.secondary)) {{
                            existingAnswer.secondary.forEach(sec => {{
                                selections.push({{ answer: sec, element: null }});
                            }});
                        }}
                    }}
                }}
                
                for (const [key, text] of Object.entries(question.answers)) {{
                    const isSelected = selections.some(s => s.answer === key);
                    const selectionIndex = selections.findIndex(s => s.answer === key);
                    let optionClass = 'option';
                    
                    if (isSelected) {{
                        optionClass += ' selected';
                        if (selectionIndex === 0) optionClass += ' primary';
                        else if (selectionIndex === 1) optionClass += ' secondary';
                        else if (selectionIndex === 2) optionClass += ' tertiary';
                    }}
                    
                    html += `<div class="${{optionClass}}" onclick="selectAnswer('${{key}}', this)">
                        <div class="option-letter">${{key}}</div>
                        <div>${{text}}</div>`;
                    
                    // Add badge if selected
                    if (isSelected) {{
                        const badgeNumber = selectionIndex + 1;
                        const badgeType = selectionIndex === 0 ? 'primary' : selectionIndex === 1 ? 'secondary' : 'tertiary';
                        html += `<div class="selection-badge selection-badge--${{badgeType}}">${{badgeNumber}}</div>`;
                    }}
                    
                    html += `</div>`;
                }}
                
                html += '</div>';
                document.getElementById('question-container').innerHTML = html;
                
                // Update selections array with actual DOM elements
                selections.forEach((selection, index) => {{
                    const element = document.querySelector(`[onclick*="${{selection.answer}}"]`);
                    if (element) {{
                        selections[index].element = element;
                    }}
                }});
                
                updateNavigation();
            }}
            
            let selections = [];
            const MAX_SELECTIONS = 3;
            
            function selectAnswer(answer, element) {{
                const questionId = quizData.questions[currentQuestion].id;
                
                // Check if this answer is already selected
                const existingIndex = selections.findIndex(s => s.answer === answer);
                
                if (existingIndex !== -1) {{
                    // Remove this selection and shift others down
                    selections.splice(existingIndex, 1);
                    element.classList.remove('selected', 'primary', 'secondary', 'tertiary');
                    removeBadge(element);
                }} else if (selections.length < MAX_SELECTIONS) {{
                    // Add new selection
                    selections.push({{ answer: answer, element: element }});
                    updateSelectionStyles();
                }}
                
                // Update answer format for backend
                if (selections.length > 0) {{
                    answers[questionId] = {{
                        primary: selections[0]?.answer || null,
                        secondary: selections.slice(1).map(s => s.answer)
                    }};
                }} else {{
                    delete answers[questionId];
                }}
                
                // Log answer selection
                logAnalytics('answer_selected', {{
                    question_id: questionId,
                    selections: selections.map(s => s.answer),
                    question_number: currentQuestion + 1
                }});
                
                updateNavigation();
            }}
            
            function updateSelectionStyles() {{
                // Reset all selections
                document.querySelectorAll('.option').forEach(opt => {{
                    opt.classList.remove('selected', 'primary', 'secondary', 'tertiary');
                    removeBadge(opt);
                }});
                
                // Apply styles based on selection order
                selections.forEach((selection, index) => {{
                    const element = selection.element;
                    element.classList.add('selected');
                    
                    if (index === 0) {{
                        element.classList.add('primary');
                        addBadge(element, '1', 'primary');
                    }} else if (index === 1) {{
                        element.classList.add('secondary');
                        addBadge(element, '2', 'secondary');
                    }} else if (index === 2) {{
                        element.classList.add('tertiary');
                        addBadge(element, '3', 'tertiary');
                    }}
                }});
            }}
            
            function addBadge(element, number, type) {{
                const badge = document.createElement('div');
                badge.className = `selection-badge selection-badge--${{type}}`;
                badge.textContent = number;
                element.appendChild(badge);
            }}
            
            function removeBadge(element) {{
                const badge = element.querySelector('.selection-badge');
                if (badge) {{
                    badge.remove();
                }}
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
                const secondaryArchetype = result?.secondary_archetype ? quizData.archetypes[result.secondary_archetype] : null;
                
                if (archetype) {{
                    document.getElementById('result-icon').textContent = archetype.icon;
                    document.getElementById('result-name').textContent = archetype.name;
                    document.getElementById('result-description').textContent = archetype.description;
                    document.getElementById('result-approach').textContent = archetype.approach;
                    document.getElementById('result-risks').textContent = archetype.risks;
                    
                    // Show secondary archetype if exists
                    if (secondaryArchetype) {{
                        document.getElementById('secondary-archetype').classList.remove('hidden');
                        document.getElementById('secondary-name').textContent = secondaryArchetype.name;
                        document.getElementById('secondary-details').classList.remove('hidden');
                        document.getElementById('secondary-description').textContent = secondaryArchetype.description;
                        
                        const secondaryCharList = document.getElementById('secondary-characteristics');
                        secondaryCharList.innerHTML = '';
                        secondaryArchetype.characteristics.slice(0, 3).forEach(char => {{
                            const li = document.createElement('li');
                            li.textContent = char;
                            secondaryCharList.appendChild(li);
                        }});
                    }}
                    
                    const charList = document.getElementById('result-characteristics');
                    charList.innerHTML = '';
                    archetype.characteristics.forEach(char => {{
                        const li = document.createElement('li');
                        li.textContent = char;
                        charList.appendChild(li);
                    }});
                    
                    // Create radar chart
                    createRadarChart(result.scores);
                    
                    // Log completion
                    logAnalytics('quiz_completed', {{
                        archetype: result.primary_archetype,
                        secondary_archetype: result.secondary_archetype,
                        archetype_name: archetype.name,
                        completion_time: result.completion_time,
                        role: result.role_demographic
                    }});
                }} else {{
                    displayLocalResults();
                }}
                
                showScreen('results');
            }}
            
            function createRadarChart(scores) {{
                const canvas = document.getElementById('radar-chart');
                const ctx = canvas.getContext('2d');
                const centerX = canvas.width / 2;
                const centerY = canvas.height / 2;
                const radius = Math.min(centerX, centerY) - 60;
                
                // Clear canvas
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Archetype names and colors
                const archetypes = Object.keys(quizData.archetypes);
                const colors = Object.values(quizData.archetypes).map(a => a.color);
                const maxScore = Math.max(...Object.values(scores)) || 1;
                
                // Draw background grid
                ctx.strokeStyle = '#e9ecef';
                ctx.lineWidth = 1;
                for (let i = 1; i <= 5; i++) {{
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, (radius * i) / 5, 0, 2 * Math.PI);
                    ctx.stroke();
                }}
                
                // Draw axes and labels
                ctx.strokeStyle = '#e9ecef';
                ctx.fillStyle = '#666';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                
                archetypes.forEach((archetype, i) => {{
                    const angle = (i * 2 * Math.PI) / archetypes.length - Math.PI / 2;
                    const x = centerX + Math.cos(angle) * radius;
                    const y = centerY + Math.sin(angle) * radius;
                    
                    // Draw axis line
                    ctx.beginPath();
                    ctx.moveTo(centerX, centerY);
                    ctx.lineTo(x, y);
                    ctx.stroke();
                    
                    // Draw label
                    const labelX = centerX + Math.cos(angle) * (radius + 30);
                    const labelY = centerY + Math.sin(angle) * (radius + 30);
                    const archetypeData = quizData.archetypes[archetype];
                    
                    ctx.fillStyle = colors[i] || '#667eea';
                    ctx.font = 'bold 11px Arial';
                    ctx.fillText(archetypeData.name, labelX, labelY - 8);
                    ctx.font = '20px Arial';
                    ctx.fillText(archetypeData.icon, labelX, labelY + 12);
                }});
                
                // Draw data polygon
                ctx.beginPath();
                ctx.strokeStyle = '#667eea';
                ctx.fillStyle = 'rgba(102, 126, 234, 0.2)';
                ctx.lineWidth = 3;
                
                archetypes.forEach((archetype, i) => {{
                    const score = scores[archetype] || 0;
                    const normalizedScore = (score / maxScore) * radius;
                    const angle = (i * 2 * Math.PI) / archetypes.length - Math.PI / 2;
                    const x = centerX + Math.cos(angle) * normalizedScore;
                    const y = centerY + Math.sin(angle) * normalizedScore;
                    
                    if (i === 0) {{
                        ctx.moveTo(x, y);
                    }} else {{
                        ctx.lineTo(x, y);
                    }}
                    
                    // Draw score points
                    ctx.save();
                    ctx.fillStyle = colors[i] || '#667eea';
                    ctx.beginPath();
                    ctx.arc(x, y, 4, 0, 2 * Math.PI);
                    ctx.fill();
                    ctx.restore();
                }});
                
                ctx.closePath();
                ctx.fill();
                ctx.stroke();
                
                // Add score values
                ctx.fillStyle = '#333';
                ctx.font = 'bold 10px Arial';
                archetypes.forEach((archetype, i) => {{
                    const score = scores[archetype] || 0;
                    if (score > 0) {{
                        const normalizedScore = (score / maxScore) * radius;
                        const angle = (i * 2 * Math.PI) / archetypes.length - Math.PI / 2;
                        const x = centerX + Math.cos(angle) * (normalizedScore + 15);
                        const y = centerY + Math.sin(angle) * (normalizedScore + 15);
                        ctx.fillText(score.toString(), x, y);
                    }}
                }});
            }}
            
            function toggleArchetypes() {{
                const preview = document.getElementById('archetypes-preview');
                const toggleText = document.getElementById('archetypes-toggle-text');
                const toggleIcon = document.getElementById('archetypes-toggle-icon');
                
                if (preview.classList.contains('hidden')) {{
                    preview.classList.remove('hidden');
                    toggleText.textContent = 'Hide Archetypes';
                    toggleIcon.textContent = '▲';
                }} else {{
                    preview.classList.add('hidden');
                    toggleText.textContent = 'Meet the AI Archetypes';
                    toggleIcon.textContent = '▼';
                }}
            }}
            
            function toggleAllArchetypes() {{
                const allArchetypes = document.getElementById('all-archetypes');
                const toggleText = document.getElementById('all-archetypes-toggle-text');
                const toggleIcon = document.getElementById('all-archetypes-toggle-icon');
                
                if (allArchetypes.classList.contains('hidden')) {{
                    allArchetypes.classList.remove('hidden');
                    toggleText.textContent = 'Hide Archetype Comparison';
                    toggleIcon.textContent = '▲';
                }} else {{
                    allArchetypes.classList.add('hidden');
                    toggleText.textContent = 'Compare with All 11 Archetypes';
                    toggleIcon.textContent = '▼';
                }}
            }}
            
            function displayLocalResults() {{
                // Fallback local calculation would need archetype scoring logic
                // For now, default to Pragmatist
                const archetype = quizData.archetypes['Pragmatist'];
                
                document.getElementById('result-icon').textContent = archetype.icon;
                document.getElementById('result-name').textContent = archetype.name;
                document.getElementById('result-description').textContent = archetype.description;
                document.getElementById('result-approach').textContent = archetype.approach;
                document.getElementById('result-risks').textContent = archetype.risks || 'Potential challenges may vary.';
                
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
    """Submit quiz and save results with professional scoring"""
    try:
        # Calculate scores using professional scoring system
        scores, role_demographic = calculate_scores(submission.responses)
        
        if not scores:
            # Fallback if no scores calculated
            primary_archetype = "Pragmatist"
            secondary_archetype = None
            archetype_name = "The Pragmatist"
        else:
            primary_archetype, secondary_archetype = determine_primary_and_secondary(scores)
            archetype_name = QUIZ_DATA["archetypes"][primary_archetype]["name"]
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Get client info
        client_info = get_client_info(request)
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            INSERT INTO results 
            (session_id, primary_archetype, archetype_name, all_scores, responses, 
             role_demographic, completion_time, user_agent, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            primary_archetype,
            archetype_name,
            json.dumps({
                "scores": scores,
                "secondary_archetype": secondary_archetype
            }),
            json.dumps(submission.responses),
            role_demographic,
            submission.completion_time,
            client_info["user_agent"],
            client_info["ip_address"]
        ))
        conn.commit()
        conn.close()
        
        # Log analytics
        log_analytics("quiz_submitted", session_id, {
            "archetype": primary_archetype,
            "archetype_name": archetype_name,
            "completion_time": submission.completion_time,
            "role": role_demographic
        }, **client_info)
        
        return {
            "session_id": session_id,
            "primary_archetype": primary_archetype,
            "secondary_archetype": secondary_archetype,
            "archetype_name": archetype_name,
            "scores": scores,
            "role_demographic": role_demographic,
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

@app.get("/results/{session_id}", response_class=HTMLResponse)
async def get_results(session_id: str):
    """Display shared results page"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute('''
            SELECT primary_archetype, archetype_name, all_scores, completed_at, completion_time, role_demographic
            FROM results WHERE session_id = ?
        ''', (session_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Results not found")
        
        primary_archetype, archetype_name, scores_json, completed_at, completion_time, role = result
        scores = json.loads(scores_json) if scores_json else {}
        archetype = QUIZ_DATA["archetypes"][primary_archetype]
        
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{archetype_name} - AI Archetype Results</title>
            <meta name="description" content="{archetype['description']}">
            <meta property="og:title" content="My AI Archetype: {archetype_name}">
            <meta property="og:description" content="{archetype['description']} Discover how you navigate AI transformation.">
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
                .insight-box {{
                    background: #f0f3ff;
                    padding: 1.5rem;
                    border-radius: 12px;
                    margin: 1.5rem 0;
                    text-align: left;
                }}
                .insight-box h4 {{
                    color: #667eea;
                    margin-bottom: 1rem;
                }}
                .research-note {{
                    background: #f8f9fa;
                    padding: 1rem;
                    border-radius: 8px;
                    font-size: 0.9rem;
                    color: #666;
                    margin-top: 2rem;
                    text-align: center;
                    border-left: 4px solid #667eea;
                }}
            </style>
        </head>
        <body>
            <div class="result-card">
                <div class="archetype-icon">{archetype['icon']}</div>
                <h1 class="archetype-name">{archetype_name}</h1>
                <p style="font-size: 1.1rem; margin-bottom: 2rem;">{archetype['description']}</p>
                
                <div class="characteristics">
                    <h3>How you approach AI transformation:</h3>
                    <ul>
                        {" ".join(f"<li>{char}</li>" for char in archetype['characteristics'])}
                    </ul>
                </div>
                
                <div class="insight-box">
                    <h4>Working with this archetype:</h4>
                    <p>{archetype['approach']}</p>
                </div>
                
                <div class="insight-box" style="background: #fff5f5;">
                    <h4 style="color: #e53e3e;">Potential challenges to watch:</h4>
                    <p>{archetype.get('risks', 'Individual challenges may vary.')}</p>
                </div>
                
                <div class="research-note">
                    <strong>Research-Based Framework:</strong> This archetype assessment draws from leading research in technology adoption, behavioral science, and digital transformation literature.
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 2rem; margin-top: 2rem;">
                    <h3 style="color: #667eea; margin-bottom: 1rem;">Navigate AI transformation with confidence</h3>
                    <p style="color: #666; margin-bottom: 1.5rem;">Understanding your archetype is just the beginning. Discover how you can work effectively with all types during this paradigm shift.</p>
                    <a href="/" class="btn">Discover Your AI Archetype</a>
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
        
        # Get role distribution
        cursor = conn.execute('''
            SELECT role_demographic, COUNT(*) as count
            FROM results 
            WHERE role_demographic IS NOT NULL
            GROUP BY role_demographic
            ORDER BY count DESC
        ''')
        role_distribution = cursor.fetchall()
        
        conn.close()
        
        # Create distribution chart data
        chart_data = []
        for archetype_name, archetype_display_name, count, percentage in distribution:
            archetype = QUIZ_DATA["archetypes"].get(archetype_name, {})
            chart_data.append({
                "name": archetype_display_name,
                "icon": archetype.get("icon", "📊"),
                "count": count,
                "percentage": percentage,
                "description": archetype.get("description", "AI workplace archetype")
            })
        
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Professional AI Archetype Quiz - Summary Statistics</title>
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
            </style>
        </head>
        <body>
            <div class="container">
                <div class="summary-card">
                    <h1 style="text-align: center; color: #667eea; margin-bottom: 2rem;">
                        Professional AI Archetype Quiz Summary
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
                            <div class="stat-number">11</div>
                            <div>Research-Based Archetypes</div>
                        </div>
                    </div>
                    
                    <h2 style="margin-bottom: 1rem;">Archetype Distribution</h2>
                    <p style="color: #666; margin-bottom: 2rem;">Professional scoring system - answer order doesn't affect results.</p>
                    
                    <div style="margin-bottom: 2rem;">
                        {"".join(f'''
                        <div class="archetype-item">
                            <div class="archetype-icon">{item["icon"]}</div>
                            <div class="archetype-info">
                                <div style="font-weight: 600;">{item["name"]}</div>
                                <div style="font-size: 0.9rem; color: #666; margin-top: 4px;">{item["description"]}</div>
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
                    
                    <h3 style="margin-bottom: 1rem;">Role Demographics</h3>
                    <div style="margin-bottom: 2rem;">
                        {"".join(f'''
                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">
                            <span style="text-transform: capitalize;">{role.replace('_', ' ')}</span>
                            <span>{count} ({round(count/total*100, 1)}%)</span>
                        </div>
                        ''' for role, count in role_distribution) if role_distribution else "<p>Role data being collected...</p>"}
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
                "percentage": row[3]
            }
            for row in cursor.fetchall()
        ]
        
        # Total submissions
        cursor = conn.execute('SELECT COUNT(*) FROM results')
        total = cursor.fetchone()[0]
        
        # Role distribution
        cursor = conn.execute('''
            SELECT role_demographic, COUNT(*) as count
            FROM results 
            WHERE role_demographic IS NOT NULL
            GROUP BY role_demographic
            ORDER BY count DESC
        ''')
        roles = dict(cursor.fetchall())
        
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
            "role_distribution": roles,
            "daily_submissions": daily_stats,
            "recent_events": events,
            "quiz_version": "3.0-professional",
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
            "version": "3.0-professional",
            "questions": len(QUIZ_DATA["questions"]),
            "total_results": total_results,
            "database": "connected",
            "features": ["professional_scoring", "position_independent", "archetype_based"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # to run app locally, use the command: python main.py
    # local app is available at http://localhost:8000