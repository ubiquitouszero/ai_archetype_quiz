# AI Archetype Quiz

A comprehensive 10-question assessment to discover workplace AI personalities, built for the [Accelerating Humans Podcast](https://acceleratinghumans.com). This professional-grade quiz identifies how individuals approach AI adoption and provides personalized insights for teams and organizations.

## 🚀 Live Demo

- **Take the Quiz**: [https://ai-archetype-quiz.fly.dev](https://ai-archetype-quiz.fly.dev)
- **Live Results**: [https://ai-archetype-quiz.fly.dev/summary](https://ai-archetype-quiz.fly.dev/summary)
- **API Health**: [https://ai-archetype-quiz.fly.dev/health](https://ai-archetype-quiz.fly.dev/health)

## 🧠 The 11 AI Archetypes

The quiz identifies distinct workplace AI personalities based on behavioral research and technology adoption patterns:

| Archetype | Icon | Core Approach | Key Traits |
|-----------|------|---------------|------------|
| **The Scholar** | 📚 | Evidence-based analysis | Research-focused, data-driven, methodical |
| **The Strategist** | 📈 | Business value optimization | ROI-focused, competitive, goal-oriented |
| **The Humanist** | 🤝 | People-centered implementation | Empathetic, collaborative, values-driven |
| **The Pragmatist** | 🔧 | Practical, incremental adoption | Realistic, implementation-focused, steady |
| **The Guardian** | 🛡️ | Risk management and safety | Security-conscious, compliant, cautious |
| **The Egalitarian** | ⚖️ | Equity and fairness focus | Inclusive, justice-oriented, collaborative |
| **The Innovator** | 🚀 | Cutting-edge exploration | Experimental, visionary, fast-moving |
| **The Steward** | 🌱 | Sustainable and responsible AI | Environmental, long-term thinking, ethical |
| **The Learner** | 🎓 | Education and skill building | Growth-oriented, curious, adaptive |
| **The Integrator** | 🔗 | Systems and process focus | Systematic, organized, bridge-building |
| **The Skeptic** | 🤔 | Critical evaluation | Questioning, cautious, analytical |

## ✨ Features

### Professional Assessment
- **Research-Based Framework** - Built on technology adoption research (Rogers, UTAUT) and behavioral science
- **Position-Independent Scoring** - Answer order doesn't affect results, professional scoring algorithm
- **Multi-Choice Support** - Select up to 3 options per question with weighted scoring
- **Demographic Analytics** - Role-based insights for organizational planning

### User Experience
- **Mobile-First Design** - Responsive interface with modern gradient aesthetics
- **Accessibility Compliant** - WCAG guidelines, keyboard navigation, screen reader support
- **Progress Tracking** - Real-time progress with time estimates
- **Results Visualization** - Interactive radar charts and detailed breakdowns

### Analytics & Insights
- **Comprehensive Tracking** - Question-level analytics, completion patterns, user behavior
- **Role Demographics** - Executive, team leader, individual contributor insights
- **Shareable Results** - Individual result pages with social sharing
- **Live Dashboard** - Public statistics for podcast insights and research

### Technical Excellence
- **High Performance** - SQLite with WAL mode, optimized queries, efficient caching
- **Scalable Architecture** - FastAPI backend, persistent volumes, auto-scaling
- **Database Migrations** - Automatic schema updates, backwards compatibility
- **Health Monitoring** - Comprehensive health checks and error tracking

## 📊 API Endpoints

### Public Endpoints
- `GET /` - Interactive quiz interface
- `GET /results/{session_id}` - Shareable individual results
- `GET /summary` - Public statistics dashboard
- `GET /health` - Application health status

### API Endpoints
- `POST /api/submit` - Submit quiz responses
- `GET /api/stats` - Aggregate analytics (JSON)
- `POST /api/analytics` - Event tracking
- `GET /api/quiz/data` - Quiz structure (if needed)

## 🛠 Technical Stack

- **Backend**: FastAPI 0.104+ with Python 3.11
- **Database**: SQLite with Write-Ahead Logging (WAL)
- **Frontend**: Vanilla JavaScript with modern CSS
- **Deployment**: Fly.io with persistent volumes
- **Analytics**: Custom event tracking system
- **Styling**: CSS Grid/Flexbox with design system

## 📈 Analytics & Research

### Comprehensive Data Collection
- **User Journey Tracking**: Page views, quiz starts, question interactions, completions
- **Behavioral Insights**: Answer patterns, completion times, navigation behavior
- **Performance Metrics**: Load times, error rates, user engagement
- **Demographic Analysis**: Role-based archetype distributions

### Research Applications
- **Organizational Assessment**: Team AI readiness evaluation
- **Change Management**: Tailored adoption strategies by archetype
- **Training Programs**: Personalized learning paths
- **Market Research**: Industry AI adoption patterns

### Privacy & Ethics
- **Anonymous by Default**: No PII collection, session-based tracking
- **Transparent Data Use**: Clear analytics disclosure
- **User Control**: Shareable results are opt-in
- **GDPR Considerations**: EU-compliant data handling

## 🚀 Quick Deployment

### Deploy to Fly.io (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-archetype-quiz.git
cd ai-archetype-quiz

# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login and deploy
flyctl auth login
flyctl launch --copy-config --name your-app-name

# Create persistent volume for database
flyctl volumes create quiz_data --size 1gb

# Deploy application
flyctl deploy
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Access at http://localhost:8000
```

### Environment Configuration

```bash
# Optional: Set environment variables
export SECRET_KEY="your-secret-key"
export ENVIRONMENT="production"

# For future OAuth features
export GOOGLE_CLIENT_ID="your-oauth-client-id"
export GOOGLE_CLIENT_SECRET="your-oauth-secret"
```

## 📁 Project Structure

```
ai-archetype-quiz/
├── main.py                 # FastAPI application with embedded quiz logic
├── requirements.txt        # Python dependencies
├── fly.toml               # Fly.io deployment configuration
├── Dockerfile             # Container configuration
├── data/                  # Database storage (auto-created)
│   └── quiz.db           # SQLite database with analytics
├── static/               # Static assets
│   ├── app.js           # Quiz frontend logic
│   ├── style.css        # Modern CSS with design system
│   └── images/          # Icons and graphics
├── templates/            # Jinja2 templates
│   ├── index.html       # Main quiz interface
│   ├── results.html     # Shareable results page
│   └── summary.html     # Public statistics dashboard
├── deploy/               # Deployment scripts
│   └── deploy.sh        # Production deployment automation
└── .github/workflows/    # GitHub Actions CI/CD
    └── fly-deploy.yml   # Automated deployment
```

## 💾 Database Schema

### Results Table
```sql
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    primary_archetype TEXT NOT NULL,
    archetype_name TEXT NOT NULL,
    all_scores TEXT NOT NULL,           -- JSON: detailed scoring
    responses TEXT NOT NULL,            -- JSON: user responses
    role_demographic TEXT,              -- User role category
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_time REAL,              -- Duration in minutes
    user_agent TEXT,                   -- Browser info
    ip_address TEXT                    -- Geographic analysis
);
```

### Analytics Table
```sql
CREATE TABLE analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,          -- quiz_started, question_answered, etc.
    session_id TEXT,                   -- Links to results
    event_data TEXT,                   -- JSON: event details
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 Use Cases & Applications

### For Organizations
- **Team Assessment**: Understand your team's AI adoption readiness and resistance patterns
- **Change Management**: Design AI rollouts that account for different personality types
- **Training & Development**: Create targeted learning experiences based on archetypes
- **Strategic Planning**: Make informed decisions about AI implementation timelines

### For Researchers & Academics
- **Behavioral Studies**: Anonymous aggregate data on workplace AI attitudes
- **Longitudinal Research**: Track changing perceptions over time
- **Cross-Industry Analysis**: Compare AI readiness across sectors
- **Publication-Ready Data**: Exportable datasets for academic research

### For Content Creators & Podcasters
- **Audience Insights**: Deep understanding of listener AI perspectives
- **Content Strategy**: Episode planning based on archetype distribution
- **Community Building**: Foster discussions around AI workplace personalities
- **Lead Generation**: High-value content that captures audience engagement

### For Consultants & Coaches
- **Client Assessment**: Rapid evaluation of organizational AI readiness
- **Workshop Design**: Customized training based on team composition
- **Change Strategy**: Data-driven approach to AI adoption planning
- **Progress Tracking**: Measure attitude shifts over time

## 🔧 Customization & Extension

### Adding New Questions
Update the quiz data structure in `main.py`:

```python
"questions": [
    {
        "id": 11,
        "question": "Your custom question text?",
        "type": "standard",  # or "demographic" 
        "answers": {
            "A": "Scholar-oriented response",
            "B": "Strategist-oriented response",
            "C": "Humanist-oriented response",
            # ... map to appropriate archetypes
        },
        "scoring": {
            "A": "Scholar",
            "B": "Strategist", 
            "C": "Humanist",
            # ... archetype mappings
        }
    }
]
```

### Modifying Archetypes
Extend archetype definitions:

```python
"archetypes": {
    "Scholar": {
        "name": "The Scholar",
        "description": "Your updated description",
        "characteristics": ["Updated trait 1", "Updated trait 2"],
        "approach": "How to work with this archetype",
        "risks": "Potential challenges to watch",
        "icon": "📚",
        "color": "#4ECDC4"
    }
}
```

### Custom Styling
The application uses a CSS design system in `/static/style.css`:

```css
:root {
    --color-primary: #667eea;
    --color-secondary: #f0f3ff;
    --radius-base: 8px;
    /* Customize design tokens */
}
```

### Analytics Integration
Add your preferred analytics platform:

```html
<!-- In templates/index.html -->
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>

<!-- Plausible Analytics -->
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

## 📊 Monitoring & Operations

### Health Monitoring
```bash
# Check application health
curl https://your-app.fly.dev/health

# Monitor real-time logs
flyctl logs --app your-app-name

# SSH into container
flyctl ssh console --app your-app-name

# Check database
sqlite3 /app/data/quiz.db "SELECT COUNT(*) FROM results;"
```

### Performance Optimization
- **Database**: Regular VACUUM operations, query optimization
- **Caching**: Static asset caching, API response caching
- **Scaling**: Horizontal scaling with Fly.io load balancing
- **Monitoring**: Custom metrics for quiz completion rates

### Backup & Recovery
```bash
# Backup database
flyctl ssh console --app your-app-name
sqlite3 /app/data/quiz.db ".backup backup.db"

# Download backup
flyctl ssh sftp get /app/data/backup.db ./local-backup.db
```

## 🤝 Contributing

We welcome contributions to improve the AI Archetype Quiz:

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Code Quality
- Follow PEP 8 Python style guidelines
- Add type hints for new functions
- Include docstrings for public methods
- Test your changes thoroughly

### Areas for Contribution
- **New Archetypes**: Research-backed personality types
- **Analytics Features**: Advanced reporting and insights
- **Accessibility**: Enhanced screen reader support
- **Internationalization**: Multi-language support
- **Performance**: Database optimization, caching improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Research Foundation**: Built on technology adoption research by Rogers, Venkatesh (UTAUT), and behavioral science literature
- **Design Inspiration**: Modern web standards and accessibility best practices
- **Community**: The Accelerating Humans podcast community for insights and feedback
- **Infrastructure**: Fly.io for reliable, global edge deployment

## 📞 Support & Contact

### For Technical Issues
- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/ai-archetype-quiz/issues)
- **Documentation**: Check this README and inline code comments
- **Health Check**: Monitor `/health` endpoint for system status

### For Research & Collaboration
- **Email**: [bert@acceleratinghumans.com](mailto:bert@acceleratinghumans.com)
- **Podcast**: [Accelerating Humans](https://acceleratinghumans.com)
- **Data Requests**: Contact for research partnerships

### For Business Use
- **Licensing**: MIT license allows commercial use
- **Customization**: Available for organizational implementations
- **Training**: Workshop and training opportunities

---

**Built with ❤️ for understanding human-AI collaboration in the workplace**

*Helping organizations navigate AI transformation through behavioral insights and data-driven strategies.*