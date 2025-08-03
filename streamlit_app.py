#!/usr/bin/env python3
"""
Streamlit Cloud deployment entry point
This file is used for Streamlit Cloud deployment
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent)
sys.path.append(project_root)

# Import and run the minimal app
from src.app_minimal import main

if __name__ == "__main__":
    main() 