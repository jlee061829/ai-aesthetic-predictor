#!/usr/bin/env python3
"""
Test script to verify deployment setup
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import torch
        print("✅ PyTorch imported successfully")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        import plotly
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    return True

def test_model_files():
    """Test if model files exist"""
    print("\n📁 Testing model files...")
    
    model_files = [
        "src/sa_0.4.pt",
        "src/laion_aesthetic_predictor.py"
    ]
    
    for file_path in model_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def test_app_import():
    """Test if the app can be imported"""
    print("\n🚀 Testing app import...")
    
    try:
        # Add project root to path
        project_root = str(Path(__file__).parent)
        sys.path.append(project_root)
        
        # Try to import the deployment app
        from src.app_deploy import main
        print("✅ App imported successfully")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def main():
    print("🎨 AI Aesthetic Scorer - Deployment Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test model files
    files_ok = test_model_files()
    
    # Test app import
    app_ok = test_app_import()
    
    print("\n" + "=" * 50)
    if imports_ok and files_ok and app_ok:
        print("🎉 All tests passed! Your app is ready for deployment.")
        print("\nNext steps:")
        print("1. Commit your changes: git add . && git commit -m 'Deployment ready'")
        print("2. Push to GitHub: git push origin main")
        print("3. Deploy to your chosen platform")
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        if not imports_ok:
            print("- Check your requirements.txt and install dependencies")
        if not files_ok:
            print("- Ensure all model files are in the correct locations")
        if not app_ok:
            print("- Check for syntax errors in the app code")

if __name__ == "__main__":
    main() 