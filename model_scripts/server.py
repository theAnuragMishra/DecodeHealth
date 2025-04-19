from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from encryption import dna_sequence_encryptor
from report_gen import report_generator
from summary_gen import summary_generator
from visualizer import summary_visualizer
import base64
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

if not app.config['SECRET_KEY']:
    raise ValueError("No FLASK_SECRET_KEY set in environment variables")

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('upload')
def handle_upload(data):
    try:
        # Process DNA encryption
        original_sequence = data.get('dna_sequence')
        if not original_sequence:
            raise ValueError("No DNA sequence found in input")
        
        encrypted_seq, private_keys = dna_sequence_encryptor(original_sequence)
        
        # Create modified JSON
        encrypted_data = data.copy()
        encrypted_data['dna_sequence'] = encrypted_seq
        encrypted_data['private_keys'] = private_keys
        emit('encrypted_data', encrypted_data)

        # Generate report from original data
        report_content = report_generator(data)  # Using original input
        emit('report_generated', {'report': report_content})

        # Generate summary from report
        summary_content = summary_generator(report_content)
        emit('summary_generated', {'summary': summary_content})

        # Generate visualization
        image_bytes = summary_visualizer(summary_content)
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        emit('visualization', {'image': image_b64})

    except Exception as e:
        emit('processing_error', {'error': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True)