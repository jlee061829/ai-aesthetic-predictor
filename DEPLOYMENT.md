# AI Aesthetic Scorer - Deployment Guide

This guide covers multiple deployment options for the AI Aesthetic Scorer application.

## 🚀 Quick Deploy Options

### 1. Streamlit Cloud (Recommended - Easiest)

**Steps:**
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set the path to `streamlit_app.py`
5. Deploy!

**Advantages:**
- Free tier available
- Automatic deployments from GitHub
- No server management
- Built for Streamlit apps

### 2. Heroku

**Prerequisites:**
- Heroku account
- Heroku CLI installed

**Steps:**
```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Add buildpack for Python
heroku buildpacks:set heroku/python

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Open the app
heroku open
```

### 3. Railway

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will automatically detect the Dockerfile
4. Deploy!

### 4. Docker Deployment

**Local Docker:**
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build and run manually
docker build -t ai-aesthetic-scorer .
docker run -p 8501:8501 ai-aesthetic-scorer
```

**Docker on any cloud:**
- AWS ECS
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform

## 🔧 Environment Setup

### Required Environment Variables
- `PYTORCH_ENABLE_MPS_FALLBACK=1` (for Apple Silicon compatibility)

### Model Files
Ensure your model files are in the `models/` directory:
- `sa_0.4.pt` (already included)
- Any additional trained models

## 📊 Monitoring & Scaling

### Health Check
The app runs on port 8501 by default.

### Resource Requirements
- **Minimum:** 1GB RAM, 1 CPU
- **Recommended:** 2GB RAM, 2 CPU
- **GPU:** Optional (CPU inference works well)

### Scaling Considerations
- Streamlit Cloud: Automatic scaling
- Heroku: Use dyno scaling
- Docker: Use orchestration tools (Kubernetes, Docker Swarm)

## 🛠️ Troubleshooting

### Common Issues

1. **Model loading errors:**
   - Ensure model files are in the correct directory
   - Check file permissions

2. **Memory issues:**
   - Reduce batch size in model inference
   - Use CPU-only inference

3. **Port conflicts:**
   - Change port in `streamlit_app.py` or environment variables

### Logs
- Streamlit Cloud: Built-in logging
- Heroku: `heroku logs --tail`
- Docker: `docker logs <container_id>`

## 🔒 Security Considerations

1. **Environment Variables:** Store sensitive data in environment variables
2. **CORS:** Configure CORS settings in `.streamlit/config.toml`
3. **Rate Limiting:** Consider adding rate limiting for production
4. **HTTPS:** Enable HTTPS in production environments

## 📈 Performance Optimization

1. **Model Caching:** Use `@st.cache_resource` for model loading
2. **Image Processing:** Optimize image preprocessing
3. **Memory Management:** Clear cache periodically
4. **CDN:** Use CDN for static assets

## 🎯 Next Steps

1. Choose your deployment platform
2. Set up CI/CD pipeline
3. Configure monitoring and alerts
4. Set up custom domain (optional)
5. Implement user analytics

For questions or issues, check the main README.md or create an issue in the repository. 