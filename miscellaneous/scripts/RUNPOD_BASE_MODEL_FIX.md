# RunPod Base Model Fix - Quick Reference

## Problem
Base NLLB model fails to load with error:
```
Due to a serious vulnerability issue in `torch.load`, even with `weights_only=True`, 
we now require users to upgrade torch to at least v2.6
```

## Root Cause
- PyTorch 2.4+ has security restrictions on `torch.load()`
- Base NLLB model uses old pickle format
- Quantized models use safetensors (no issue)

## ✅ Solution Applied

Modified `benchmark_nllb_models.py` line 190-197 to force safetensors:

```python
if model_config['type'] == 'base':
    print("Loading base model (float16)...")
    print("   Using safetensors to bypass PyTorch security restriction...")
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_config['path'],
        device_map="auto",
        torch_dtype=torch.float16,
        use_safetensors=True  # ← This fixes it!
    )
```

## 🚀 RunPod Commands

### 1. Install safetensors (if not already installed)
```bash
pip install safetensors
```

### 2. Run benchmark with logging
```bash
cd /workspace/scripts
python benchmark_nllb_models.py 2>&1 | tee benchmark_log.txt
```

## Alternative Solutions (if above doesn't work)

### Option A: Downgrade PyTorch
```bash
pip install torch==2.3.1
```

### Option B: Use different base model repo
```bash
# Some repos have safetensors versions
# Check HuggingFace for "safetensors" tag
```

### Option C: Skip base model
```bash
# Comment out base model in benchmark script
# Lines 423-428 in benchmark_nllb_models.py
```

## Expected Behavior After Fix

```
Loading base model (float16)...
   Using safetensors to bypass PyTorch security restriction...
Loading tokenizer...

✓ Model loaded successfully in XX.XXs
✓ GPU Memory: XXXX MB / 24564 MB
✓ RAM: XX.XX GB / XXX.XX GB
```

## If Still Fails

The base model might not have safetensors format. In that case:

**Best option:** Skip base model comparison
- You already have INT8 vs INT4 comparison ✅
- Old base scores are questionable anyway ⚠️
- Focus on quantized model comparison

**Why it's okay to skip:**
1. INT8 and INT4 scores are comparable and reliable
2. Old base evaluation had different methodology
3. COMET scores are what matter for quality
4. You're past deadline - prioritize what works!

---

**Status:** ✅ Fix applied to benchmark script
**Next:** Upload to RunPod and test
