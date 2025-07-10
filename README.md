# AI Archetype Quiz v1.0

**Professional AI workplace personality assessment for the Accelerating Humans podcast**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-aiarchetypes.acceleratinghumans.com-blue)](https://aiarchetypes.acceleratinghumans.com)
[![Version](https://img.shields.io/badge/Version-1.0-green)](https://github.com/yourusername/ai-archetype-quiz)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## Overview

The AI Archetype Quiz helps professionals understand their natural approach to AI adoption in the workplace. Based on leading research in technology adoption, behavioral science, and digital transformation, it identifies one of 11 research-backed archetypes that describe how people navigate AI implementation.

**🎯 Purpose**: Help individuals and organizations navigate AI transformation with clarity and reduce conflict during technology adoption.

## Features

### ✨ Core Functionality
- **10-question strategic assessment** (~5 minutes)
- **11 research-based archetypes** with detailed profiles
- **Professional scoring system** (position-independent weighting)
- **Interactive radar chart visualization** (high-DPI, responsive)
- **Primary + secondary archetype detection**
- **Role-based demographic analysis**

### 📊 Analytics & Insights
- Real-time response tracking
- Archetype distribution analytics
- Role demographic breakdowns
- Completion time metrics
- Public summary statistics

### 🔧 Technical Features
- **FastAPI backend** with SQLite database
- **Responsive design** (mobile-first)
- **High-performance SMS-style UX** 
- **Shareable results** with unique URLs
- **Research references** with academic citations

## Archetypes

| Archetype | Description | Icon |
|-----------|-------------|------|
| **The Scholar** | Scientific inquiry and intellectual rigor | 📚 |
| **The Strategist** | Competitive advantage and business value | 📈 |
| **The Humanist** | Human wellbeing and dignity | 🤝 |
| **The Pragmatist** | Practical implementation and evidence | 🔧 |
| **The Guardian** | Risk management and governance | 🛡️ |
| **The Egalitarian** | Fairness and equity | ⚖️ |
| **The Innovator** | Transformative change and experimentation | 🚀 |
| **The Steward** | Environmental and resource stewardship | 🌱 |
| **The Learner/Educator** | AI literacy and skill development | 🎓 |
| **The Integrator/Facilitator** | Implementation and process improvement | 🔗 |
| **The Skeptic/Resistor** | Critical evaluation and risk awareness | 🤔 |

## Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/ai-archetype-quiz.git
cd ai-archetype-quiz

# Install dependencies
pip install fastapi uvicorn sqlite3

# Run locally
python main.py

# Access at http://localhost:8000
```

### Production Deployment

```bash
# Deploy to Fly.io (recommended)
flyctl launch --copy-config --name aiarchetypes-acceleratinghumans
flyctl volumes create quiz_data --size 1gb
flyctl deploy

# Custom domain setup
flyctl certs create aiarchetypes.acceleratinghumans.com
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main quiz interface |
| `/api/submit` | POST | Submit quiz responses |
| `/api/analytics` | POST | Log user interactions |
| `/api/stats` | GET | Public analytics data |
| `/results/{session_id}` | GET | Shareable results page |
| `/summary` | GET | Public statistics dashboard |
| `/references` | GET | Research citations |
| `/health` | GET | System health check |

## Data Storage

### Database Schema

**Results Table:**
- `session_id`: Unique identifier for each quiz completion
- `primary_archetype`: Main archetype classification
- `secondary_archetype`: Secondary influence (if significant)
- `all_scores`: JSON with complete scoring breakdown
- `responses`: User's question responses
- `role_demographic`: Professional role category
- `completion_time`: Time to complete (minutes)

**Analytics Table:**
- `event_type`: User interaction category
- `session_id`: Link to quiz session
- `event_data`: Interaction details
- `created_at`: Timestamp

### Privacy & Data Handling
- **No email collection** - anonymous by design
- **Minimal tracking** - only quiz interactions
- **User-controlled sharing** - opt-in shareable links
- **GDPR-friendly** - no personal identification

## Research Foundation

Built on established academic research:

- **Technology Adoption**: Rogers' Diffusion of Innovations, UTAUT-2
- **Behavioral Science**: Psychological factors in AI attitudes
- **Organizational Change**: Digital transformation frameworks

See `/references` for complete academic citations.

## Development

### Architecture
- **Backend**: FastAPI (Python 3.8+)
- **Database**: SQLite with automatic migrations
- **Frontend**: Vanilla JS with modern CSS
- **Visualization**: HTML5 Canvas with high-DPI support

### Key Components
- `main.py`: Complete application (all routes, logic, HTML)
- `data/quiz.db`: SQLite database (auto-created)
- Embedded quiz data (no external JSON files)

### Scoring Algorithm
- **Professional weighting**: First choice = 3 points, additional choices = 1 point
- **Position-independent**: Answer order doesn't affect results
- **Secondary detection**: Within 3 points and minimum 4 total points
- **11-archetype coverage**: Comprehensive workplace AI personality mapping

## Usage Analytics

Track key metrics:
- **Completion rate**: Quiz start to finish conversion
- **Archetype distribution**: Popular personality types
- **Role insights**: Patterns by professional position
- **Geographic trends**: Regional AI adoption attitudes

## Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/enhancement`)
3. **Test** locally with `python main.py`
4. **Commit** changes (`git commit -am 'Add enhancement'`)
5. **Push** to branch (`git push origin feature/enhancement`)
6. **Create** Pull Request

## Citation

When referencing this quiz in academic work:

> Carroll, R. (2025). AI Archetype Quiz: Understanding Workplace AI Adoption Patterns Through Behavioral Archetypes. Accelerating Humans. Available at: https://aiarchetypes.acceleratinghumans.com

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contact

**Created by**: Bert Carroll  
**Podcast**: [Accelerating Humans](https://acceleratinghumans.com)  
**Purpose**: Navigate AI transformation with clarity and confidence

---

*Version 1.0 - First production release*