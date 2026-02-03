#!/usr/bin/env python3
"""
Download INT8 Quantized NLLB Model from HuggingFace
"""

import os
from huggingface_hub import snapshot_download
from dotenv import load_dotenv

# Load HF token from .env
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

print("🚀 Downloading INT8 Quantized NLLB Model...")
print("📦 Model: Rewatiramans/nllb-200-distilled-600M-8bit")
print("📁 Output: ./nllb_ct2_int8/")
print()

try:
    snapshot_download(
        repo_id="Rewatiramans/nllb-200-distilled-600M-8bit",
        local_dir="./nllb_ct2_int8",
        token=HF_TOKEN,
        local_dir_use_symlinks=False
    )
    
    print("\n✅ Download complete!")
    print("📂 Model saved to: ./nllb_ct2_int8/")
    
except Exception as e:
    print(f"\n❌ Download failed: {e}")
    import traceback
    traceback.print_exc()
