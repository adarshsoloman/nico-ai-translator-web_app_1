# RunPod Benchmarking Guide: NLLB Model Variants

## Overview

This guide provides a comprehensive benchmarking plan to compare three NLLB model variants on RunPod:

1. **Original Base Model**: `facebook/nllb-200-distilled-600M` (~1.2 GB)
2. **8-bit Quantized**: `Rewatiramans/nllb-200-distilled-600M-8bit` (879 MB)
3. **4-bit Quantized**: `Rewatiramans/nllb-200-distilled-600M-4bit` (724 MB)

## Objectives

- Compare translation quality across all three models
- Measure inference speed and throughput
- Analyze memory usage (VRAM + RAM)
- Evaluate cost-effectiveness for deployment
- Determine optimal model for production use

## RunPod Setup

### Recommended GPU

For fair comparison, use a consistent GPU across all tests:

- **RTX 4090** (24 GB VRAM) - Recommended
- **RTX A6000** (48 GB VRAM) - Alternative
- **RTX 3090** (24 GB VRAM) - Budget option

### Docker Template

Use a PyTorch-based template:
- `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel`
- Or latest stable PyTorch 2.x template

### Initial Setup Commands

```bash
# Update system
apt-get update && apt-get install -y nano tmux git zip

# Install Python dependencies
pip install --upgrade pip
pip install transformers>=4.30.0
pip install torch>=2.0.0
pip install accelerate>=0.20.0
pip install bitsandbytes>=0.41.0
pip install sentencepiece
pip install sacrebleu
pip install pandas
pip install tqdm
pip install psutil
pip install GPUtil

# Clone or upload your benchmarking script
```

## Benchmarking Script

Create a comprehensive benchmarking script: `benchmark_nllb_models.py`

