#!/usr/bin/env python3
"""
Extract FLORES dataset from Parquet files to text files
"""
import pandas as pd
import os

# Read the parquet files
print("Reading FLORES parquet files...")
eng_df = pd.read_parquet('FLORES/eng_Latn.parquet')
hin_df = pd.read_parquet('FLORES/hin_Deva.parquet')

print(f"English sentences: {len(eng_df)}")
print(f"Hindi sentences: {len(hin_df)}")

# Extract the text column (usually 'sentence' or 'text')
# Let's check what columns are available
print("\nEnglish columns:", eng_df.columns.tolist())
print("Hindi columns:", hin_df.columns.tolist())

# Extract sentences (adjust column name if needed)
if 'sentence' in eng_df.columns:
    eng_sentences = eng_df['sentence'].tolist()
    hin_sentences = hin_df['sentence'].tolist()
elif 'text' in eng_df.columns:
    eng_sentences = eng_df['text'].tolist()
    hin_sentences = hin_df['text'].tolist()
else:
    # Use the first column
    eng_sentences = eng_df.iloc[:, 0].tolist()
    hin_sentences = hin_df.iloc[:, 0].tolist()

# Save to text files
print("\nSaving to text files...")
with open('FLORES/flores_eng.txt', 'w', encoding='utf-8') as f:
    for sent in eng_sentences:
        f.write(sent + '\n')

with open('FLORES/flores_hin.txt', 'w', encoding='utf-8') as f:
    for sent in hin_sentences:
        f.write(sent + '\n')

print(f"✓ Saved {len(eng_sentences)} English sentences to FLORES/flores_eng.txt")
print(f"✓ Saved {len(hin_sentences)} Hindi sentences to FLORES/flores_hin.txt")
