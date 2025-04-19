from flask import Flask, render_template, request, jsonify, send_file
import os
import io
import base64
import json
import tempfile
from PIL import Image

from report_generator import generate_report
from encrypter import encrypt_file
from health_report_visualizer import HealthReportAnalyzer, HealthVisualizer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Ensure uploads directory exists
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_files')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_fasta', methods=['POST'])
def handle_fasta_upload():
    """
    Handle FASTA file upload from the lab via HTTP POST request
    Process through the pipeline and return results
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file part in the request'
            }), 400
            
        file = request.files['file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
            
        filename = file.filename
        
        # Save the file temporarily
        temp_path = os.path.join(UPLOAD_DIR, filename)
        file.save(temp_path)
        
        # Step 1: Generate report from FASTA file
        report = generate_report(temp_path)
        
        # Save report to a file for visualization
        report_path = os.path.join(UPLOAD_DIR, 'report.txt')
        with open(report_path, 'w') as f:
            f.write(report)
        
        # Step 2: Analyze report and generate visualization
        analyzer = HealthReportAnalyzer(llm_api_choice="ollama")  # Choose appropriate API
        vulnerabilities = analyzer.analyze_report(report)
        
        visualizer = HealthVisualizer()
        image = visualizer.generate_visualization(
            vulnerabilities,
            gender="neutral",
            crazy_mode=True
        )
        
        # Save image to a BytesIO object
        img_io = io.BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)
        
        # Encode image as base64 for sending via HTTP
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        # Step 3: Encrypt the original FASTA file
        encrypted_path = os.path.join(UPLOAD_DIR, f'{filename}.enc')
        encrypt_file(temp_path, encrypted_path)
        
        # Read encrypted file
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Encode encrypted file as base64
        encrypted_base64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        # Prepare response data
        response_data = {
            'status': 'success',
            'report': report,
            'vulnerabilities': vulnerabilities,
            'image': img_base64,
            'encrypted_file': encrypted_base64,
            'message': 'Genome data successfully processed'
        }
        
        # Clean up temporary files
        os.remove(temp_path)
        os.remove(report_path)
        os.remove(encrypted_path)
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Error processing genome data: {str(e)}'
        }), 500

# Optional: Add endpoints to download the generated files directly
@app.route('/download_image', methods=['GET'])
def download_visualization():
    """Endpoint to download the visualization as an image file"""
    try:
        # Get base64 image from the request
        img_base64 = request.args.get('image')
        if not img_base64:
            return jsonify({'status': 'error', 'message': 'No image data provided'}), 400
            
        # Decode the base64 image
        img_data = base64.b64decode(img_base64)
        img_io = io.BytesIO(img_data)
        
        # Return the image file for download
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name='health_visualization.png'
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/download_encrypted', methods=['GET'])
def download_encrypted_file():
    """Endpoint to download the encrypted file"""
    try:
        # Get base64 encrypted file from the request
        encrypted_base64 = request.args.get('file')
        if not encrypted_base64:
            return jsonify({'status': 'error', 'message': 'No encrypted file data provided'}), 400
            
        # Decode the base64 data
        encrypted_data = base64.b64decode(encrypted_base64)
        file_io = io.BytesIO(encrypted_data)
        
        # Return the file for download
        return send_file(
            file_io,
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name='genome_data.fasta.enc'
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)