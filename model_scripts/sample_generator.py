import os
import json
sample_data=[
  {
    "name": "Alice Smith",
    "age": 29,
    "gender": "female",
    "dna_sequence": "ATGCGTAACGT"
  },
  {
    "name": "James Lee",
    "age": 35,
    "gender": "male",
    "dna_sequence": "CGTAC"
  },
  {
    "name": "Maria Gonzalez",
    "age": 42,
    "gender": "female",
    "dna_sequence": "GGCATCGTAGGCATGCA"
  },
  {
    "name": "Omar Rahman",
    "age": 23,
    "gender": "male",
    "dna_sequence": "TACG"
  },
  {
    "name": "Lina Patel",
    "age": 31,
    "gender": "female",
    "dna_sequence": "ATCGTACGTTAG"
  },
  {
    "name": "Tom Ray",
    "age": 40,
    "gender": "male",
    "dna_sequence": "ATCGTAATGC"
  }
]
with open("sample.fasta", "w") as fasta_file:
    for i, person in enumerate(sample_data):
        name_tag = person["name"].replace(" ", "_")
        fasta_file.write(f">seq{i}_{name_tag}\n{person['dna_sequence']}\n")

print("✅ FASTA file created: sample.fasta")