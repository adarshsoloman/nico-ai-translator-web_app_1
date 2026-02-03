# Quantized Model Migration Guide

## Overview

This guide explains how to migrate from the original NLLB-200-distilled-600M base model to Rewat's quantized versions in the NICO AI translator web app.

## Available Quantized Models

Rewat has created two quantized versions:

| Model | Size | HuggingFace Path |
|-------|------|------------------|
| 8-bit Quantized | 879 MB | `Rewatiramans/nllb-200-distilled-600M-8bit` |
| 4-bit Quantized | 724 MB | `Rewatiramans/nllb-200-distilled-600M-4bit` |

**Original Model**: `facebook/nllb-200-distilled-600M` (~1.2 GB)

## Key Considerations

### 1. **Loading Method Changes**

Quantized models require special loading configuration using `BitsAndBytesConfig`:

```python
from transformers import AutoModelForSeq2SeqLM, BitsAndBytesConfig

# For 8-bit model
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0
)

# For 4-bit model
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

# Load the model
model = AutoModelForSeq2SeqLM.from_pretrained(
    "Rewatiramans/nllb-200-distilled-600M-8bit",  # or 4-bit version
    quantization_config=quantization_config,
    device_map="auto"
)
```

### 2. **LoRA Adapter Compatibility** ⚠️

**CRITICAL**: Your existing LoRA adapters were trained on the **full-precision base model**. There are compatibility concerns:

- **Weight Format Mismatch**: Quantized models use different weight representations (int8/int4 vs float16/float32)
- **Adapter Expectations**: LoRA adapters expect specific tensor formats from the base model
- **Potential Issues**: Adapters may not load, or may load but produce incorrect translations

### 3. **Migration Strategies**

#### **Strategy A: Quantized Base Only (No Adapters)**

**Pros:**
- Simple drop-in replacement
- Smaller memory footprint (879 MB or 724 MB vs ~1.2 GB)
- Faster inference
- Immediate deployment

**Cons:**
- Lose fine-tuning improvements from your LoRA adapters
- Translation quality reverts to base model performance

**Implementation:**
```python
# Simply change the model path and add quantization config
MODEL_NAME = "Rewatiramans/nllb-200-distilled-600M-8bit"
# Remove LoRA adapter loading code
```

#### **Strategy B: Test Adapter Compatibility**

**Pros:**
- Might work with existing adapters (worth testing)
- Keep fine-tuning benefits if compatible

**Cons:**
- Likely to fail or produce poor results
- Time spent testing may not yield results

**Implementation:**
```python
# Load quantized base
model = AutoModelForSeq2SeqLM.from_pretrained(
    "Rewatiramans/nllb-200-distilled-600M-8bit",
    quantization_config=quantization_config,
    device_map="auto"
)

# Try loading existing LoRA adapters
from peft import PeftModel
model = PeftModel.from_pretrained(model, "path/to/lora/adapters")
```

#### **Strategy C: Re-train LoRA on Quantized Base (QLoRA)**

**Pros:**
- Best of both worlds: small model + fine-tuning benefits
- Proper compatibility guaranteed
- Industry-standard approach (QLoRA)

**Cons:**
- Requires re-training (time + compute on RunPod)
- Need to set up QLoRA training pipeline

**Implementation:**
- Use your existing training data
- Train new LoRA adapters on the quantized base model
- This is called **QLoRA** (Quantized LoRA)

## Recommended Migration Path

### Phase 1: Quick Test (Strategy A)
1. Create a copy of your current project folder
2. Modify model loading to use quantized base (no adapters)
3. Test translation quality
4. Compare with original base + LoRA setup

### Phase 2: Compatibility Test (Strategy B)
1. Try loading existing LoRA adapters on quantized base
2. Run test translations
3. If it works well, great! If not, proceed to Phase 3

### Phase 3: QLoRA Training (Strategy C - if needed)
1. Set up QLoRA training on RunPod
2. Use your existing training dataset
3. Train new adapters on quantized base
4. Deploy and test

## Code Changes Required

### Current Setup (Assumed)
```python
# Load base model
model = AutoModelForSeq2SeqLM.from_pretrained(
    "facebook/nllb-200-distilled-600M",
    device_map="auto"
)

# Load LoRA adapters
from peft import PeftModel
model = PeftModel.from_pretrained(model, "path/to/lora/adapters")
```

### New Setup (8-bit, No Adapters)
```python
from transformers import AutoModelForSeq2SeqLM, BitsAndBytesConfig
import torch

# Configure 8-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0
)

# Load quantized model
model = AutoModelForSeq2SeqLM.from_pretrained(
    "Rewatiramans/nllb-200-distilled-600M-8bit",
    quantization_config=quantization_config,
    device_map="auto"
)

# No LoRA adapter loading
```

### New Setup (4-bit, No Adapters)
```python
from transformers import AutoModelForSeq2SeqLM, BitsAndBytesConfig
import torch

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)

# Load quantized model
model = AutoModelForSeq2SeqLM.from_pretrained(
    "Rewatiramans/nllb-200-distilled-600M-4bit",
    quantization_config=quantization_config,
    device_map="auto"
)

# No LoRA adapter loading
```

## Dependencies

Ensure you have the required libraries:

```bash
pip install bitsandbytes>=0.41.0
pip install accelerate>=0.20.0
pip install transformers>=4.30.0
```

## Testing Checklist

After migration, test the following:

- [ ] Model loads without errors
- [ ] English → Hindi translation works
- [ ] Hindi → English translation works
- [ ] Translation quality is acceptable
- [ ] Inference speed (should be faster)
- [ ] Memory usage (should be lower)
- [ ] API endpoints respond correctly
- [ ] Streaming functionality works
- [ ] Docker container builds and runs

## Performance Expectations

| Metric | Original + LoRA | 8-bit Quantized | 4-bit Quantized |
|--------|----------------|-----------------|-----------------|
| Model Size | ~1.2 GB | 879 MB | 724 MB |
| VRAM Usage | Higher | Medium | Lower |
| Inference Speed | Baseline | Faster | Fastest |
| Translation Quality | Fine-tuned | Base model | Base model |

## Rollback Plan

If quantized models don't meet quality requirements:

1. Keep original folder as backup
2. Revert to original base model + LoRA adapters
3. Consider QLoRA training for future optimization

## Next Steps

1. **Create project copy**: Duplicate current folder for testing
2. **Choose model**: Start with 8-bit (better quality than 4-bit)
3. **Modify code**: Update model loading in `app/main.py` or relevant files
4. **Test thoroughly**: Run through testing checklist
5. **Benchmark**: Use the benchmarking guide to compare all options
6. **Decide**: Based on quality vs. performance trade-offs

## Questions to Answer

Before finalizing migration:

1. Is the translation quality acceptable without LoRA adapters?
2. How much faster is inference with quantized models?
3. Is the quality loss worth the speed/memory gains?
4. Should we invest time in QLoRA training?

## References

- [BitsAndBytes Documentation](https://github.com/TimDettmers/bitsandbytes)
- [QLoRA Paper](https://arxiv.org/abs/2305.14314)
- [HuggingFace Quantization Guide](https://huggingface.co/docs/transformers/main_classes/quantization)
