#!/usr/bin/env python3
"""
NLLB to CTranslate2 Conversion Script (Torch 2.6+ Compatible)
"""

import ctranslate2
import transformers
import os
import sys

def convert_model():
    model_name = "facebook/nllb-200-distilled-600M"
    output_dir = "nllb_ct2_fp16"
    
    print(f"🚀 Starting conversion: {model_name} -> {output_dir}")
    print("   Using manual model loading to bypass Torch 2.6+ restrictions...")
    
    if os.path.exists(output_dir):
        print(f"⚠️  Note: {output_dir} already exists. Overwriting...")
    
    try:
        # Step 1: Manually load the model with safetensors
        print("\n📥 Loading model with transformers (using safetensors)...")
        model = transformers.AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            use_safetensors=True,  # This bypasses the torch.load security block
            torch_dtype="float16"
        )
        
        # Step 2: Load tokenizer
        print("📥 Loading tokenizer...")
        tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)
        
        # Step 3: Convert using CTranslate2
        print(f"\n🔄 Converting to CTranslate2 format...")
        converter = ctranslate2.converters.TransformersConverter(
            model_name_or_path=model_name,
            load_as_float16=True,
            copy_files=["tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"]
        )
        
        # Override the model loading with our pre-loaded model
        converter._model = model
        converter._tokenizer = tokenizer
        
        # Perform the conversion
        converter.convert(output_dir, force=True)
        
        print("\n✅ Conversion Successful!")
        print(f"📂 Model saved to: {os.path.abspath(output_dir)}")
        
    except Exception as e:
        print("\n❌ Conversion Failed!")
        print(f"Error: {str(e)}")
        
        # Provide helpful debugging info
        import traceback
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        
        sys.exit(1)

if __name__ == "__main__":
    convert_model()
