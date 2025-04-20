import os
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login

def genomic_analysis_pipeline(
    input_fasta: str,
    reference_fasta: str,
    output_report: str = "test_output/genetic_report.txt",
    hf_token: str = None,
    max_variants: int = 100
):
    """
    Complete genomic analysis pipeline from FASTA to AI report
    
    Args:
        input_fasta: Path to input sample FASTA
        reference_fasta: Path to reference genome FASTA
        output_report: Output report path
        hf_token: HuggingFace authentication token
        max_variants: Maximum variants to analyze
    """
    
    # Validate inputs
    if not Path(input_fasta).exists():
        raise FileNotFoundError(f"Input FASTA not found: {input_fasta}")
    if not Path(reference_fasta).exists():
        raise FileNotFoundError(f"Reference FASTA not found: {reference_fasta}")

    # 1. Read sequences
    def read_fasta(filepath):
        with open(filepath) as f:
            return "".join(line.strip() for line in f if not line.startswith(">"))
    
    ref_seq = read_fasta(reference_fasta)
    sample_seq = read_fasta(input_fasta)

    # 2. Generate variants
    variants = []
    min_length = min(len(ref_seq), len(sample_seq))
    for pos in range(min_length):
        if ref_seq[pos] != sample_seq[pos]:
            variants.append({
                "CHROM": "chr1",
                "POS": pos + 1,
                "REF": ref_seq[pos],
                "ALT": sample_seq[pos],
                "SAMPLE": Path(input_fasta).stem
            })
            if len(variants) >= max_variants:
                break

    # 3. Create VCF
    def write_vcf(variants, vcf_path):
        with open(vcf_path, "w") as f:
            f.write("##fileformat=VCFv4.2\n")
            f.write("##source=DirectComparison\n")
            f.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE\n")
            for var in variants:
                f.write(f"{var['CHROM']}\t{var['POS']}\t.\t{var['REF']}\t{var['ALT']}"
                        f"\t100\tPASS\t.\tGT\t{var['SAMPLE']}\n")
    
    vcf_path = str(Path(output_report).with_suffix(".vcf"))
    write_vcf(variants, vcf_path)

    # 4. AI Analysis
    if hf_token:
        login(token=hf_token)
        tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
        
        with open(output_report, "w") as report:
            for var in variants:
                prompt = f"""Analyze this genetic variant:
                - Chromosome: {var['CHROM']}
                - Position: {var['POS']}
                - Reference: {var['REF']}
                - Alternate: {var['ALT']}
                - Sample: {var['SAMPLE']}
                Provide potential health implications."""
                
                inputs = tokenizer(prompt, return_tensors="pt")
                outputs = model.generate(**inputs, max_length=512, 
                                      do_sample=True, temperature=0.8)
                analysis = tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                report.write(f"## Variant {var['CHROM']}:{var['POS']}\n")
                report.write(f"REF: {var['REF']} → ALT: {var['ALT']}\n")
                report.write(f"Analysis:\n{analysis}\n\n")

    print(f"Pipeline complete. Results in {vcf_path} and {output_report}")

# Usage
genomic_analysis_pipeline(
    input_fasta="testIn/sample.fasta", 
    reference_fasta="testIn/Homo_sapiens.GRCh38.dna.alt.fa",  
    hf_token=os.environ.get("HF_TOKEN"),  
    max_variants=50
)