#!/usr/bin/env python3
"""
Test script to verify all required packages are installed correctly
"""

print("Testing package imports...")

try:
    import streamlit as st
    print("✅ Streamlit imported successfully")
except ImportError as e:
    print(f"❌ Streamlit import failed: {e}")

try:
    import pandas as pd
    print("✅ Pandas imported successfully")
except ImportError as e:
    print(f"❌ Pandas import failed: {e}")

try:
    import numpy as np
    print("✅ NumPy imported successfully")
except ImportError as e:
    print(f"❌ NumPy import failed: {e}")

try:
    import plotly.express as px
    print("✅ Plotly Express imported successfully")
except ImportError as e:
    print(f"❌ Plotly Express import failed: {e}")

try:
    import plotly.graph_objects as go
    print("✅ Plotly Graph Objects imported successfully")
except ImportError as e:
    print(f"❌ Plotly Graph Objects import failed: {e}")

try:
    from plotly.subplots import make_subplots
    print("✅ Plotly Subplots imported successfully")
except ImportError as e:
    print(f"❌ Plotly Subplots import failed: {e}")

try:
    from prophet import Prophet
    print("✅ Prophet imported successfully")
except ImportError as e:
    print(f"❌ Prophet import failed: {e}")

try:
    import openpyxl
    print("✅ OpenPyXL imported successfully")
except ImportError as e:
    print(f"❌ OpenPyXL import failed: {e}")

print("\nAll imports completed!")
