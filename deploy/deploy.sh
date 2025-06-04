#!/bin/bash
set -e

echo "🚀 Deploying AI Archetype Quiz..."

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first."
    exit 1
fi

# Set secrets if they don't exist
echo "🔐 Setting up secrets..."
flyctl secrets set SECRET_KEY=$(openssl rand -base64 32) --app ai-archetype-quiz || true
flyctl secrets set GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID" --app ai-archetype-quiz || true
flyctl secrets set GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET" --app ai-archetype-quiz || true

# Deploy
echo "📦 Deploying to Fly.io..."
flyctl deploy

echo "✅ Deployment complete!"
echo "🌐 Your app is available at: https://ai-archetype-quiz.fly.dev"
