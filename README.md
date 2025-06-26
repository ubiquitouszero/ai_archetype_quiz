# AI Archetype Quiz

A professional-grade quiz application to discover workplace AI personalities, built for the [Accelerating Humans Podcast](https://acceleratinghumans.com). Users take a 10-question assessment to identify their AI archetype and receive personalized insights.

## 🚀 Live Demo

- **Quiz**: [https://ai-archetype-quiz.fly.dev](https://ai-archetype-quiz.fly.dev)
- **Summary**: [https://ai-archetype-quiz.fly.dev/summary](https://ai-archetype-quiz.fly.dev/summary)
- **Health Check**: [https://ai-archetype-quiz.fly.dev/health](https://ai-archetype-quiz.fly.dev/health)

## 🧠 AI Archetypes

The quiz identifies 7 distinct workplace AI personalities:

| Archetype | Icon | Description |
|-----------|------|-------------|
| **The Pioneer** | 🚀 | Eager adopter who sees AI as adventure and advantage |
| **The Analyst** | 📊 | Wants evidence, ROI, and a plan before acting |
| **The Worrier** | 😰 | Feels threatened or uncertain about AI's impact |
| **The Guardian** | 🛡️ | Prioritizes caution, ethics, and minimizing risk |
| **The Traditionalist** | 📚 | Prefers established methods, skeptical of AI hype |
| **The Opportunist** | ⚡ | Sees AI as a way to leap ahead and disrupt |
| **The Humanitarian** | 🤝 | Focuses on equity, fairness, and team wellbeing |

## ✨ Features

### Core Functionality
- **10-Question Assessment** - Scientifically designed scenarios
- **Personalized Results** - Detailed archetype analysis with characteristics and guidance
- **Mobile Responsive** - Beautiful gradient design that works on all devices
- **Fast & Reliable** - Self-contained with embedded quiz data

### Analytics & Persistence
- **Results Database** - SQLite with persistent volume storage
- **Shareable URLs** - Individual result pages for social sharing
- **Usage Analytics** - Track quiz completions, archetypes, and user behavior
- **Summary Dashboard** - Aggregate statistics perfect for podcast insights

### API Endpoints
- `GET /` - Main quiz interface
- `GET /results/{session_id}` - Individual shareable results
- `GET /summary` - Public statistics dashboard
- `GET /api/stats` - JSON analytics data
- `POST /api/submit` - Quiz submission endpoint
- `GET /health` - Application health check

## 🛠 Technical Stack

- **Backend**: FastAPI with Python 3.11
- **Database**: SQLite with WAL mode for concurrency
- **Frontend**: Vanilla JavaScript with modern CSS
- **Deployment**: Fly.io with persistent volumes
- **Styling**: Custom CSS with gradient design and animations

## 📊 Analytics Tracking

The application tracks comprehensive analytics for podcast insights:

### Events Logged
- Page views and quiz starts
- Answer selections per question
- Quiz completions with timing
- Result sharing activity
- User engagement patterns

### Metrics Available
- Total submissions and completion rates
- Archetype distribution percentages
- Average completion times
- Daily/weekly activity trends
- Geographic patterns (anonymized)

## 🚀 Deployment

### Quick Deploy to Fly.io

```bash
# Clone and setup
git clone <repository-url>
cd ai-archetype-quiz

# Install Fly CLI and login
curl -L https://fly.io/install.sh | sh
flyctl auth login

# Deploy
flyctl launch
flyctl deploy

# Set up persistent volume for database
flyctl volumes create quiz_data --size 1gb
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python -m uvicorn main:app --reload --port 8000

# Visit http://localhost:8000
```

### Environment Variables

```bash
# Optional OAuth for admin features (future)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Production settings
SECRET_KEY=your_secret_key
ENVIRONMENT=production
```

## 🗂 Project Structure

```
ai-archetype-quiz/
├── main.py                 # FastAPI application with embedded quiz
├── requirements.txt        # Python dependencies
├── fly.toml               # Fly.io deployment configuration
├── Dockerfile             # Container configuration
├── data/                  # Database storage (created automatically)
│   └── quiz.db           # SQLite database
├── static/               # Static assets (if needed)
├── templates/            # Jinja2 templates (if needed)
└── README.md             # This file
```

## 📈 Database Schema

### Results Table
```sql
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    primary_archetype TEXT NOT NULL,
    archetype_name TEXT NOT NULL,
    all_scores TEXT NOT NULL,        -- JSON
    responses TEXT NOT NULL,         -- JSON
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_time REAL,           -- Minutes
    user_agent TEXT,
    ip_address TEXT
);
```

### Analytics Table
```sql
CREATE TABLE analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    session_id TEXT,
    event_data TEXT,                -- JSON
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 Use Cases

### For Organizations
- **Team Assessment** - Understand your team's AI adoption patterns
- **Change Management** - Tailor AI rollouts to different personality types
- **Training Programs** - Customize AI education based on archetypes
- **Hiring & Development** - Consider AI attitudes in role placement

### For Podcasters & Content Creators
- **Audience Insights** - Rich data on listener AI perspectives
- **Content Planning** - Episode topics based on archetype distribution
- **Community Building** - Foster discussions around AI personalities
- **Lead Generation** - Capture audience engagement with valuable content

### For Researchers
- **AI Adoption Studies** - Anonymous aggregate data on workplace attitudes
- **Behavioral Analysis** - Track changing AI perceptions over time
- **Market Research** - Understand professional AI readiness by segment

## 🔧 Customization

### Adding New Questions
Edit the `QUIZ_DATA` dictionary in `main.py`:

```python
{
    "id": 11,
    "question": "Your new question here?",
    "answers": {
        "A": "Pioneer response",
        "B": "Analyst response", 
        # ... etc
    }
}
```

### Modifying Archetypes
Update archetype definitions with new characteristics or insights:

```python
"A": {
    "name": "The Pioneer",
    "description": "Updated description",
    "characteristics": ["New trait 1", "New trait 2"],
    "podcast_insight": "Insight for content creators"
}
```

### Styling Changes
The application uses embedded CSS for reliability. Modify the styles in the HTML template within `main.py` or extract to separate CSS files.

## 📊 Monitoring & Analytics

### Health Monitoring
```bash
curl https://your-app.fly.dev/health
```

### Usage Statistics
```bash
curl https://your-app.fly.dev/api/stats
```

### Database Access
```bash
# SSH into Fly.io container
flyctl ssh console

# Access SQLite database
sqlite3 /app/data/quiz.db
.tables
SELECT COUNT(*) FROM results;
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Designed for the **Accelerating Humans Podcast**
- Quiz methodology based on workplace AI adoption research
- Built with modern web standards for performance and accessibility
- Deployed on Fly.io for global edge performance

## 📞 Support

For questions, issues, or podcast collaboration:

- **Issues**: [GitHub Issues](https://github.com/ubiquitouszero/ai-archetype-quiz/issues)
- **Podcast**: [Accelerating Humans](https://acceleratinghumans.com)
- **Analytics**: Check `/summary` for real-time statistics

---

**Built with ❤️ for understanding human-AI collaboration**