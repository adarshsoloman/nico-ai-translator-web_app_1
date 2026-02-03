# CTranslate2 Setup Guide - Version Compatibility Notes

## ⚠️ Critical Version Requirements

After extensive troubleshooting on RunPod (Feb 2026), the following version combination is **required** for successful NLLB model conversion to CTranslate2:

### Working Versions
```bash
torch==2.6.0          # Required for PyTorch security patch (CVE-2025-32434)
torchvision==0.21.0   # Must match Torch 2.6.0 for operator compatibility
transformers==4.46.0  # Compatible with CT2 and Torch 2.6+
ctranslate2==4.5.0    # Last version with stable NLLB/M2M100 support
```

## Why These Specific Versions?

### Torch 2.6.0+
- **Required** to bypass `torch.load` security vulnerability
- The security lock prevents loading `.bin` checkpoint files
- Using `use_safetensors=True` bypasses this restriction

### Torchvision 0.21.0
- Must be upgraded alongside Torch
- Older versions cause: `RuntimeError: operator torchvision::nms does not exist`
- Torchvision has C++ extensions compiled for specific PyTorch versions

### Transformers 4.46.0
- Newer versions (4.47+) changed tokenizer backend internals
- Breaks CTranslate2's `additional_special_tokens` access
- This version works with both Torch 2.6+ and CT2 4.5.0

### CTranslate2 4.5.0
- Handles updated M2M100 model structure from transformers 4.46
- Later versions may have breaking changes with current transformers

## Installation Commands (RunPod)

### Fresh Environment Setup
```bash
# Install specific versions
pip install torch==2.6.0 torchvision==0.21.0
pip install transformers==4.46.0 ctranslate2==4.5.0

# Install additional dependencies
pip install sentencepiece sacrebleu unbabel-comet
```

### If You Already Have Conflicting Versions
```bash
# Force reinstall all critical packages
pip install --force-reinstall torch==2.6.0 torchvision==0.21.0 transformers==4.46.0 ctranslate2==4.5.0
```

## Conversion Process

Once the environment is set up correctly:

```bash
cd /workspace/scripts
python convert_to_ct2.py
```

**Expected Output:**
- Downloads NLLB-200-distilled-600M model (with safetensors)
- Converts to CTranslate2 format
- Creates `nllb_ct2_fp16/` directory

## Troubleshooting

### Error: "torch.load vulnerability"
- **Solution:** Upgrade to `torch>=2.6.0`

### Error: "operator torchvision::nms does not exist"
- **Solution:** Upgrade `torchvision` to match your Torch version

### Error: "'M2M100Encoder' object has no attribute 'embed_scale'"
- **Solution:** Update `ctranslate2` to 4.5.0+

### Error: "TokenizersBackend has no attribute additional_special_tokens"
- **Solution:** Downgrade `transformers` to 4.46.0

## What Worked (Chronological Log)

1. ❌ Initial attempt with default versions → `torch.load` security error
2. ❌ Upgraded to Torch 2.6.0 → `torchvision::nms` operator error  
3. ❌ Upgraded torchvision → `M2M100ForConditionalGeneration` import error
4. ❌ Force-reinstalled ctranslate2 → `embed_scale` attribute error
5. ❌ Upgraded ctranslate2 → `additional_special_tokens` error
6. ✅ **Installed transformers==4.46.0 + ctranslate2==4.5.0** → **SUCCESS!**

## Date & Environment
- **Date Tested:** February 2, 2026
- **Platform:** RunPod (Ubuntu, Python 3.11)
- **GPU:** RTX 4090
- **Model:** facebook/nllb-200-distilled-600M

---

**Maintained by:** NICO AI Translation Project  
**Last Updated:** 2026-02-02
