# RunPod CTranslate2 Benchmarking Guide 🚀

To ensure a fair and optimized comparison, we have switched the entire benchmark suite to the **CTranslate2 (CT2)** engine. This benchmarks Float16, INT8, and INT4 variants under the same high-performance C++ backend.

## 📋 One-Time Setup on RunPod

After uploading the new scripts and files to RunPod, run:

```bash
# 1. Install new dependencies
pip install -U ctranslate2 transformers[sentencepiece] sacrebleu unbabel-comet

# 2. Convert NLLB model to CT2 Format (FP16 base)
# This only needs to be done once.
cd /workspace/scripts
python convert_to_ct2.py
```

## 🚀 Run the Benchmark

Now run the refactored benchmark script. It will automatically test `float16`, `int8_float16`, and `int4_float16` using the same engine.

```bash
# Start a tmux session
tmux new -s ct2_benchmark

# Run with logging
# Note: Provide the path to the directory created in the step above.
python benchmark_nllb_models.py --model_path ./nllb_ct2_fp16 2>&1 | tee benchmark_ct2_log.txt
```

## 🎯 What to Expect

### **1. NO MORE LOADING ERRORS**
CTranslate2 uses a custom format that bypasses the `torch.load` security restrictions and meta-tensor initialization issues.

### **2. Fair Comparison**
- **Float16**: The baseline performance of NLLB on CT2.
- **INT8**: CTranslate2's internal INT8 quantization.
- **INT4**: CTranslate2's internal INT4 quantization.

### **3. Accuracy**
Since we are using the same engine and tokenizer for all three, the BLEU and COMET score differences will be a **true reflection** of the quantization impact.

---

**Generated Files after Run:**
- `benchmark_results_ct2_<timestamp>.json`
- `benchmark_summary_ct2_<timestamp>.csv`
- `benchmark_ct2_log.txt`
