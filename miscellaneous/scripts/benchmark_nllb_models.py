#!/usr/bin/env python3
"""
NLLB Model Benchmarking Script (CTranslate2 Version)
===================================================

Compares three precision variants using the CTranslate2 engine:
1. Float16 (Baseline)
2. INT8 Quantized (int8_float16)
3. INT4 Quantized (int4_float16)

Benefits:
- Fair comparison (same engine for all)
- High performance (C++ backend)
- Bypasses PyTorch loading security/meta-tensor issues

Measures: Speed, Memory Usage, Throughput, Quality (BLEU, COMET)
"""

import torch
import time
import psutil
import GPUtil
import ctranslate2
import transformers
from typing import List, Dict, Optional
import pandas as pd
from tqdm import tqdm
import json
import os
from datetime import datetime
from sacrebleu.metrics import BLEU
from comet import download_model, load_from_checkpoint


class NLLBBenchmark:
    """Comprehensive benchmarking suite using CTranslate2 engine"""
    
    def __init__(self, model_path: str, eval_dataset_dir: str = "../eval_dataset"):
        """
        Initialize benchmark suite
        
        Args:
            model_path: Path to the converted CTranslate2 model (FP16)
            eval_dataset_dir: Path to directory containing FLORES and NTREX datasets
        """
        self.model_path = model_path
        self.results = []
        self.test_sentences, self.references = self.load_test_data(eval_dataset_dir)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize BLEU metric
        self.bleu = BLEU()
        
        # Initialize COMET model (will be loaded on first use)
        self.comet_model = None
        self.comet_model_path = None
        
        # Initialize Tokenizer
        print(f"📥 Loading tokenizer from {model_path}...")
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(model_path)
        
        print("=" * 80)
        print("NLLB MODEL BENCHMARKING SUITE (CTRANSLATE2)")
        print("=" * 80)
        print(f"CTranslate2 version: {ctranslate2.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"Test sentences EN→HI: {len(self.test_sentences['en_to_hi'])}")
        print(f"Test sentences HI→EN: {len(self.test_sentences['hi_to_en'])}")
        print("=" * 80)
        
    def load_test_data(self, eval_dataset_dir: str) -> tuple:
        """Load test sentences and references from FLORES and NTREX datasets"""
        print(f"\n📂 Loading evaluation datasets from {eval_dataset_dir}...")
        
        # Paths
        flores_eng_path = os.path.join(eval_dataset_dir, "FLORES", "flores_eng.txt")
        flores_hin_path = os.path.join(eval_dataset_dir, "FLORES", "flores_hin.txt")
        ntrex_eng_path = os.path.join(eval_dataset_dir, "NTREX", "newstest2019-src.eng.txt")
        ntrex_hin_path = os.path.join(eval_dataset_dir, "NTREX", "newstest2019-ref.hin.txt")
        
        sources = {"en_to_hi": [], "hi_to_en": []}
        references = {"en_to_hi": [], "hi_to_en": []}
        
        # Load FLORES
        if os.path.exists(flores_eng_path) and os.path.exists(flores_hin_path):
            with open(flores_eng_path, 'r', encoding='utf-8') as f:
                eng = [line.strip() for line in f if line.strip()]
            with open(flores_hin_path, 'r', encoding='utf-8') as f:
                hin = [line.strip() for line in f if line.strip()]
            sources["en_to_hi"].extend(eng)
            references["en_to_hi"].extend(hin)
            sources["hi_to_en"].extend(hin)
            references["hi_to_en"].extend(eng)
            print(f"   ✓ Loaded {len(eng)} FLORES pairs")
        
        # Load NTREX
        if os.path.exists(ntrex_eng_path) and os.path.exists(ntrex_hin_path):
            with open(ntrex_eng_path, 'r', encoding='utf-8') as f:
                eng = [line.strip() for line in f if line.strip()]
            with open(ntrex_hin_path, 'r', encoding='utf-8') as f:
                hin = [line.strip() for line in f if line.strip()]
            sources["en_to_hi"].extend(eng)
            references["en_to_hi"].extend(hin)
            sources["hi_to_en"].extend(hin)
            references["hi_to_en"].extend(eng)
            print(f"   ✓ Loaded {len(eng)} NTREX pairs")
        
        return sources, references
    
    def load_comet_model(self):
        """Load COMET model (lazy loading)"""
        if self.comet_model is None:
            print("\n📥 Loading COMET model...")
            self.comet_model_path = download_model("Unbabel/wmt22-comet-da")
            self.comet_model = load_from_checkpoint(self.comet_model_path)
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get GPU and RAM usage"""
        try:
            gpus = GPUtil.getGPUs()
            gpu_mem = gpus[0].memoryUsed if gpus else 0
        except:
            gpu_mem = 0
        ram = psutil.virtual_memory().used / (1024 ** 3)
        return {"gpu_memory_mb": gpu_mem, "ram_used_gb": ram}

    def load_translator(self, compute_type: str) -> tuple:
        """Load CTranslate2 translator with specific compute type"""
        print(f"\nLOADING: CTranslate2 ({compute_type})")
        start_time = time.time()
        
        translator = ctranslate2.Translator(
            self.model_path,
            device="cuda" if torch.cuda.is_available() else "cpu",
            compute_type=compute_type
        )
        
        load_time = time.time() - start_time
        memory = self.get_memory_usage()
        print(f"✓ Loaded in {load_time:.2f}s | GPU: {memory['gpu_memory_mb']}MB")
        return translator, load_time, memory

    def translate(self, translator, text: str, src_lang: str, tgt_lang: str) -> str:
        """Perform CT2 translation"""
        # Set source language
        self.tokenizer.src_lang = src_lang
        
        # Tokenize
        source = self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(text))
        
        # Translate
        results = translator.translate_batch(
            [source],
            target_prefix=[[tgt_lang]],
            max_decoding_length=256,
            beam_size=5
        )
        
        # Decode (skip target prefix)
        target = results[0].hypotheses[0]
        translation = self.tokenizer.decode(self.tokenizer.convert_tokens_to_ids(target), skip_special_tokens=True)
        return translation

    def calculate_bleu(self, hypotheses: List[str], references: List[str]) -> float:
        refs = [[ref] for ref in references]
        score = self.bleu.corpus_score(hypotheses, list(zip(*refs)))
        return round(score.score, 2)

    def calculate_comet(self, sources: List[str], hypotheses: List[str], references: List[str]) -> float:
        self.load_comet_model()
        data = [{"src": s, "mt": h, "ref": r} for s, h, r in zip(sources, hypotheses, references)]
        model_output = self.comet_model.predict(data, batch_size=8, gpus=1 if torch.cuda.is_available() else 0)
        return round(model_output.system_score, 4)

    def run_benchmark(self, translator, compute_type: str, direction: str) -> Dict:
        print(f"\nBENCHMARKING: {compute_type} | {direction.upper()}")
        
        if direction == "en_to_hi":
            src, tgt, test_set, ref_set = "eng_Latn", "hin_Deva", self.test_sentences["en_to_hi"], self.references["en_to_hi"]
        else:
            src, tgt, test_set, ref_set = "hin_Deva", "eng_Latn", self.test_sentences["hi_to_en"], self.references["hi_to_en"]
        
        # Warmup
        for _ in range(3):
            _ = self.translate(translator, test_set[0], src, tgt)
        
        hypotheses = []
        times = []
        
        for sentence in tqdm(test_set, desc="Translating"):
            start = time.time()
            translation = self.translate(translator, sentence, src, tgt)
            times.append(time.time() - start)
            hypotheses.append(translation)
            
        avg_time = sum(times) / len(times)
        throughput = 1 / avg_time
        
        print("📊 Calculating quality...")
        bleu = self.calculate_bleu(hypotheses, ref_set)
        comet = self.calculate_comet(test_set, hypotheses, ref_set)
        
        return {
            "model": f"CT2-{compute_type}",
            "direction": direction,
            "avg_time_ms": round(avg_time * 1000, 2),
            "throughput_sps": round(throughput, 2),
            "bleu_score": bleu,
            "comet_score": comet
        }

    def run_full_suite(self):
        # CTranslate2 4.5.0 supports: float16 and int8_float16
        # Note: int4_float16 requires CT2 5.0+, which breaks compatibility with transformers 4.46
        precisions = ["float16", "int8_float16"]
        
        for precision in precisions:
            translator, load_time, memory = self.load_translator(precision)
            for direction in ["en_to_hi", "hi_to_en"]:
                res = self.run_benchmark(translator, precision, direction)
                res["load_time_s"] = round(load_time, 2)
                res["gpu_memory_mb"] = memory["gpu_memory_mb"]
                res["ram_gb"] = round(memory["ram_used_gb"], 2)
                self.results.append(res)
            del translator
            torch.cuda.empty_cache()

    def save_report(self):
        df = pd.DataFrame(self.results)
        print("\n", df.to_string(index=False))
        
        json_file = f"benchmark_results_ct2_{self.timestamp}.json"
        csv_file = f"benchmark_summary_ct2_{self.timestamp}.csv"
        
        with open(json_file, "w") as f:
            json.dump(self.results, f, indent=2)
        df.to_csv(csv_file, index=False)
        print(f"\n✅ Results saved to:\n- {json_file}\n- {csv_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True, help="Path to CT2 model directory")
    args = parser.parse_args()
    
    benchmark = NLLBBenchmark(model_path=args.model_path)
    benchmark.run_full_suite()
    benchmark.save_report()

if __name__ == "__main__":
    main()
