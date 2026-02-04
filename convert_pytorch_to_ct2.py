#!/usr/bin/env python3
"""
Convert PyTorch INT8 Model to CTranslate2 Format
"""

import ctranslate2
import os
import sys

def convert_to_ct2():
    input_dir = "./nllb_ct2_int8"  # PyTorch model directory
    output_dir = "./nllb_ct2_int8_converted"  # CT2 output directory
    
    print("🔄 Converting PyTorch INT8 model to CTranslate2 format...")
    print(f"📥 Input: {input_dir}")
    print(f"📤 Output: {output_dir}")
    print()
    
    try:
        # Convert with INT8 quantization
        converter = ctranslate2.converters.TransformersConverter(
            model_name_or_path=input_dir,
            copy_files=["tokenizer.json", "tokenizer_config.json", "special_tokens_map.json", "sentencepiece.bpe.model"]
        )
        
        converter.convert(
            output_dir=output_dir,
            quantization="int8",
            force=True
        )
        
        print("\n✅ Conversion successful!")
        print(f"📂 CT2 model saved to: {os.path.abspath(output_dir)}")
        print()
        print("Next steps:")
        print("1. Rename directory: mv nllb_ct2_int8 nllb_ct2_int8_pytorch")
        print("2. Rename converted: mv nllb_ct2_int8_converted nllb_ct2_int8")
        print("3. Restart the app!")
        
    except Exception as e:
        print(f"\n❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    convert_to_ct2()
