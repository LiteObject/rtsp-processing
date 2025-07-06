#!/usr/bin/env python3
"""
Standalone entry point for the Streamlit UI dashboard.
This script can be run directly with: streamlit run run_ui.py
"""
from src.ui_dashboard import main
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main dashboard function

if __name__ == "__main__":
    main()
