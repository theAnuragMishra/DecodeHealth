from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
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
socketio = SocketIO(app, cors_allowed_origins="*")

# Ensure uploads directory exists
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_files')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('upload_fasta')
def handle_fasta_upload(data):
    """
    Handle FASTA file upload from the lab via SocketIO
    Process through the pipeline and return results
    """
    try:
        # Extract file data
        file_data = data.get('file')
        filename = data.get('filename', 'genome_data.fasta')
        
        # Decode the base64 file data if it's encoded
        if isinstance(file_data, str) and file_data.startswith('data:'):
            file_data = file_data.split(',')[1]
            file_data = base64.b64decode(file_data)
        
        # Save the file temporarily
        temp_path = os.path.join(UPLOAD_DIR, filename)
        with open(temp_path, 'wb') as f:
            f.write(file_data if isinstance(file_data, bytes) else file_data.encode())
        
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
        
        # Encode image as base64 for sending via SocketIO
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        # Step 3: Encrypt the original FASTA file
        encrypted_path = os.path.join(UPLOAD_DIR, f'{filename}.enc')
        encrypt_file(temp_path, encrypted_path)
        
        # Read encrypted file
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Encode encrypted file as base64
        encrypted_base64 = base64.b64encode(encrypted_data).decode('utf-8')
        
        # Send all processed data back to client
        emit('processing_complete', {
            'status': 'success',
            'report': report,
            'vulnerabilities': vulnerabilities,
            'image': img_base64,
            'encrypted_file': encrypted_base64,
            'message': 'Genome data successfully processed'
        })
        
        # Clean up temporary files
        os.remove(temp_path)
        os.remove(report_path)
        os.remove(encrypted_path)
        
    except Exception as e:
        emit('processing_error', {
            'status': 'error',
            'message': f'Error processing genome data: {str(e)}'
        })
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)