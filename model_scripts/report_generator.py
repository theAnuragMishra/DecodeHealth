"""
Variant Calling Pipeline

This script takes a FASTA file with DNA sequencing data, aligns it to the GRCh38 reference genome,
and outputs a VCF file with identified variants.

Requirements:
- BWA (Burrows-Wheeler Aligner)
- SAMtools
- BCFtools
- Reference genome: Homo_sapiens.GRCh38.dna.alt.fa
"""

import os
import subprocess
import argparse
import logging
from pathlib import Path
import shutil
import tempfile

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def check_dependencies():
    """Check if all required tools are installed"""
    required_tools = ['bwa', 'samtools', 'bcftools']
    missing_tools = []
    
    for tool in required_tools:
        try:
            subprocess.run([tool, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        except FileNotFoundError:
            missing_tools.append(tool)
    
    if missing_tools:
        raise EnvironmentError(f"Missing required tools: {', '.join(missing_tools)}")

def extract_bwa(bwa_tar_path, output_dir):
    """Extract BWA from tar file if needed"""
    logger = logging.getLogger(__name__)
    
    # Check if bwa is already in PATH
    try:
        subprocess.run(['bwa', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        logger.info("BWA already installed, skipping extraction")
        return
    except FileNotFoundError:
        logger.info("BWA not found in PATH, extracting from tar file")
        
    # Extract BWA
    os.makedirs(output_dir, exist_ok=True)
    subprocess.run(['tar', '-xf', bwa_tar_path, '-C', output_dir], check=True)
    
    # Add extracted BWA to PATH
    bwa_bin_dir = None
    for root, dirs, files in os.walk(output_dir):
        if 'bwa' in files:
            bwa_bin_dir = root
            break
    
    if bwa_bin_dir:
        os.environ['PATH'] = f"{bwa_bin_dir}:{os.environ['PATH']}"
        logger.info(f"Added BWA to PATH: {bwa_bin_dir}")
    else:
        raise FileNotFoundError("BWA executable not found in extracted tar file")

def index_reference(reference_path):
    """Index the reference genome if index doesn't exist"""
    logger = logging.getLogger(__name__)
    
    # Check if BWA index exists
    if not any(Path(f"{reference_path}.{ext}").exists() for ext in ['amb', 'ann', 'bwt', 'pac', 'sa']):
        logger.info("Indexing reference genome with BWA...")
        subprocess.run(['bwa', 'index', reference_path], check=True)
    else:
        logger.info("BWA index already exists")
    
    # Check if SAMtools index exists
    if not Path(f"{reference_path}.fai").exists():
        logger.info("Indexing reference genome with SAMtools...")
        subprocess.run(['samtools', 'faidx', reference_path], check=True)
    else:
        logger.info("SAMtools index already exists")

def align_and_call_variants(input_fasta, reference_path, output_vcf, threads=1):
    """Align FASTA to reference and call variants"""
    logger = logging.getLogger(__name__)
    
    # Create a temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Define intermediate file paths
        sample_name = Path(input_fasta).stem
        sam_file = f"{temp_dir}/{sample_name}.sam"
        bam_file = f"{temp_dir}/{sample_name}.bam"
        sorted_bam = f"{temp_dir}/{sample_name}.sorted.bam"
        
        # Align with BWA MEM
        logger.info("Aligning reads to reference...")
        with open(sam_file, 'w') as sam_out:
            subprocess.run([
                'bwa', 'mem',
                '-t', str(threads),
                reference_path,
                input_fasta
            ], stdout=sam_out, check=True)
        
        # Convert SAM to BAM
        logger.info("Converting SAM to BAM...")
        subprocess.run([
            'samtools', 'view',
            '-bS', sam_file,
            '-o', bam_file
        ], check=True)
        
        # Sort BAM file
        logger.info("Sorting BAM file...")
        subprocess.run([
            'samtools', 'sort',
            '-@', str(threads),
            '-o', sorted_bam,
            bam_file
        ], check=True)
        
        # Index BAM file
        logger.info("Indexing BAM file...")
        subprocess.run([
            'samtools', 'index',
            sorted_bam
        ], check=True)
        
        # Call variants with mpileup and bcftools
        logger.info("Calling variants...")
        subprocess.run([
            'bcftools', 'mpileup',
            '-f', reference_path,
            sorted_bam,
            '|',
            'bcftools', 'call',
            '-mv',
            '-o', output_vcf
        ], shell=True, check=True)
        
        # Normalize VCF
        logger.info("Normalizing variants...")
        temp_vcf = f"{temp_dir}/temp.vcf"
        shutil.move(output_vcf, temp_vcf)
        subprocess.run([
            'bcftools', 'norm',
            '-f', reference_path,
            '-o', output_vcf,
            temp_vcf
        ], check=True)
        
    logger.info(f"Variant calling complete. Results written to {output_vcf}")
    return output_vcf

def process_dna_sequencing(input_fasta, reference_path, output_vcf, bwa_tar_path=None, threads=1):
    """
    Main function to process DNA sequencing data and call variants
    
    Args:
        input_fasta: Path to input FASTA file with DNA sequencing data
        reference_path: Path to reference genome (GRCh38)
        output_vcf: Path to output VCF file
        bwa_tar_path: Path to BWA tar file (optional)
        threads: Number of threads to use
        
    Returns:
        Path to output VCF file
    """
    logger = setup_logging()
    
    # Check if input files exist
    if not os.path.exists(input_fasta):
        raise FileNotFoundError(f"Input FASTA file not found: {input_fasta}")
    
    if not os.path.exists(reference_path):
        raise FileNotFoundError(f"Reference genome not found: {reference_path}")
    
    # Extract BWA if tar file is provided
    if bwa_tar_path and os.path.exists(bwa_tar_path):
        extract_bwa(bwa_tar_path, os.path.join(os.path.dirname(output_vcf), 'tools'))
    
    # Check if required tools are installed
    check_dependencies()
    
    # Index reference genome if needed
    index_reference(reference_path)
    
    # Align and call variants
    return align_and_call_variants(input_fasta, reference_path, output_vcf, threads)