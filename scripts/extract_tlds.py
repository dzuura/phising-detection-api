"""Extract unique TLDs from training dataset"""
import pandas as pd
import json
import os
import sys

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# Read dataset from data folder inside the repository
dataset_path = os.path.join(project_root, 'data', 'phishing-dataset.csv')

if not os.path.exists(dataset_path):
    print(f"Error: Dataset not found at {dataset_path}")
    print("Please place your training dataset in the 'data' folder with the name 'phishing-dataset.csv'")
    sys.exit(1)

print(f"Reading dataset from: {dataset_path}")
df = pd.read_csv(dataset_path)

# Get unique TLDs
unique_tlds = sorted(df['TLD'].unique().tolist())
print(f"Total unique TLDs: {len(unique_tlds)}")
print(f"\nFirst 20 TLDs: {unique_tlds[:20]}")
print(f"\nLast 20 TLDs: {unique_tlds[-20:]}")

# Save to JSON in project root
output_path = os.path.join(project_root, 'tld_list.json')
with open(output_path, 'w') as f:
    json.dump(unique_tlds, f, indent=2)

print(f"\nTLD list saved to {output_path}")
