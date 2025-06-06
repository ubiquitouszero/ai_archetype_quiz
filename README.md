# AI Archetype Quiz

Discover how you approach AI in the workplace. Built with FastAPI and a lightweight front end.

## Features
- 10-question assessment identifying AI workplace archetypes
- Real-time admin analytics dashboard
- Public summary of archetype distribution
- OAuth-secured admin access
- Shareable individual results

## Archetypes
Based on podcast research, identifying seven workplace AI approaches:
- **Pioneer** – early adopters who see AI as adventure
- **Analyst** – data-driven, want ROI before acting
- **Worrier** – concerned about job security and change
- **Guardian** – prioritize ethics and risk management
- **Traditionalist** – prefer established methods
- **Opportunist** – see AI as competitive advantage
- **Humanitarian** – focus on equity and team impact

## Quick Deploy
```bash
git clone https://github.com/yourusername/ai-archetype-quiz
cd ai-archetype-quiz
flyctl launch
flyctl deploy
```

### Local Development
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Built with FastAPI, deployed on Fly.io. Licensed under MIT.
