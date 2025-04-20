import numpy as np
import secrets
from typing import Tuple

# Define chaotic maps
def logistic_map(x: float, r: float) -> float:
    return r * x * (1 - x)

def tent_map(x: float, mu: float = 1.999) -> float:
    return mu * min(x, 1 - x)

def sine_map(x: float, a: float = 1.0) -> float:
    return a * np.sin(np.pi * x)

# Initialize maps with different parameters
MAPS = [
    lambda x: logistic_map(x, r=3.99),
    lambda x: logistic_map(x, r=3.95),
    lambda x: tent_map(x, mu=1.999),
    lambda x: sine_map(x, a=1.0)
]

# Nucleotide encoding
NUC_TO_INT = {'A': 0, 'T': 1, 'C': 2, 'G': 3}
INT_TO_NUC = {0: 'A', 1: 'T', 2: 'C', 3: 'G'}

def encrypt_dna(dna_sequence: str) -> Tuple[str, dict]:
    """
    Encrypts a DNA sequence using multiple chaotic maps with chaotic switching.
    Returns the ciphertext and a dictionary of keys needed for decryption.
    """
    # Generate random initial conditions (keys)
    keys = {
        'x0': secrets.randbelow(2**53) / (2**53),  # For chaotic state
        'x_switch': secrets.randbelow(2**53) / (2**53),  # For map switching
        'r_switch': 3.99  # Fixed parameter for switch logic
    }
    
    x0, x_switch = keys['x0'], keys['x_switch']
    encrypted_sequence = []
    
    for nuc in dna_sequence:
        # Select map dynamically (chaotic switching)
        map_idx = int(np.floor(x_switch * len(MAPS))) % len(MAPS)
        current_map = MAPS[map_idx]
        
        # Update chaotic state and switch
        x0 = current_map(x0)
        x_switch = logistic_map(x_switch, keys['r_switch'])
        
        # Encrypt nucleotide (XOR with chaotic output)
        key_byte = int(np.floor(x0 * 4)) % 4
        encrypted_nuc = NUC_TO_INT[nuc] ^ key_byte
        encrypted_sequence.append(INT_TO_NUC[encrypted_nuc % 4])
    
    return ''.join(encrypted_sequence), keys

def decrypt_dna(encrypted_sequence: str, keys: dict) -> str:
    """
    Decrypts a DNA sequence using the same keys and chaotic map switching logic.
    """
    x0, x_switch = keys['x0'], keys['x_switch']
    decrypted_sequence = []
    
    for nuc in encrypted_sequence:
        # Select map dynamically (same as encryption)
        map_idx = int(np.floor(x_switch * len(MAPS))) % len(MAPS)
        current_map = MAPS[map_idx]
        
        # Update chaotic state and switch
        x0 = current_map(x0)
        x_switch = logistic_map(x_switch, keys['r_switch'])
        
        # Decrypt nucleotide (XOR is self-inverse)
        key_byte = int(np.floor(x0 * 4)) % 4
        decrypted_nuc = NUC_TO_INT[nuc] ^ key_byte
        decrypted_sequence.append(INT_TO_NUC[decrypted_nuc % 4])
    
    return ''.join(decrypted_sequence)

