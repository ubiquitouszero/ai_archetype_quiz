#!/bin/bash
# Production Deployment Script for AI Archetype Quiz
# acceleratinghumans.com

set -e

echo "🚀 Deploying AI Archetype Quiz to acceleratinghumans.com..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    print_error "flyctl is not installed. Please install it first:"
    echo "curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Check if user is logged in to Fly.io
if ! flyctl auth whoami &> /dev/null; then
    print_error "Not logged in to Fly.io. Please run 'flyctl auth login' first."
    exit 1
fi

# Validate environment
print_status "Validating environment..."

# Check if app exists
APP_NAME="accelerating-humans-quiz"
if ! flyctl apps list | grep -q "$APP_NAME"; then
    print_status "Creating new Fly.io app: $APP_NAME"
    flyctl apps create $APP_NAME --org personal
fi

# Create volume if it doesn't exist
print_status "Checking for data volume..."
if ! flyctl volumes list --app $APP_NAME | grep -q "quiz_data"; then
    print_status "Creating data volume..."
    flyctl volumes create quiz_data --size 1 --app $APP_NAME --region ord
fi

# Set secrets
print_status "Setting up secrets..."

# Generate a strong secret key if not already set
if ! flyctl secrets list --app $APP_NAME | grep -q "SECRET_KEY"; then
    SECRET_KEY=$(openssl rand -base64 32)
    flyctl secrets set SECRET_KEY="$SECRET_KEY" --app $APP_NAME
    print_success "SECRET_KEY generated and set"
else
    print_status "SECRET_KEY already exists"
fi

# Set environment
flyctl secrets set ENVIRONMENT="production" --app $APP_NAME || true

# Pre-deployment checks
print_status "Running pre-deployment checks..."

# Check if required files exist
required_files=("main.py" "requirements.txt" "fly.toml" "templates/index.html" "static/app.js" "static/style.css")
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        print_error "Required file missing: $file"
        exit 1
    fi
done

# Validate Python syntax
print_status "Validating Python syntax..."
python -m py_compile main.py
if [[ $? -ne 0 ]]; then
    print_error "Python syntax errors found in main.py"
    exit 1
fi

# Check if data files exist
if [[ ! -d "data" ]]; then
    print_warning "Data directory not found. Creating it..."
    mkdir -p data
fi

# Deploy
print_status "Deploying to Fly.io..."
flyctl deploy --wait-timeout 300 --app $APP_NAME

if [[ $? -eq 0 ]]; then
    print_success "Deployment successful!"
    
    # Post-deployment checks
    print_status "Running post-deployment health checks..."
    
    sleep 10  # Give the app time to start
    
    APP_URL="https://$APP_NAME.fly.dev"
    
    # Check health endpoint
    if curl -f -s "$APP_URL/health" > /dev/null; then
        print_success "Health check passed"
    else
        print_warning "Health check failed - app may still be starting"
    fi
    
    # Check main page
    if curl -f -s "$APP_URL/" > /dev/null; then
        print_success "Main page accessible"
    else
        print_warning "Main page check failed"
    fi
    
    # Display useful information
    echo ""
    echo "🎉 Deployment Complete!"
    echo "=================================="
    echo "App URL: $APP_URL"
    echo "Health Check: $APP_URL/health"
    echo "Quiz Stats: $APP_URL/summary"
    echo ""
    echo "📊 Monitoring Commands:"
    echo "  flyctl logs --app $APP_NAME"
    echo "  flyctl status --app $APP_NAME"
    echo "  flyctl ssh console --app $APP_NAME"
    echo ""
    echo "🔧 Management:"
    echo "  flyctl apps open --app $APP_NAME"
    echo "  flyctl scale count 2 --app $APP_NAME  # Scale up"
    echo ""
    
    # Custom domain setup reminder
    echo "🌐 Custom Domain Setup:"
    echo "To use acceleratinghumans.com:"
    echo "1. flyctl certs create acceleratinghumans.com --app $APP_NAME"
    echo "2. Add CNAME record: quiz.acceleratinghumans.com -> $APP_NAME.fly.dev"
    echo "3. Update DNS settings with your domain provider"
    echo ""
    
else
    print_error "Deployment failed!"
    echo "Check logs with: flyctl logs --app $APP_NAME"
    exit 1
fi

# Optional: Open the app
read -p "Open the deployed app in browser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    flyctl apps open --app $APP_NAME
fi