```python
import torch
import time
import psutil
import GPUtil
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, BitsAndBytesConfig
from typing import List, Dict
import pandas as pd
from tqdm import tqdm
import json

class NLLBBenchmark:
    def __init__(self):
        self.results = []
        self.test_sentences = self.load_test_data()
        
    def load_test_data(self) -> Dict[str, List[str]]:
        """Load test sentences for both directions"""
        return {
            "en_to_hi": [
                "Hello, how are you?",
                "Machine translation has improved significantly over the years.",
                "The quick brown fox jumps over the lazy dog.",
                "Artificial intelligence is transforming the world.",
                "I would like to book a table for two people at 7 PM.",
                # Add more test sentences
            ],
            "hi_to_en": [
                "नमस्ते, आप कैसे हैं?",
                "मशीन अनुवाद पिछले कुछ वर्षों में काफी सुधर गया है।",
                "कृत्रिम बुद्धिमत्ता दुनिया को बदल रही है।",
                "मुझे शाम 7 बजे दो लोगों के लिए एक टेबल बुक करनी है।",
                # Add more test sentences
            ]
        }
    
    def get_memory_usage(self):
        """Get current memory usage"""
        # GPU Memory
        gpus = GPUtil.getGPUs()
        gpu_memory = gpus[0].memoryUsed if gpus else 0
        
        # RAM
        ram = psutil.virtual_memory()
        ram_used = ram.used / (1024 ** 3)  # Convert to GB
        
        return {
            "gpu_memory_mb": gpu_memory,
            "ram_gb": round(ram_used, 2)
        }
    
    def load_model(self, model_config: Dict):
        """Load model based on configuration"""
        print(f"\n{'='*60}")
        print(f"Loading: {model_config['name']}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        if model_config['type'] == 'base':
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_config['path'],
                device_map="auto",
                torch_dtype=torch.float16
            )
        elif model_config['type'] == '8bit':
            quant_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0
            )
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_config['path'],
                quantization_config=quant_config,
                device_map="auto"
            )
        elif model_config['type'] == '4bit':
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True
            )
            model = AutoModelForSeq2SeqLM.from_pretrained(
                model_config['path'],
                quantization_config=quant_config,
                device_map="auto"
            )
        
        tokenizer = AutoTokenizer.from_pretrained(model_config['path'])
        
        load_time = time.time() - start_time
        memory = self.get_memory_usage()
        
        print(f"✓ Loaded in {load_time:.2f}s")
        print(f"✓ GPU Memory: {memory['gpu_memory_mb']} MB")
        print(f"✓ RAM: {memory['ram_gb']} GB")
        
        return model, tokenizer, load_time, memory
    
    def benchmark_translation(self, model, tokenizer, direction: str, model_name: str):
        """Benchmark translation for a specific direction"""
        print(f"\nBenchmarking {direction}...")
        
        # Set language codes
        if direction == "en_to_hi":
            src_lang = "eng_Latn"
            tgt_lang = "hin_Deva"
            test_set = self.test_sentences["en_to_hi"]
        else:
            src_lang = "hin_Deva"
            tgt_lang = "eng_Latn"
            test_set = self.test_sentences["hi_to_en"]
        
        translations = []
        times = []
        
        # Warmup
        print("Warming up...")
        for _ in range(3):
            _ = self.translate(model, tokenizer, test_set[0], src_lang, tgt_lang)
        
        # Actual benchmarking
        print("Running benchmark...")
        for sentence in tqdm(test_set):
            start = time.time()
            translation = self.translate(model, tokenizer, sentence, src_lang, tgt_lang)
            elapsed = time.time() - start
            
            translations.append({
                "source": sentence,
                "translation": translation,
                "time_ms": elapsed * 1000
            })
            times.append(elapsed)
        
        # Calculate metrics
        avg_time = sum(times) / len(times)
        throughput = 1 / avg_time  # sentences per second
        
        result = {
            "model": model_name,
            "direction": direction,
            "avg_time_ms": round(avg_time * 1000, 2),
            "throughput_sps": round(throughput, 2),
            "translations": translations
        }
        
        print(f"✓ Avg time: {result['avg_time_ms']} ms")
        print(f"✓ Throughput: {result['throughput_sps']} sentences/sec")
        
        return result
    
    def translate(self, model, tokenizer, text: str, src_lang: str, tgt_lang: str) -> str:
        """Perform single translation"""
        tokenizer.src_lang = src_lang
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            generated_tokens = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_lang),
                max_length=256,
                num_beams=5
            )
        
        translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        return translation
    
    def run_full_benchmark(self):
        """Run complete benchmark across all models"""
        models = [
            {
                "name": "Original Base Model",
                "path": "facebook/nllb-200-distilled-600M",
                "type": "base"
            },
            {
                "name": "8-bit Quantized",
                "path": "Rewatiramans/nllb-200-distilled-600M-8bit",
                "type": "8bit"
            },
            {
                "name": "4-bit Quantized",
                "path": "Rewatiramans/nllb-200-distilled-600M-4bit",
                "type": "4bit"
            }
        ]
        
        all_results = []
        
        for model_config in models:
            # Load model
            model, tokenizer, load_time, memory = self.load_model(model_config)
            
            # Benchmark both directions
            for direction in ["en_to_hi", "hi_to_en"]:
                result = self.benchmark_translation(
                    model, tokenizer, direction, model_config['name']
                )
                result['load_time_s'] = load_time
                result['gpu_memory_mb'] = memory['gpu_memory_mb']
                result['ram_gb'] = memory['ram_gb']
                all_results.append(result)
            
            # Clean up
            del model
            del tokenizer
            torch.cuda.empty_cache()
            time.sleep(5)  # Cool down
        
        self.results = all_results
        return all_results
    
    def generate_report(self):
        """Generate comprehensive benchmark report"""
        print("\n" + "="*80)
        print("BENCHMARK RESULTS SUMMARY")
        print("="*80)
        
        # Create comparison DataFrame
        summary_data = []
        for result in self.results:
            summary_data.append({
                "Model": result['model'],
                "Direction": result['direction'],
                "Avg Time (ms)": result['avg_time_ms'],
                "Throughput (s/s)": result['throughput_sps'],
                "GPU Memory (MB)": result['gpu_memory_mb'],
                "RAM (GB)": result['ram_gb'],
                "Load Time (s)": round(result['load_time_s'], 2)
            })
        
        df = pd.DataFrame(summary_data)
        print("\n", df.to_string(index=False))
        
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON
        with open(f"benchmark_results_{timestamp}.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Save summary CSV
        df.to_csv(f"benchmark_summary_{timestamp}.csv", index=False)
        
        print(f"\n✓ Results saved:")
        print(f"  - benchmark_results_{timestamp}.json")
        print(f"  - benchmark_summary_{timestamp}.csv")
        
        return df

# Run benchmark
if __name__ == "__main__":
    print("Starting NLLB Model Benchmark...")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    benchmark = NLLBBenchmark()
    benchmark.run_full_benchmark()
    benchmark.generate_report()
    
    print("\n✓ Benchmark complete!")
```

## Running the Benchmark

### Step-by-Step Process

```bash
# 1. Start tmux session (recommended)
tmux new -s nllb_benchmark

# 2. Run the benchmark
python benchmark_nllb_models.py

# 3. Detach from tmux if needed (Ctrl+B, then D)
# Reattach later with: tmux attach -t nllb_benchmark
```

### Expected Runtime

- Each model: ~10-15 minutes (depending on test set size)
- Total benchmark: ~30-45 minutes for all three models

## Metrics to Collect

### Performance Metrics

| Metric | Description | Unit |
|--------|-------------|------|
| Load Time | Time to load model into memory | seconds |
| Inference Time | Average time per translation | milliseconds |
| Throughput | Translations per second | sentences/sec |
| GPU Memory | VRAM usage during inference | MB |
| RAM Usage | System memory usage | GB |

