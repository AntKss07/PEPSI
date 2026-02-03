"""
Flask API Server for Health Report PDF Extraction
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import tempfile
from werkzeug.utils import secure_filename

from field_mapper import extract_and_map
from schema_config import FIELD_SCHEMA

app = Flask(__name__, static_folder='.')
CORS(app)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('.', 'index.html')


@app.route('/styles.css')
def styles():
    """Serve the CSS file."""
    return send_from_directory('.', 'styles.css')


@app.route('/app.js')
def app_js():
    """Serve the JavaScript file."""
    return send_from_directory('.', 'app.js')


@app.route('/api/schema', methods=['GET'])
def get_schema():
    """Return the form field schema."""
    return jsonify({
        "success": True,
        "field_count": len(FIELD_SCHEMA),
        "fields": list(FIELD_SCHEMA.keys())
    })


@app.route('/api/extract', methods=['POST'])
def extract_pdf():
    """
    Extract data from uploaded PDF and map to form fields.
    
    Expects: multipart/form-data with 'file' field containing PDF
    Returns: JSON with all mapped fields
    """
    if 'file' not in request.files:
        return jsonify({
            "success": False,
            "error": "No file uploaded"
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            "success": False,
            "error": "No file selected"
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "error": "Invalid file type. Only PDF files are allowed."
        }), 400
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract and map fields
        extracted_data = extract_and_map(filepath)
        
        # Clean up temp file
        os.remove(filepath)
        
        # Count non-empty fields
        non_empty_count = sum(1 for v in extracted_data.values() if v)
        
        return jsonify({
            "success": True,
            "filename": filename,
            "total_fields": len(extracted_data),
            "extracted_fields": non_empty_count,
            "data": extracted_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Health Report PDF Extractor"
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Health Report PDF Extractor API")
    print("=" * 60)
    print(f"Schema fields loaded: {len(FIELD_SCHEMA)}")
    print("Starting server on http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
