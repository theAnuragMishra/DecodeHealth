# encryptor.py
import argparse
from crypt4gh import encrypt
from cryptography.hazmat.primitives import serialization
import os

def generate_keys(private_key_path='private.key', public_key_path='public.key'):
    """Generate Crypt4GH key pair if they don't exist"""
    if not os.path.exists(private_key_path):
        from crypt4gh.keys import generate_key_pair
        generate_key_pair(private_key_path, public_key_path)
        print(f"Generated new keys: {private_key_path}, {public_key_path}")

def encrypt_file(input_path, public_key_path, output_path):
    """Encrypt a genomic file using Crypt4GH"""
    # Load public key
    with open(public_key_path, 'rb') as f:
        public_key = serialization.load_ssh_public_key(f.read())
    
    # Encrypt with Crypt4GH
    with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        encrypt(keys=[(0, public_key, None)], infile=f_in, outfile=f_out)
    
    print(f"Encrypted {input_path} -> {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Encrypt genomic files with Crypt4GH')
    parser.add_argument('-i', '--input', required=True, help='Input FASTQ/FASTA file')
    parser.add_argument('-o', '--output', required=True, help='Output encrypted file (.c4gh)')
    parser.add_argument('-p', '--pubkey', default='public.key', help='Public key path')
    parser.add_argument('-g', '--generate-keys', action='store_true', help='Generate new key pair')
    
    args = parser.parse_args()
    
    if args.generate_keys:
        generate_keys()
    
    encrypt_file(args.input, args.pubkey, args.output)