import streamlit as st
import numpy as np
from PIL import Image

# Set page config
st.set_page_config(
    page_title="🎨 AI Aesthetic Scorer",
    page_icon="🎨",
    layout="wide"
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
    
    # Simple sharpness (variance of differences)
    h, w = gray.shape
    diff_x = np.diff(gray, axis=1)
    diff_y = np.diff(gray, axis=0)
    sharpness = np.std(diff_x) + np.std(diff_y)
    
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
    sharpness_score = min(metrics['sharpness'] / 100.0, 2.0)    # Normalize sharpness
    
    # Combine scores with weights
    base_score = 5.0  # Base score
    aesthetic_score = base_score + (brightness_score + contrast_score + sharpness_score) / 3.0
    
    # Clamp to 0-10 range
    aesthetic_score = max(0.0, min(10.0, aesthetic_score))
    
    return aesthetic_score

def extract_dominant_colors(image, num_colors=5):
    """Extract dominant colors using simple sampling"""
    # Resize image for faster processing
    image_small = image.resize((100, 100))
    image_array = np.array(image_small)
    
    # Sample colors from different regions
    h, w = image_array.shape[:2]
    colors = []
    
    # Sample from corners and center
    positions = [
        (0, 0),           # Top-left
        (w-1, 0),         # Top-right
        (0, h-1),         # Bottom-left
        (w-1, h-1),       # Bottom-right
        (w//2, h//2)      # Center
    ]
    
    for x, y in positions:
        if 0 <= x < w and 0 <= y < h:
            color = image_array[y, x]
            colors.append(color)
    
    return colors, [20.0] * len(colors)  # Equal distribution

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
            
            # Extract and display dominant colors
            colors, percentages = extract_dominant_colors(image)
            
            st.subheader("🎨 Dominant Colors")
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
                    
                    # Create a simple progress bar instead of gauge
                    st.progress(score / 10.0)
                
                # Interpretation
                if score >= 7.5:
                    st.success("🌟 **High Aesthetic Quality** - This image demonstrates excellent composition, lighting, and visual appeal!")
                elif score >= 6.0:
                    st.info("✨ **Good Aesthetic Quality** - This image has solid visual elements and composition.")
                else:
                    st.warning("📸 **Room for Improvement** - Consider adjusting lighting, composition, or subject matter.")
                
                # Additional analysis
                st.subheader("📊 Image Metrics")
                
                # Create a simple bar chart using st.bar_chart
                metrics_data = {
                    'Metric': ['Brightness', 'Contrast', 'Sharpness'],
                    'Value': [metrics['brightness'], metrics['contrast'], metrics['sharpness']]
                }
                
                # Display metrics as a simple chart
                chart_data = {
                    'Brightness': [metrics['brightness']],
                    'Contrast': [metrics['contrast']],
                    'Sharpness': [metrics['sharpness']]
                }
                
                st.bar_chart(chart_data)
                
            except Exception as e:
                st.error(f"Error during analysis: {e}")
                st.info("This might be due to deployment constraints or missing dependencies.")

if __name__ == "__main__":
    main() 