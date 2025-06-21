import os
import sys
import streamlit as st
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from PIL import Image, ExifTags
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from laion_aesthetic_predictor import LAIONAestheticPredictor

# Set page config
st.set_page_config(
    page_title="🎨 AI Aesthetic Scorer",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, beautiful design
st.markdown("""
<style>
    /* Main styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Header styling */
    .main-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .main-header h1 {
        color: #2d3748;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header p {
        color: #4a5568;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 0;
    }
    
    /* Upload area styling */
    .upload-area {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    /* Image container styling */
    .image-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    /* Score display styling */
    .score-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    .score-value {
        font-size: 4rem;
        font-weight: 700;
        margin: 1rem 0;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .score-label {
        font-size: 1.2rem;
        color: #4a5568;
        margin-bottom: 1rem;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea, #764ba2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border: none;
        border-radius: 15px;
        padding: 0.75rem 2rem;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border: 2px dashed #667eea;
        border-radius: 15px;
        background: rgba(102, 126, 234, 0.05);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    /* Info box styling */
    .info-box {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Animation for score */
    @keyframes scoreAppear {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .score-animation {
        animation: scoreAppear 0.5s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Define MLP model architecture
class MLP(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 1)
        )
    
    def forward(self, x):
        return self.layers(x)

@st.cache_resource
def load_model():
    return LAIONAestheticPredictor()

def auto_orient_image(image):
    """Fix image orientation based on EXIF data"""
    try:
        # Check if image has EXIF data
        if hasattr(image, '_getexif') and image._getexif() is not None:
            exif = image._getexif()
            
            # Find orientation tag
            orientation = None
            for tag_id in ExifTags.TAGS:
                if ExifTags.TAGS[tag_id] == 'Orientation':
                    orientation = tag_id
                    break
            
            if orientation and orientation in exif:
                orientation_value = exif[orientation]
                
                # Apply rotation based on orientation value
                if orientation_value == 3:
                    image = image.rotate(180, expand=True)
                elif orientation_value == 6:
                    image = image.rotate(270, expand=True)
                elif orientation_value == 8:
                    image = image.rotate(90, expand=True)
    except Exception as e:
        st.warning(f"Could not auto-orient image: {e}")
    
    return image

def get_score_color(score):
    """Get color based on score"""
    if score >= 8:
        return "#10B981"  # Green for high scores
    elif score >= 6:
        return "#F59E0B"  # Yellow for medium scores
    else:
        return "#EF4444"  # Red for low scores

def create_score_gauge(score):
    """Create a beautiful gauge chart for the score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Aesthetic Score", 'font': {'size': 24}},
        delta = {'reference': 5, 'increasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': get_score_color(score)},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 3], 'color': '#FEE2E2'},
                {'range': [3, 6], 'color': '#FEF3C7'},
                {'range': [6, 8], 'color': '#D1FAE5'},
                {'range': [8, 10], 'color': '#DCFCE7'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 9
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎨 AI Aesthetic Scorer</h1>
        <p>Powered by LAION-Aesthetics • Discover the beauty in your images</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 About")
        st.markdown("""
        This AI model evaluates the aesthetic quality of images based on human preferences learned from millions of ratings.
        
        **How it works:**
        1. Upload your image
        2. AI analyzes visual features
        3. Get a score from 0-10
        
        **Score interpretation:**
        - **8-10**: Exceptional beauty
        - **6-8**: Good aesthetic quality
        - **4-6**: Average appeal
        - **0-4**: Needs improvement
        """)
        
        st.markdown("---")
        st.markdown("### 🔧 Technical Details")
        st.markdown("""
        - **Model**: ViT-Base + MLP
        - **Training Data**: LAION-Aesthetics dataset
        - **Features**: Visual composition, color harmony, subject appeal
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Upload area
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "📁 Choose an image to analyze...",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload an image to get its aesthetic score"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            # Load and process image
            image = Image.open(uploaded_file).convert("RGB")
            original_image = image.copy()
            
            # Auto-orient the image
            image = auto_orient_image(image)
            
            # Display image
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.subheader("🖼️ Your Image")
            
            # Show image with proper aspect ratio
            col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
            with col_img2:
                st.image(image, use_container_width=True, caption="Analyzed Image")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Analyze image
            with st.spinner("🎨 Analyzing aesthetic quality..."):
                score = model.predict(image)
            
            # Display results
            st.markdown('<div class="score-container">', unsafe_allow_html=True)
            st.subheader("📊 Aesthetic Analysis Results")
            
            # Score display
            col_score1, col_score2, col_score3 = st.columns([1, 2, 1])
            with col_score2:
                st.markdown(f"""
                <div class="score-animation">
                    <div class="score-value">{score:.1f}</div>
                    <div class="score-label">out of 10</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Gauge chart
            gauge_fig = create_score_gauge(score)
            st.plotly_chart(gauge_fig, use_container_width=True)
            
            # Score interpretation
            if score >= 8:
                st.success("🌟 **Exceptional!** This image has outstanding aesthetic appeal.")
            elif score >= 6:
                st.info("✨ **Good!** This image has solid aesthetic qualities.")
            elif score >= 4:
                st.warning("📈 **Average.** There's room for improvement in composition or lighting.")
            else:
                st.error("💡 **Needs work.** Consider improving composition, lighting, or subject matter.")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Quick tips
        st.markdown("### 💡 Quick Tips")
        st.markdown("""
        **For better scores:**
        - Use natural lighting
        - Follow rule of thirds
        - Ensure good contrast
        - Choose interesting subjects
        - Pay attention to composition
        
        **Common mistakes:**
        - Poor lighting
        - Cluttered backgrounds
        - Unbalanced composition
        - Low resolution
        - Blurry images
        """)
        
        # Recent scores (placeholder for future feature)
        st.markdown("### 📈 Recent Scores")
        st.markdown("""
        *Coming soon: Track your improvement over time!*
        """)

if __name__ == "__main__":
    main()