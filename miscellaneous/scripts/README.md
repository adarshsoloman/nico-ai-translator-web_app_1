# NLLB Model Benchmarking Scripts

Comprehensive benchmarking suite for comparing NLLB-200-distilled-600M model variants on RunPod.

**Measures:**
- ⏱️ **Speed**: Translation time, throughput
- 💾 **Memory**: GPU VRAM, RAM usage
- 🎯 **Quality**: BLEU and COMET scores

**Models Tested:**
1. **Base Model** (facebook/nllb-200-distilled-600M) - 1.2 GB
2. **INT8 Quantized** (Rewatiramans/nllb-200-distilled-600M-8bit) - 879 MB
3. **INT4 Quantized** (Rewatiramans/nllb-200-distilled-600M-4bit) - 724 MB

## 📊 Evaluation Datasets

This benchmark uses **professional evaluation datasets**:

- **FLORES-200**: 1,013 parallel sentences (English ↔ Hindi)
- **NTREX-128**: 1,998 parallel sentences (English ↔ Hindi)

**Total**: ~3,000 sentences per direction for robust evaluation!

These datasets are located in `../eval_dataset/`:
```
eval_dataset/
├── FLORES/
│   ├── flores_eng.txt (1,013 sentences)
│   └── flores_hin.txt (1,013 sentences)
└── NTREX/
    ├── newstest2019-src.eng.txt (1,998 sentences)
    └── newstest2019-ref.hin.txt (1,998 sentences)
```

The benchmark script automatically loads and combines both datasets.

## RunPod Setup

### 1. Choose GPU

Recommended GPUs for consistent benchmarking:
- **RTX 4090** (24 GB VRAM) - Best value
- **RTX A6000** (48 GB VRAM) - More headroom
- **RTX 3090** (24 GB VRAM) - Budget option

### 2. Docker Template

Use: `runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel` or latest PyTorch 2.x template

### 3. Initial Setup

```bash
# Update system
apt-get update && apt-get install -y nano tmux git zip

# Navigate to workspace
cd /workspace

# Upload this scripts folder or clone your repo
# git clone <your-repo-url>
# cd <repo>/scripts

# Install dependencies
pip install -r requirements.txt
```

## Running the Benchmark

### Quick Start

```bash
# Start tmux session (recommended for long-running tasks)
tmux new -s nllb_benchmark

# Run the benchmark
python benchmark_nllb_models.py

# Detach from tmux: Ctrl+B, then D
# Reattach later: tmux attach -t nllb_benchmark
```

### ⏱️ Expected Runtime

With **~3,000 sentences per direction** + **BLEU + COMET scoring**:

- **Base Model**: ~60-90 minutes per direction
- **INT8 Model**: ~45-75 minutes per direction  
- **INT4 Model**: ~35-60 minutes per direction

**Total estimated time**: **6-8 hours** for all 3 models × 2 directions

> 💡 **Note**: COMET scoring adds ~3-4 hours but provides state-of-the-art quality assessment!
> 🎯 **Worth it**: You'll have publication-quality benchmarking results!

### What Gets Tested

For each model:
- ✅ Model loading time
- ✅ GPU memory usage (VRAM)
- ✅ RAM usage
- ✅ Translation speed (avg time per sentence)
- ✅ Throughput (sentences/second)
- ✅ Both directions: English→Hindi and Hindi→English
- ✅ Sample translations for quality review

## Output Files

After completion, you'll get:

```
benchmark_results_YYYYMMDD_HHMMSS.json    # Detailed results with all translations
benchmark_summary_YYYYMMDD_HHMMSS.csv     # Summary table for easy comparison
```

## Analyzing Results

```bash
# Run analysis script
python analyze_results.py benchmark_results_YYYYMMDD_HHMMSS.json

# This will generate:
# - Comparison charts (PNG images)
# - Detailed analysis report (TXT)
```

## Downloading Results

```bash
# Zip all results
zip -r benchmark_results.zip benchmark_*.json benchmark_*.csv *.png *.txt

# Download via RunPod file browser
# Or use rclone if configured for Google Drive
```

## Interpreting Results

### Key Metrics

| Metric | What to Look For |
|--------|------------------|
| **Avg Time (ms)** | Lower is better - faster translations |
| **Throughput (s/s)** | Higher is better - more sentences/second |
| **GPU Memory (MB)** | Lower is better - less VRAM needed |
| **Load Time (s)** | Lower is better - faster startup |

### Expected Performance

```
Speed:     INT4 > INT8 > Base
Memory:    INT4 < INT8 < Base
Quality:   Base ≥ INT8 > INT4 (manual review needed)
```

### Decision Matrix

| Priority | Choose |
|----------|--------|
| Best Quality | Base or INT8 |
| Best Speed | INT4 |
| Balanced | INT8 |
| Lowest Memory | INT4 |

## Next Steps

After benchmarking:

1. **Review Results**: Check CSV summary and sample translations
2. **Choose Model**: Based on speed/quality trade-offs
3. **QLoRA Training**: Train LoRA adapters on chosen quantized model
4. **Integration**: Update web app with quantized base + new LoRA adapters

## Troubleshooting

### Out of Memory (OOM)

```bash
# Reduce test set size in test_data.json
# Or test models one at a time by commenting out in benchmark_nllb_models.py
```

### Slow Model Download

```bash
# Models download from HuggingFace on first run
# Subsequent runs use cached models (~/.cache/huggingface/)
# Be patient on first run!
```

### Import Errors

```bash
pip install --upgrade transformers accelerate bitsandbytes torch
```

## Cost Estimation

RunPod costs (approximate):
- RTX 4090: ~$0.69/hour × 0.75 hours = **~$0.52 per benchmark**
- RTX A6000: ~$0.79/hour × 0.75 hours = **~$0.59 per benchmark**

💡 **Tip**: Stop the pod immediately after downloading results to save costs!

## Support

If you encounter issues:
1. Check tmux logs: `tmux attach -t nllb_benchmark`
2. Review error messages in terminal
3. Ensure all dependencies are installed
4. Verify GPU is available: `nvidia-smi`
