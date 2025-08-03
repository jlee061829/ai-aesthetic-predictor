import os
import sys
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import cv2

# Fix for PyTorch compatibility issues with Streamlit
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Try to import PyTorch with error handling
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    st.error("PyTorch not available. Please check your installation.")
    TORCH_AVAILABLE = False

# Try to import the aesthetic predictor
try:
    from laion_aesthetic_predictor import LAIONAestheticPredictor
    PREDICTOR_AVAILABLE = True
except ImportError as e:
    st.error(f"Could not import aesthetic predictor: {e}")
    PREDICTOR_AVAILABLE = False

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
        background: #0e1117;
        color: #fafafa;
    }
    
    /* Header styling */
    .main-header {
        background: #0e1117;
        padding: 1.5rem 0;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header p {
        font-size: 1.1rem;
        color: #888;
    }
    
    /* Analysis box styling */
    .analysis-box {
        background: #262730;
        border-radius: 20px;
        padding: 1.5rem;
        margin-top: 1rem;
        border: 1px solid #3c3f58;
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
        color: #888;
        margin-bottom: 1rem;
        text-align: center;
    }

    .st-emotion-cache-1gulkj5 {
        text-align: center;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea, #764ba2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border: none;
        border-radius: 10px;
        color: white;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8, #6a4190);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    """Load the aesthetic prediction model with error handling"""
    if not TORCH_AVAILABLE:
        st.error("PyTorch is required but not available")
        return None
    
    if not PREDICTOR_AVAILABLE:
        st.error("Aesthetic predictor is not available")
        return None
    
    try:
        predictor = LAIONAestheticPredictor()
        return predictor
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

def get_score_color(score):
    """Get color based on aesthetic score"""
    if score >= 7.5:
        return "#00ff88"  # Green for high aesthetic
    elif score >= 6.0:
        return "#ffaa00"  # Orange for medium aesthetic
    else:
        return "#ff4444"  # Red for low aesthetic

def create_score_gauge(score):
    """Create a gauge chart for the aesthetic score"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Aesthetic Score"},
        delta = {'reference': 5.0},
        gauge = {
            'axis': {'range': [None, 10]},
            'bar': {'color': get_score_color(score)},
            'steps': [
                {'range': [0, 5], 'color': "lightgray"},
                {'range': [5, 7.5], 'color': "gray"},
                {'range': [7.5, 10], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 9
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return fig

def calculate_sharpness(image_array):
    """Calculate image sharpness using Laplacian variance"""
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var

def extract_color_palette(image, num_colors=5):
    """Extract dominant colors from image"""
    # Resize image for faster processing
    image_small = image.resize((150, 150))
    image_array = np.array(image_small)
    
    # Reshape to get all pixels
    pixels = image_array.reshape(-1, 3)
    
    # Use k-means to find dominant colors
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=num_colors, random_state=42)
    kmeans.fit(pixels)
    
    # Get the colors and their percentages
    colors = kmeans.cluster_centers_.astype(int)
    labels = kmeans.labels_
    
    # Calculate percentages
    unique, counts = np.unique(labels, return_counts=True)
    percentages = (counts / len(labels)) * 100
    
    return colors, percentages

def create_brightness_histogram(image_array):
    """Create brightness histogram"""
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    
    fig = px.line(
        x=range(256), 
        y=hist.flatten(),
        title="Brightness Distribution",
        labels={'x': 'Brightness', 'y': 'Frequency'}
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        xaxis={'gridcolor': '#444'},
        yaxis={'gridcolor': '#444'}
    )
    
    return fig

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎨 AI Aesthetic Scorer</h1>
        <p>Upload an image to get an AI-powered aesthetic quality score</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if model is available
    if not TORCH_AVAILABLE or not PREDICTOR_AVAILABLE:
        st.error("""
        ⚠️ **Deployment Issue Detected**
        
        The required dependencies are not available. This might be due to:
        - PyTorch installation issues
        - Missing model files
        - Deployment platform limitations
        
        Please check the deployment logs for more details.
        """)
        return
    
    # Load model
    with st.spinner("Loading AI model..."):
        model = load_model()
    
    if model is None:
        st.error("Failed to load the aesthetic prediction model. Please check the deployment logs.")
        return
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg'],
        help="Upload an image to analyze its aesthetic quality"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📸 Uploaded Image")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
        
        with col2:
            st.subheader("🎯 Analysis")
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get image array for analysis
            image_array = np.array(image)
            
            # Calculate basic metrics
            sharpness = calculate_sharpness(image_array)
            
            # Display metrics
            st.metric("Sharpness", f"{sharpness:.2f}")
            
            # Extract and display color palette
            colors, percentages = extract_color_palette(image)
            
            st.subheader("🎨 Color Palette")
            color_cols = st.columns(len(colors))
            for i, (color, percentage) in enumerate(zip(colors, percentages)):
                with color_cols[i]:
                    st.color_picker(f"Color {i+1}", f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}", disabled=True)
                    st.write(f"{percentage:.1f}%")
        
        # Analyze with AI model
        with st.spinner("Analyzing image with AI..."):
            try:
                # Get aesthetic score
                score = model.predict(image)
                
                # Display results
                st.markdown("---")
                st.markdown("""
                <div class="analysis-box">
                    <h2>🎨 AI Aesthetic Analysis</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Score display
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col2:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="score-label">Aesthetic Score</div>
                        <div class="score-value">{score:.2f}/10</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create gauge chart
                    gauge_fig = create_score_gauge(score)
                    st.plotly_chart(gauge_fig, use_container_width=True)
                
                # Interpretation
                if score >= 7.5:
                    st.success("🌟 **High Aesthetic Quality** - This image demonstrates excellent composition, lighting, and visual appeal!")
                elif score >= 6.0:
                    st.info("✨ **Good Aesthetic Quality** - This image has solid visual elements and composition.")
                else:
                    st.warning("📸 **Room for Improvement** - Consider adjusting lighting, composition, or subject matter.")
                
                # Additional analysis
                st.subheader("📊 Detailed Analysis")
                
                # Brightness histogram
                brightness_fig = create_brightness_histogram(image_array)
                st.plotly_chart(brightness_fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error during analysis: {e}")
                st.info("This might be due to model loading issues or deployment constraints.")

if __name__ == "__main__":
    main() 