### Quality Metrics (Manual Review)

For each model, manually review translations for:
- **Accuracy**: Correctness of translation
- **Fluency**: Natural language flow
- **Completeness**: No missing information
- **Context**: Proper handling of context

## Test Dataset Recommendations

### Diverse Test Cases

Include sentences that test:

1. **Simple greetings**: "Hello", "Good morning"
2. **Complex sentences**: Long sentences with multiple clauses
3. **Technical terms**: Domain-specific vocabulary
4. **Idiomatic expressions**: Phrases that don't translate literally
5. **Numbers and dates**: "I'll meet you on January 15th at 3:30 PM"
6. **Questions**: Various question types
7. **Commands**: Imperative sentences
8. **Formal vs. informal**: Different registers

### Sample Test Set Size

- **Quick test**: 20-30 sentences per direction
- **Comprehensive test**: 100+ sentences per direction
- **Production validation**: 500+ sentences with reference translations

## Analysis Framework

### Speed Comparison

```
Expected Results:
- 4-bit: Fastest (1.5-2x faster than base)
- 8-bit: Fast (1.2-1.5x faster than base)
- Base: Baseline speed
```

### Memory Comparison

```
Expected Results:
- 4-bit: Lowest VRAM (~724 MB)
- 8-bit: Medium VRAM (~879 MB)
- Base: Highest VRAM (~1.2 GB)
```

### Quality Comparison

```
Expected Results:
- Base: Best quality (if using LoRA adapters)
- 8-bit: Minimal quality loss (<5%)
- 4-bit: Noticeable quality loss (5-15%)
```

## Cost Analysis

Calculate RunPod costs:

```
Cost per hour × Benchmark duration = Total cost

Example (RTX 4090):
$0.69/hour × 0.75 hours = ~$0.52 per full benchmark
```

## Decision Matrix

After benchmarking, use this matrix to decide:

| Priority | Recommended Model |
|----------|-------------------|
| **Best Quality** | Original Base (+ LoRA if available) |
| **Best Speed** | 4-bit Quantized |
| **Balanced** | 8-bit Quantized |
| **Lowest Memory** | 4-bit Quantized |
| **Production (Quality-Critical)** | 8-bit or Base |
| **Production (Speed-Critical)** | 4-bit |

## Post-Benchmark Actions

### 1. Download Results

```bash
# Zip all results
zip -r benchmark_results.zip benchmark_*.json benchmark_*.csv

# Download using RunPod file browser or:
# Use rclone if configured for Google Drive
```

### 2. Analysis

- Compare CSV summaries in Excel/Google Sheets
- Review JSON for detailed translation examples
- Calculate quality scores manually or with BLEU/METEOR

### 3. Documentation

Document findings:
- Which model performed best overall?
- What are the trade-offs?
- Recommendation for production deployment
- Any unexpected results?

## Troubleshooting

### Common Issues

**Out of Memory (OOM)**
```bash
# Reduce batch size or test set size
# Use smaller GPU
# Test models one at a time
```

**Slow Loading**
```bash
# Check internet connection
# Models download from HuggingFace on first run
# Subsequent runs use cached models
```

**Import Errors**
```bash
# Reinstall dependencies
pip install --upgrade transformers accelerate bitsandbytes
```

## Advanced Benchmarking (Optional)

### BLEU Score Calculation

If you have reference translations:

```python
from sacrebleu import corpus_bleu

references = [["reference translation 1", "reference translation 2", ...]]
hypotheses = ["model translation 1", "model translation 2", ...]

bleu = corpus_bleu(hypotheses, references)
print(f"BLEU Score: {bleu.score}")
```

### Batch Processing

Test different batch sizes:
- Batch size 1 (single sentence)
- Batch size 4
- Batch size 8
- Batch size 16

### Long Document Testing

Test with longer texts:
- Paragraphs (100-200 words)
- Articles (500+ words)

## Deliverables

After completing the benchmark, you should have:

1. ✅ JSON file with detailed results
2. ✅ CSV summary for easy comparison
3. ✅ Performance metrics for all three models
4. ✅ Quality assessment notes
5. ✅ Recommendation document
6. ✅ Cost analysis

## Next Steps

Based on benchmark results:

1. **Choose optimal model** for your use case
2. **Update web app** with selected model
3. **Document decision** and rationale
4. **Plan deployment** strategy
5. **Consider QLoRA training** if needed

## References

- [NLLB Model Card](https://huggingface.co/facebook/nllb-200-distilled-600M)
- [BitsAndBytes Documentation](https://github.com/TimDettmers/bitsandbytes)
- [Transformers Quantization](https://huggingface.co/docs/transformers/main_classes/quantization)
- [RunPod Documentation](https://docs.runpod.io/)
