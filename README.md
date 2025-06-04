# AI Archetype Quiz

Discover how you approach AI in the workplace. Built for behavioral health professionals and organizational leaders.

## Features
- 10-question assessment identifying AI workplace archetypes
- Real-time admin analytics dashboard
- Public summary of archetype distribution
- OAuth-secured admin access
- Shareable individual results

## Archetypes
Based on podcast research, identifying 7 workplace AI approaches:
- **Pioneer**: Early adopters who see AI as adventure
- **Analyst**: Data-driven, want ROI before acting
- **Worrier**: Concerned about job security and change
- **Guardian**: Prioritize ethics and risk management
- **Traditionalist**: Prefer established methods
- **Opportunist**: See AI as competitive advantage
- **Humanitarian**: Focus on equity and team impact

## Quick Deploy
```bash
git clone https://github.com/yourusername/ai-archetype-quiz
cd ai-archetype-quiz
flyctl launch
flyctl deploy
Local Development
bashpip install -r requirements.txt
uvicorn main:app --reload
Built with FastAPI, deployed on Fly.io. Licensed under MIT.
