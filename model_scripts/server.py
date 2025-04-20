from flask import Flask, request, abort
from flask_socketio import SocketIO, emit
from pathlib import Path
from typing import TextIO, Union
import base64
import os
import json
from io import BytesIO

# Import custom modules
from encrypt_decrypt import encrypt_dna, decrypt_dna
from health_report_visualizer import generate_health_summary, generate_health_visualization

from dotenv import load_dotenv
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

if not app.config['SECRET_KEY']:
    raise ValueError("No FLASK_SECRET_KEY set in environment variables")

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

# Environment variables
REFERENCE_FASTA = os.getenv('REFERENCE_FASTA', 'testIn/Homo_sapiens.GRCh38.dna.alt.fa')
HF_TOKEN = os.getenv('HF_TOKEN')

def run_analysis(
    input_handle: TextIO,
    reference_path: Union[str, Path],
    max_variants: int = 100,
    hf_token: str = None
) -> (str, str):
    """
    Core pipeline reading FASTA handles, returning VCF and report as strings.
    """
    # Read reference sequence
    ref_path = Path(reference_path)
    if not ref_path.exists():
        raise FileNotFoundError(f"Reference FASTA not found: {ref_path}")

    def read_fasta_from_file(f):
        return "".join(line.strip() for line in f if not line.startswith(">"))

    ref_seq = read_fasta_from_file(open(ref_path, 'r'))
    sample_seq = read_fasta_from_file(input_handle)

    # Generate variants
    variants = []
    for pos, (r, s) in enumerate(zip(ref_seq, sample_seq), start=1):
        if r != s:
            variants.append({"CHROM": "chr1", "POS": pos, "REF": r, "ALT": s})
            if len(variants) >= max_variants:
                break

    # Build VCF string
    vcf_lines = [
        "##fileformat=VCFv4.2",
        "##source=DirectComparison",
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE"
    ]
    for v in variants:
        vcf_lines.append(
            f"{v['CHROM']}\t{v['POS']}\t.\t{v['REF']}\t{v['ALT']}\t100\tPASS\t.\tGT\t{Path(input_handle.name).stem}"
        )
    vcf_str = "\n".join(vcf_lines)

    # Build AI report string
    report_lines = []
    if hf_token:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from huggingface_hub import login
        
        login(token=hf_token)
        tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        for v in variants:
            prompt = (
                f"Analyze this genetic variant:\n"
                f"- Chromosome: {v['CHROM']}\n"
                f"- Position: {v['POS']}\n"
                f"- Reference: {v['REF']}\n"
                f"- Alternate: {v['ALT']}\n"
                f"Provide potential health implications."
            )
            inputs = tokenizer(prompt, return_tensors="pt")
            outputs = model.generate(**inputs, max_length=512, do_sample=True, temperature=0.8)
            analysis = tokenizer.decode(outputs[0], skip_special_tokens=True)
            report_lines.append(f"## Variant {v['CHROM']}:{v['POS']}")
            report_lines.append(f"REF: {v['REF']} → ALT: {v['ALT']}")
            report_lines.append("Analysis:")
            report_lines.append(analysis)
            report_lines.append("")
    report_str = "\n".join(report_lines)

    return vcf_str, report_str, sample_seq

def extract_dna_sequence(fasta_content):
    """
    Extract DNA sequence from FASTA content
    """
    lines = fasta_content.splitlines()
    sequence = ""
    for line in lines:
        if not line.startswith(">"):  # Skip header lines
            sequence += line.strip()
    return sequence

@socketio.on('process_fasta')
def handle_fasta_processing(data):
    try:
        # Step 1: Validate input
        if 'fasta_content' not in data:
            raise ValueError("Missing FASTA content in input")
            
        fasta_content = data['fasta_content']
        max_variants = data.get('max_variants', 100)
        gender = data.get('gender', 'neutral')
        crazy_mode = data.get('crazy_mode', True)
        llm_api_choice = data.get('llm_api_choice', 'ollama')
        
        # Create a temporary file with the FASTA content
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.fa', delete=False) as temp_file:
            temp_file.write(fasta_content)
            temp_file.flush()
            temp_file_path = temp_file.name
        
        # Step 2: Process the FASTA file through the pipeline
        with open(temp_file_path, 'r') as input_handle:
            vcf_str, report_str, dna_sequence = run_analysis(
                input_handle, 
                REFERENCE_FASTA, 
                max_variants=max_variants, 
                hf_token=HF_TOKEN
            )
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        # Step 3: Emit report first to show progress
        emit('report_generated', {'report': report_str})
        
        # Step 4: Encrypt the DNA sequence
        encrypted_seq, keys = encrypt_dna(dna_sequence)
        
        # Step 5: Generate health summary from report
        annotated_report, vulnerabilities = generate_health_summary(
            report_str,
            llm_api_choice=llm_api_choice
        )
        
        # Step 6: Emit summary
        emit('health_summary', {
            'annotated_report': annotated_report,
            'vulnerabilities': vulnerabilities
        })
        
        # Step 7: Generate visualization from summary
        img = generate_health_visualization(
            vulnerabilities,
            gender=gender,
            crazy_mode=crazy_mode
        )
        
        # Convert image to base64 for transmission
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Step 8: Return all results together
        emit('processing_complete', {
            'report': report_str,
            'annotated_report': annotated_report,
            'encrypted_sequence': encrypted_seq,
            'encryption_keys': keys,
            'sequence_length': len(dna_sequence),
            'visualization': img_str
        })
        
    except Exception as e:
        emit('processing_error', {
            'error': str(e),
            'message': f"Error processing FASTA file: {str(e)}"
        })

if __name__ == '__main__':
    socketio.run(app, debug=True)