#!/usr/bin/env python3
"""
Quick CPU Benchmark for NLLB Model
Test CT2-FP16 and CT2-INT8 on local CPU
"""

import ctranslate2
import transformers
import time
from tqdm import tqdm

def cpu_benchmark():
    print("=" * 80)
    print("NLLB CPU BENCHMARK")
    print("=" * 80)
    
    # Load tokenizer
    model_path = "./nllb_ct2_fp16"
    print(f"\n📥 Loading tokenizer from {model_path}...")
    tokenizer = transformers.AutoTokenizer.from_pretrained(model_path)
    
    # Test sentences (small sample for quick test)
    test_sentences_en = [
        "Hello, how are you?",
        "What is your name?",
        "I love machine learning.",
        "The weather is beautiful today.",
        "Translation models are amazing.",
    ] * 20  # 100 sentences total
    
    test_sentences_hi = [
        "नमस्ते, आप कैसे हैं?",
        "आपका नाम क्या है?",
        "मुझे मशीन लर्निंग पसंद है।",
        "आज मौसम बहुत अच्छा है।",
        "अनुवाद मॉडल अद्भुत हैं।",
    ] * 20
    
    print(f"Test sentences: {len(test_sentences_en)} per direction")
    
    # Benchmark both precisions (CPU supports float32 and int8, not float16)
    for compute_type in ["float32", "int8"]:
        print(f"\n{'='*80}")
        print(f"TESTING: {compute_type.upper()}")
        print(f"{'='*80}")
        
        # Load translator (CPU mode)
        print(f"\nLoading model (CPU, {compute_type})...")
        start = time.time()
        translator = ctranslate2.Translator(
            model_path,
            device="cpu",
            compute_type=compute_type,
            inter_threads=4,  # Adjust based on your CPU cores
            intra_threads=4
        )
        load_time = time.time() - start
        print(f"✓ Loaded in {load_time:.2f}s")
        
        # Benchmark EN→HI
        print(f"\n🔄 Translating EN→HI...")
        tokenizer.src_lang = "eng_Latn"
        times = []
        
        for sentence in tqdm(test_sentences_en, desc="EN→HI"):
            source_tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(sentence))
            start = time.time()
            results = translator.translate_batch(
                [source_tokens],
                target_prefix=[["hin_Deva"]],
                max_decoding_length=256,
                beam_size=5
            )
            times.append(time.time() - start)
        
        avg_time_en_hi = sum(times) / len(times) * 1000
        throughput_en_hi = 1 / (avg_time_en_hi / 1000)
        
        # Benchmark HI→EN
        print(f"\n🔄 Translating HI→EN...")
        tokenizer.src_lang = "hin_Deva"
        times = []
        
        for sentence in tqdm(test_sentences_hi, desc="HI→EN"):
            source_tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(sentence))
            start = time.time()
            results = translator.translate_batch(
                [source_tokens],
                target_prefix=[["eng_Latn"]],
                max_decoding_length=256,
                beam_size=5
            )
            times.append(time.time() - start)
        
        avg_time_hi_en = sum(times) / len(times) * 1000
        throughput_hi_en = 1 / (avg_time_hi_en / 1000)
        
        # Results
        print(f"\n{'='*80}")
        print(f"RESULTS: {compute_type.upper()}")
        print(f"{'='*80}")
        print(f"Load Time:            {load_time:.2f}s")
        print(f"\nEN→HI:")
        print(f"  Avg Time:           {avg_time_en_hi:.2f} ms/sentence")
        print(f"  Throughput:         {throughput_en_hi:.2f} sentences/sec")
        print(f"\nHI→EN:")
        print(f"  Avg Time:           {avg_time_hi_en:.2f} ms/sentence")
        print(f"  Throughput:         {throughput_hi_en:.2f} sentences/sec")
        print(f"{'='*80}\n")
        
        del translator

if __name__ == "__main__":
    cpu_benchmark()
