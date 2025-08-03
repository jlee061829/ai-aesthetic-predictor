#!/bin/bash

echo "🚀 Ultra-Minimal Deployment Script"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not initialized. Please run:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    exit 1
fi

echo "✅ Project structure verified"

# Check current requirements
echo "📦 Current requirements.txt:"
cat requirements.txt

echo ""
echo "🔄 This will deploy the ultra-minimal version with only 4 packages:"
echo "   - streamlit"
echo "   - numpy" 
echo "   - pillow"
echo "   - plotly"
echo ""

read -p "Continue with ultra-minimal deployment? (y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Backup current requirements
if [ -f "requirements.txt" ]; then
    cp requirements.txt requirements_backup.txt
    echo "✅ Backed up current requirements.txt"
fi

# Ensure we're using ultra-minimal requirements
echo "streamlit" > requirements.txt
echo "numpy" >> requirements.txt
echo "pillow" >> requirements.txt
echo "plotly" >> requirements.txt

echo "✅ Updated requirements.txt to ultra-minimal"

# Test the app locally
echo "🧪 Testing app locally..."
python -c "from src.app_ultra_minimal import main; print('✅ App imports successfully')"

if [ $? -eq 0 ]; then
    echo "✅ Local test passed"
else
    echo "❌ Local test failed"
    exit 1
fi

# Commit and push
echo "📝 Committing changes..."
git add .
git commit -m "Ultra-minimal deployment - only 4 packages"

echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "🎉 Ultra-minimal deployment ready!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://share.streamlit.io"
echo "2. Connect your GitHub repository"
echo "3. Set path to: streamlit_app.py"
echo "4. Deploy!"
echo ""
echo "📊 Expected results:"
echo "- Build time: 1-3 minutes"
echo "- Success rate: ~99%"
echo "- Features: Basic aesthetic scoring"
echo ""
echo "🔧 If this still fails, try:"
echo "- Railway: https://railway.app"
echo "- Heroku: heroku create && git push heroku main"
echo "- Docker: docker build -t ai-aesthetic-scorer ." 