import os
import sys
import streamlit as st
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import subprocess
import cv2

# Fix for PyTorch compatibility issues with Streamlit
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

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
        border-radius: 15px;
        padding: 0.75rem 2rem;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
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
        text-align: center;
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
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Aesthetic Score", 'font': {'size': 24, 'color': '#fafafa'}},
        gauge = {
            'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "#fafafa"},
            'bar': {'color': get_score_color(score)},
            'bgcolor': "#262730",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 3], 'color': '#3e2d3b'},
                {'range': [3, 6], 'color': '#4a3d4a'},
                {'range': [6, 8], 'color': '#3f4a5f'},
                {'range': [8, 10], 'color': '#3d5a5f'}
            ],
            'threshold': {
                'line': {'color': "#d63031", 'width': 4},
                'thickness': 0.75,
                'value': 9
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="#262730",
        font={'color': "#fafafa", 'family': "Arial"}
    )
    
    return fig

# --- New Statistics Functions ---

def calculate_sharpness(image_array):
    """Calculate image sharpness using the variance of the Laplacian."""
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var

def extract_color_palette(image, num_colors=5):
    """Extract the dominant color palette from an image using histogram method."""
    # Resize for faster processing
    img = image.copy()
    img.thumbnail((100, 100))
    
    # Convert to numpy array
    pixels = np.array(img)
    
    # Calculate histograms for each channel
    hist_r = np.histogram(pixels[:, :, 0], bins=8, range=(0, 256))[0]
    hist_g = np.histogram(pixels[:, :, 1], bins=8, range=(0, 256))[0]
    hist_b = np.histogram(pixels[:, :, 2], bins=8, range=(0, 256))[0]
    
    # Find the most common color ranges
    colors = []
    for i in range(num_colors):
        # Find the bin with the highest count for each channel
        r_bin = np.argmax(hist_r)
        g_bin = np.argmax(hist_g)
        b_bin = np.argmax(hist_b)
        
        # Convert bin to color value (center of the bin)
        r_val = int((r_bin + 0.5) * 256 / 8)
        g_val = int((g_bin + 0.5) * 256 / 8)
        b_val = int((b_bin + 0.5) * 256 / 8)
        
        colors.append([r_val, g_val, b_val])
        
        # Reduce the count for this bin to find the next most common color
        hist_r[r_bin] = 0
        hist_g[g_bin] = 0
        hist_b[b_bin] = 0
    
    return np.array(colors)
def create_brightness_histogram(image_array):
    """Create a brightness histogram for the image."""
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    
    fig = go.Figure(data=[go.Bar(x=np.arange(256), y=hist.ravel())])
    fig.update_layout(
        title_text='Brightness Distribution',
        xaxis_title='Pixel Intensity (0=Black, 255=White)',
        yaxis_title='Pixel Count',
        paper_bgcolor="#262730",
        plot_bgcolor="#262730",
        font={'color': "#fafafa"},
        bargap=0,
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
    
    # Load the model
    model = load_model()
    
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

        st.markdown("---")
        st.markdown("### 🧠 Fine-Tune Your Model")
        st.markdown("""
        Improve the model's accuracy by training it on your own photos.
        
        **Instructions:**
        1. Add your photos to the `data/custom_training/images` folder.
        2. Update `data/custom_training/scores.csv` with your filenames and scores (1-10).
        3. Click the button below to start fine-tuning.
        """)
        
        if st.button("🚀 Start Fine-Tuning"):
            st.info("Fine-tuning started... This may take a few minutes. Please see the terminal for progress.")
            
            # Run the fine-tuning script
            try:
                process = subprocess.Popen(
                    [sys.executable, "src/finetune_model.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Display output in a dedicated expander
                with st.expander("Show Fine-Tuning Logs", expanded=True):
                    stdout, stderr = process.communicate()
                    if process.returncode == 0:
                        st.code(stdout, language='text')
                        st.success("Fine-tuning complete! The app will now use your personalized model.")
                        st.balloons()
                    else:
                        st.code(stderr, language='text')
                        st.error("Fine-tuning failed. Please check the logs above for errors.")
                        
            except Exception as e:
                st.error(f"An error occurred while trying to run the fine-tuning script: {e}")

    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "📁 Choose an image to analyze...",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload an image to get its aesthetic score"
        )

        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")
            
            # Auto-orient the image using ImageOps
            image = ImageOps.exif_transpose(image)
            
            # Show image with proper aspect ratio
            st.image(image, use_container_width=True, caption="Analyzed Image")
            
            # Analyze image
            with st.spinner("🎨 Analyzing aesthetic quality..."):
                score = model.predict(image)
            
            st.markdown("---")
            st.subheader("📊 Aesthetic Analysis Results")
            
            # Score display
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
            
            st.markdown("---")
            st.subheader("🔬 Image Statistics")

            # --- Display New Statistics ---
            image_array = np.array(image)
            tab1, tab2, tab3 = st.tabs(["🎨 Color Palette", "💡 Brightness", "🔪 Sharpness"])

            with tab1:
                st.write("Dominant Colors in Your Image:")
                palette = extract_color_palette(image)
                cols = st.columns(len(palette))
                for i, color in enumerate(palette):
                    hex_color = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
                    with cols[i]:
                        st.color_picker(label=f'Color {i+1}', value=hex_color, key=f'color_picker_{i}')

            with tab2:
                st.write("Brightness & Contrast Analysis:")
                brightness_fig = create_brightness_histogram(image_array)
                st.plotly_chart(brightness_fig, use_container_width=True)
                st.info("A well-exposed photo typically has a histogram with a good spread of tones across the range, without being bunched up at the edges.")

            with tab3:
                st.write("Sharpness & Focus Analysis:")
                sharpness = calculate_sharpness(image_array)
                st.metric(label="Sharpness Score (Laplacian Variance)", value=f"{sharpness:.2f}")
                
                if sharpness < 50:
                    st.warning("This image may be soft or slightly out of focus.")
                elif sharpness > 200:
                    st.success("This image appears to be sharp and in focus.")
                else:
                    st.info("This image has an average level of sharpness.")
        else:
            st.info("☝️ Upload an image to start the analysis.")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Quick tips
        st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
        st.markdown("### 💡 Quick Tips For Better Scores")
        st.markdown("""
        - Use natural lighting
        - Follow the rule of thirds
        - Ensure good contrast
        - Choose interesting subjects
        - Pay attention to composition
        
        ---
        
        #### **Common Mistakes to Avoid:**
        - Poor or harsh lighting
        - Cluttered or distracting backgrounds
        - Unbalanced composition
        - Low resolution or pixelation
        - Blurry or out-of-focus images
        """)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="analysis-box" style="margin-top: 1rem;">', unsafe_allow_html=True)
        # Recent scores (placeholder for future feature)
        st.markdown("### 📈 Recent Scores")
        st.markdown("""
        *Coming soon: Track your improvement over time!*
        """)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()