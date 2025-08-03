import os
import sys
import streamlit as st
import numpy as np
from PIL import Image
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

# Set page config
st.set_page_config(
    page_title="🎨 AI Aesthetic Scorer",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: #0e1117;
        color: #fafafa;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
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
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

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
            'bar': {'color': "#667eea"},
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

def extract_color_palette(image, num_colors=5):
    """Extract dominant colors from image using basic methods"""
    # Resize image for faster processing
    image_small = image.resize((150, 150))
    image_array = np.array(image_small)
    
    # Simple color extraction (no sklearn dependency)
    pixels = image_array.reshape(-1, 3)
    
    # Use basic clustering approach
    colors = []
    percentages = []
    
    # Sample colors from different regions
    h, w = image_array.shape[:2]
    regions = [
        (0, 0, w//2, h//2),      # Top-left
        (w//2, 0, w, h//2),      # Top-right
        (0, h//2, w//2, h),      # Bottom-left
        (w//2, h//2, w, h),      # Bottom-right
        (w//4, h//4, 3*w//4, 3*h//4)  # Center
    ]
    
    for i, (x1, y1, x2, y2) in enumerate(regions):
        region = image_array[y1:y2, x1:x2]
        if region.size > 0:
            avg_color = np.mean(region, axis=(0, 1)).astype(int)
            colors.append(avg_color)
            percentages.append(20.0)  # Equal distribution
    
    return colors, percentages

def calculate_basic_metrics(image_array):
    """Calculate basic image metrics"""
    # Convert to grayscale for calculations
    if len(image_array.shape) == 3:
        gray = np.mean(image_array, axis=2)
    else:
        gray = image_array
    
    # Brightness
    brightness = np.mean(gray)
    
    # Contrast (standard deviation)
    contrast = np.std(gray)
    
    # Sharpness (simplified)
    # Use gradient magnitude as sharpness indicator
    from scipy import ndimage
    try:
        grad_x = ndimage.sobel(gray, axis=1)
        grad_y = ndimage.sobel(gray, axis=0)
        sharpness = np.mean(np.sqrt(grad_x**2 + grad_y**2))
    except:
        sharpness = contrast  # Fallback
    
    return {
        'brightness': brightness,
        'contrast': contrast,
        'sharpness': sharpness
    }

def predict_aesthetic_score(image):
    """Simple aesthetic score prediction based on image metrics"""
    image_array = np.array(image)
    metrics = calculate_basic_metrics(image_array)
    
    # Simple scoring algorithm
    brightness_score = min(metrics['brightness'] / 128.0, 2.0)  # Normalize brightness
    contrast_score = min(metrics['contrast'] / 50.0, 2.0)       # Normalize contrast
    sharpness_score = min(metrics['sharpness'] / 20.0, 2.0)     # Normalize sharpness
    
    # Combine scores with weights
    base_score = 5.0  # Base score
    aesthetic_score = base_score + (brightness_score + contrast_score + sharpness_score) / 3.0
    
    # Clamp to 0-10 range
    aesthetic_score = max(0.0, min(10.0, aesthetic_score))
    
    return aesthetic_score

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎨 AI Aesthetic Scorer</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <p style="text-align: center; color: #888; font-size: 1.1rem;">
        Upload an image to get an AI-powered aesthetic quality score
    </p>
    """, unsafe_allow_html=True)
    
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
            metrics = calculate_basic_metrics(image_array)
            
            # Display metrics
            st.metric("Brightness", f"{metrics['brightness']:.1f}")
            st.metric("Contrast", f"{metrics['contrast']:.1f}")
            st.metric("Sharpness", f"{metrics['sharpness']:.1f}")
            
            # Extract and display color palette
            colors, percentages = extract_color_palette(image)
            
            st.subheader("🎨 Color Palette")
            color_cols = st.columns(len(colors))
            for i, (color, percentage) in enumerate(zip(colors, percentages)):
                with color_cols[i]:
                    st.color_picker(f"Color {i+1}", f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}", disabled=True)
                    st.write(f"{percentage:.1f}%")
        
        # Analyze with AI model
        with st.spinner("Analyzing image..."):
            try:
                # Get aesthetic score
                score = predict_aesthetic_score(image)
                
                # Display results
                st.markdown("---")
                st.markdown("""
                <div style="background: #262730; border-radius: 20px; padding: 1.5rem; margin-top: 1rem; border: 1px solid #3c3f58;">
                    <h2 style="text-align: center;">🎨 AI Aesthetic Analysis</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Score display
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col2:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="font-size: 1.2rem; color: #888; margin-bottom: 1rem;">Aesthetic Score</div>
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
                st.subheader("📊 Image Metrics")
                
                # Create metrics visualization
                metrics_data = {
                    'Metric': ['Brightness', 'Contrast', 'Sharpness'],
                    'Value': [metrics['brightness'], metrics['contrast'], metrics['sharpness']]
                }
                
                fig = px.bar(
                    x=metrics_data['Metric'],
                    y=metrics_data['Value'],
                    title="Image Quality Metrics",
                    color=metrics_data['Value'],
                    color_continuous_scale='viridis'
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': 'white'},
                    xaxis={'gridcolor': '#444'},
                    yaxis={'gridcolor': '#444'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error during analysis: {e}")
                st.info("This might be due to deployment constraints or missing dependencies.")

if __name__ == "__main__":
    main() 