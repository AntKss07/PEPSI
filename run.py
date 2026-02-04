"""
Main entry point to run the Health Report PDF Extractor server.
Run from project root: python run.py
"""
import os
import sys

# Add src directory to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

# Import and run the Flask app
from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
