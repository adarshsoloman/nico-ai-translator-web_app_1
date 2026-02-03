# NLLB Model Benchmark Results - Complete Comparison

## Performance Summary Table

| Model | Type | Direction | Sentences | BLEU Score | COMET Score | Speed (s/s) | Avg Time (ms) | GPU Memory (MB) |
|-------|------|-----------|-----------|------------|-------------|-------------|---------------|-----------------|
| **NLLB Base** | Float16 | EN→HI | 3,009 | **3.60** | **0.4608** | N/A | N/A | ~2,500 |
| **INT8 Quantized** | 8-bit | EN→HI | 3,009 | **27.50** | **0.7821** | 1.25 | 800.13 | 20,973 |
| **INT4 Quantized** | 4-bit | EN→HI | 3,009 | **27.19** | **0.7770** | **2.26** | **441.67** | 21,559 |
| | | | | | | | | |
| **NLLB Base** | Float16 | HI→EN | 3,009 | **12.34** | **0.8536** | N/A | N/A | ~2,500 |
| **INT8 Quantized** | 8-bit | HI→EN | 3,009 | **35.91** | **0.8771** | 1.46 | 683.14 | 20,973 |
| **INT4 Quantized** | 4-bit | HI→EN | 3,009 | **34.34** | **0.8737** | **2.66** | **375.75** | 21,559 |

---

## Key Findings

### Quality Improvement (vs Base Model)

| Model | Direction | BLEU Improvement | COMET Improvement |
|-------|-----------|------------------|-------------------|
| INT8 | EN→HI | **+670%** (3.60 → 27.50) | **+70%** (0.4608 → 0.7821) |
| INT4 | EN→HI | **+655%** (3.60 → 27.19) | **+69%** (0.4608 → 0.7770) |
| INT8 | HI→EN | **+191%** (12.34 → 35.91) | **+2.8%** (0.8536 → 0.8771) |
| INT4 | HI→EN | **+178%** (12.34 → 34.34) | **+2.4%** (0.8536 → 0.8737) |

### INT4 vs INT8 Comparison

| Metric | INT8 | INT4 | Difference | Winner |
|--------|------|------|------------|--------|
| **EN→HI BLEU** | 27.50 | 27.19 | -0.31 (-1.1%) | INT8 |
| **EN→HI COMET** | 0.7821 | 0.7770 | -0.0051 (-0.65%) | INT8 |
| **HI→EN BLEU** | 35.91 | 34.34 | -1.57 (-4.4%) | INT8 |
| **HI→EN COMET** | 0.8771 | 0.8737 | -0.0034 (-0.39%) | INT8 |
| **EN→HI Speed** | 1.25 s/s | 2.26 s/s | **+81%** | **INT4** ✅ |
| **HI→EN Speed** | 1.46 s/s | 2.66 s/s | **+82%** | **INT4** ✅ |
| **Avg Time (EN→HI)** | 800.13 ms | 441.67 ms | **-45%** | **INT4** ✅ |
| **Avg Time (HI→EN)** | 683.14 ms | 375.75 ms | **-45%** | **INT4** ✅ |

---

## Recommendation

### ✅ **Choose INT4 Quantized Model**

**Rationale:**
- **7.5x better quality** than Base model (EN→HI)
- **1.8x faster** than INT8 quantized
- **Minimal quality loss** vs INT8 (< 1% COMET)
- **Production-ready** performance

**Trade-off Analysis:**
- For **1.8x speed gain**, lose only **0.65% quality** (EN→HI COMET)
- For **1.8x speed gain**, lose only **0.39% quality** (HI→EN COMET)

**Verdict:** Excellent speed/quality balance! 🎯

---

## Evaluation Details

- **Datasets:** FLORES-200 (1,013 sentences) + NTREX-128 (1,998 sentences)
- **Total Samples:** 3,009 sentences per direction
- **Metrics:** BLEU (industry standard) + COMET (state-of-the-art neural metric)
- **Hardware:** NVIDIA RTX 4090 (24 GB VRAM)
- **Evaluation Date:** January 31, 2026

---

**Model Selected for Production:** `Rewatiramans/nllb-200-distilled-600M-4bit`
