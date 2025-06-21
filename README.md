# AI Image Aesthetic Scorer

This project implements a machine learning system that predicts the aesthetic quality of images. It uses both traditional computer vision features and deep learning to analyze images and provide aesthetic scores.

## Features

- Handcrafted feature extraction (color histograms, brightness, contrast, edge detection)
- Deep learning feature extraction using pretrained CNNs
- Multiple model options (Regression and Classification)
- Model explainability using SHAP and Grad-CAM
- Web interface for easy image upload and scoring

## Project Structure

```
ai-aesthetic-scorer/
├── data/               # Dataset storage
├── models/            # Saved model files
├── src/               # Source code
│   ├── data/         # Data processing scripts
│   ├── features/     # Feature extraction code
│   ├── models/       # Model training code
│   └── utils/        # Utility functions
├── notebooks/         # Jupyter notebooks for analysis
├── tests/            # Unit tests
└── requirements.txt   # Project dependencies
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Download the AVA dataset:
```bash
python src/data/download_dataset.py
```

2. Extract features:
```bash
python src/features/extract_features.py
```

3. Train the model:
```bash
python src/models/train_model.py
```

4. Run the web interface:
```bash
streamlit run src/app.py
```

## Model Performance

- Classification accuracy: ~82% (high vs. low aesthetic)
- Mean Absolute Error (regression): ~0.8 points on 1-10 scale

## License

MIT License 