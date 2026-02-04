#!/usr/bin/env python3
"""
Convert NLLB Base Model to CTranslate2 INT8 Format
"""

import ctranslate2
import os
import sys

def convert_nllb_to_ct2_int8():
    model_name = "facebook/nllb-200-distilled-600M"
    output_dir = "./nllb_ct2_int8_final"
    
    print("🚀 Converting NLLB to CTranslate2 INT8 format...")
    print(f"📦 Source: {model_name}")
    print(f"📂 Output: {output_dir}")
    print(f"⚡ Quantization: INT8")
    print()
    print("This will take a few minutes...")
    print()
    
    try:
        # Convert directly from HuggingFace with INT8 quantization
        converter = ctranslate2.converters.TransformersConverter(
            model_name_or_path=model_name,
            copy_files=["tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "sentencepiece.bpe.model"]
        )
        
        print("📥 Downloading and converting model...")
        converter.convert(
            output_dir=output_dir,
            quantization="int8",
            force=True
        )
        
        print("\n✅ Conversion successful!")
        print(f"📂 CT2-INT8 model saved to: {os.path.abspath(output_dir)}")
        print()
        print("📊 Model size: ~700-900MB (INT8 quantized)")
        print()
        print("Next steps:")
        print("1. Backup current: mv nllb_ct2_int8 nllb_ct2_int8_pytorch_backup")
        print("2. Use new model: mv nllb_ct2_int8_final nllb_ct2_int8")
        print("3. Restart the app: python -m app.main")
        
    except Exception as e:
        print(f"\n❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    convert_nllb_to_ct2_int8()
