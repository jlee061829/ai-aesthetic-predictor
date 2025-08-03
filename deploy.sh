#!/bin/bash

# AI Aesthetic Scorer Deployment Script
echo "🎨 AI Aesthetic Scorer - Deployment Helper"
echo "=========================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not initialized. Please run:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    exit 1
fi

# Check if we're on a branch
BRANCH=$(git branch --show-current)
echo "✅ Current branch: $BRANCH"

# Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes. Please commit them first:"
    echo "   git add ."
    echo "   git commit -m 'Update for deployment'"
    exit 1
fi

echo ""
echo "🚀 Choose your deployment option:"
echo "1. Streamlit Cloud (Recommended)"
echo "2. Heroku"
echo "3. Railway"
echo "4. Docker (Local)"
echo "5. Docker (Cloud)"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "📋 Streamlit Cloud Deployment Steps:"
        echo "1. Push to GitHub:"
        echo "   git push origin $BRANCH"
        echo ""
        echo "2. Go to https://share.streamlit.io"
        echo "3. Connect your GitHub repository"
        echo "4. Set path to: streamlit_app.py"
        echo "5. Deploy!"
        ;;
    2)
        echo ""
        echo "📋 Heroku Deployment Steps:"
        echo "1. Install Heroku CLI if not installed"
        echo "2. Login to Heroku:"
        echo "   heroku login"
        echo ""
        echo "3. Create new app:"
        echo "   heroku create your-app-name"
        echo ""
        echo "4. Deploy:"
        echo "   git push heroku $BRANCH:main"
        echo ""
        echo "5. Open app:"
        echo "   heroku open"
        ;;
    3)
        echo ""
        echo "📋 Railway Deployment Steps:"
        echo "1. Go to https://railway.app"
        echo "2. Connect your GitHub repository"
        echo "3. Railway will auto-detect the Dockerfile"
        echo "4. Deploy!"
        ;;
    4)
        echo ""
        echo "📋 Local Docker Deployment:"
        echo "1. Build and run:"
        echo "   docker-compose up --build"
        echo ""
        echo "2. Or manually:"
        echo "   docker build -t ai-aesthetic-scorer ."
        echo "   docker run -p 8501:8501 ai-aesthetic-scorer"
        echo ""
        echo "3. Access at: http://localhost:8501"
        ;;
    5)
        echo ""
        echo "📋 Cloud Docker Deployment:"
        echo "Choose your cloud platform:"
        echo "- AWS ECS"
        echo "- Google Cloud Run"
        echo "- Azure Container Instances"
        echo "- DigitalOcean App Platform"
        echo ""
        echo "Use the Dockerfile in this project."
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo "🎯 Good luck with your deployment!" 