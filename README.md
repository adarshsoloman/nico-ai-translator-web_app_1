# NICO AI Translator

**Fast. Local. Offline.** 

A high-performance local translation web application using CTranslate2 INT8 quantized NLLB-200 model with LoRA adapter support for bidirectional Hindi ↔ English translation.

## ✨ Features

🚀 **Blazing Fast**: CTranslate2 INT8 inference engine (5-7x faster than PyTorch)  
✨ **Bidirectional Translation**: English ↔ Hindi  
🎯 **Domain Adapters**: LoRA adapters for specialized translations (experimental)  
📊 **Real-time Metrics**: Track translation time, tokens, and performance  
📄 **Long Document Support**: Translate up to 50,000 characters with progress tracking  
⚡ **Fully Offline**: No internet required after setup  
� **Memory Efficient**: INT8 quantization (42% smaller than FP16)  
🎨 **Modern UI**: Clean, minimal interface with dark mode support  

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.9 or higher
- **GPU**: NVIDIA GPU with 2GB+ VRAM (recommended) or CPU with AVX-512
- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: ~2GB for models and application
- **HuggingFace Account**: For downloading models (free)

### Installation

```powershell
# 1. Clone repository
git clone <your-repo-url>
cd nico-ai-phase1-nllb_quantized+lora_adapters_streaming

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment variables
cp .env.example .env
# Edit .env and add your HuggingFace token

# 6. Download NLTK data
python -c "import nltk; nltk.download('punkt')"

# 7. Download INT8 model from HuggingFace
python miscellaneous/download_int8_model.py

# 8. Run the application
python -m app.main
```

### 📥 Downloading the INT8 Model

The INT8 quantized model is **not included in the repository** to keep it lightweight. Download it from HuggingFace:

**Option 1: Automatic Download (Recommended)**
```bash
python miscellaneous/download_int8_model.py
```
This will download the model to `./nllb_ct2_int8/` automatically.

**Option 2: Manual Download**
1. Visit: [Rewatiramans/nllb-200-distilled-600M-8bit](https://huggingface.co/Rewatiramans/nllb-200-distilled-600M-8bit)
2. Download all files to `./nllb_ct2_int8/` directory
3. Ensure your `.env` file has a valid `HF_TOKEN`

**Model Details:**
- Size: 879MB (INT8 quantized)
- Source: Rewatiramans on HuggingFace
- Based on: Meta's NLLB-200-distilled-600M

### Access the Application

Open your browser: **http://localhost:8000**

---

## 🏗️ Architecture

### Core Technology Stack

- **Inference Engine**: CTranslate2 4.5.0 with INT8 quantization
- **Base Model**: NLLB-200-distilled-600M (INT8 quantized, 879MB)
- **Backend**: FastAPI for RESTful API and SSE streaming
- **Frontend**: Vanilla JavaScript with modern ES6+
- **Adapter System**: PEFT LoRA adapters (experimental support)

### Performance Metrics

**GPU (NVIDIA RTX 3050 / 4090):**
- Translation Speed: 150-200ms per sentence
- Throughput: 6-7 sentences/second
- VRAM Usage: 1.2GB (INT8)
- Quality: BLEU 27.5, COMET 0.78 (EN→HI)

**CPU (Modern x86 with AVX-512):**
- Translation Speed: 800-1200ms per sentence  
- Throughput: 1-2 sentences/second
- Memory Usage: 2GB RAM
- Quality: Identical to GPU

---

## 📂 Project Structure

```
.
├── app/
│   ├── core/
│   │   ├── model_loader.py        # CT2 model loader with INT8
│   │   ├── adapter_manager.py     # LoRA adapter management
│   │   ├── translator.py          # CT2 translation engine
│   │   ├── chunker.py             # Text chunking for long docs
│   │   ├── metrics.py             # Performance metrics
│   │   ├── cache.py               # Translation caching
│   │   └── config.py              # Application configuration
│   ├── api/
│   │   └── routes.py              # FastAPI endpoints
│   ├── logging/
│   │   └── logger.py              # Structured logging
│   ├── static/
│   │   ├── index.html             # Main translation UI
│   │   ├── dataset-builder.html   # Custom training dataset builder
│   │   └── vendor/                # External libraries
│   └── main.py                    # FastAPI application
├── adapters/                      # LoRA adapter checkpoints
│   ├── nllb_lora_en_to_hi/       # EN→HI adapter
│   └── nllb_lora_hi_to_en/       # HI→EN adapter
├── nllb_ct2_int8/                # INT8 quantized CT2 model
├── docs/                          # Documentation
│   ├── QUICK_START.md
│   ├── DOCKER_GUIDE.md
│   ├── OFFLINE_UI_SETUP.md
│   ├── QUANTIZED_MODEL_MIGRATION.md
│   └── RUNPOD_BENCHMARKING_GUIDE.md
├── miscellaneous/                 # Archived scripts & benchmarks
│   ├── benchmark_results/
│   ├── scripts/
│   └── download_int8_model.py
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🎯 Usage

### Web Interface

1. **Open**: Navigate to http://localhost:8000
2. **Select languages**: Choose EN→HI or HI→EN
3. **Enter text**: Type or paste text (up to 50,000 chars)
4. **Translate**: Click "Translate" or press Ctrl+Enter
5. **View results**: Translation appears with metrics

### Keyboard Shortcuts

- `Ctrl + Enter`: Translate
- `Ctrl + K`: Clear all fields

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Translation
```bash
POST /api/translate
Content-Type: application/json

{
  "text": "Hello, how are you?",
  "source_lang": "en",
  "target_lang": "hi"
}
```

#### Long Translation (Streaming)
```bash
POST /api/translate/long
Content-Type: application/json

{
  "text": "...very long text...",
  "source_lang": "en",
  "target_lang": "hi"
}
```

Returns Server-Sent Events (SSE) with progress updates.

#### Metrics
```bash
GET /api/metrics
```

---

## ⚙️ Configuration

Edit `app/core/config.py` to customize:

- **Model paths**: CT2 model directory
- **Compute type**: INT8 (default), FP32, FP16
- **Device**: CUDA (GPU) or CPU
- **Decoding parameters**: Beam size, max length, penalties
- **Input limits**: Max chars, max tokens
- **Chunking settings**: Chunk size, overlap
- **Logging**: Level, format, rotation

---

## 🐳 Docker Deployment

```bash
# 1. Build image
docker-compose build

# 2. Start container
docker-compose up -d

# 3. Access app
http://localhost:8000
```

See [docs/DOCKER_GUIDE.md](docs/DOCKER_GUIDE.md) for details.

---

## 📊 Model Performance

### CT2-INT8 vs PyTorch FP16

| Metric | PyTorch FP16 | CT2-INT8 | Improvement |
|:-------|:-------------|:---------|:------------|
| **Inference Time** | 800ms | 154ms | **5.2x faster** |
| **Throughput** | 1.25 s/s | 6.47 s/s | **5.2x higher** |
| **VRAM Usage** | 2.4GB | 1.2GB | **50% less** |
| **Model Size** | 2.0GB | 879MB | **56% smaller** |
| **BLEU Score** | 27.50 | 27.46 | Identical |
| **COMET Score** | 0.7821 | 0.7818 | Identical |

**Conclusion**: CT2-INT8 is significantly faster with identical quality!

---

## 🔧 Troubleshooting

### Model Loading Issues

**Problem**: Model fails to load  
**Solution**:
- Check `.env` file has valid HF_TOKEN
- Run `python miscellaneous/download_int8_model.py`
- Verify `nllb_ct2_int8/` directory exists

### Out of Memory

**Problem**: CUDA out of memory  
**Solution**:
- Use CPU mode: Set `DEVICE=cpu` in `.env`
- Reduce chunk size in `config.py`
- Close other GPU applications

### Slow Translation

**Problem**: Translation too slow  
**Solution**:
- Verify GPU is detected (check startup logs)
- Reduce `num_beams` in decoding params
- Ensure INT8 compute type is used

### Adapter Issues

**Problem**: Adapters not working  
**Solution**:
- Adapters are currently **experimental** with CT2
- Base model is always used for now
- See `adapter_manager.py` for details

---

## 🚧 Current Limitations

- **LoRA Adapters**: Domain-specific adapters are disabled in CT2 mode
  - Using base NLLB-INT8 model for all translations
  - Hybrid or merged adapter approaches under development
- **Streaming**: Limited to 10KB chunks for optimal performance
- **Languages**: Currently supports Hindi ↔ English only
  - NLLB-200 supports 200 languages, can be extended

---

## 🛠️ Development

### Adding New Features

1. **Hybrid Adapters**: Enable PyTorch adapters alongside CT2 base
2. **Merged Adapters**: Convert LoRA-merged models to CT2
3. **Multi-language**: Add language pairs from NLLB-200
4. **Batch API**: Support multiple translations in one request

### Testing

```bash
# Run application in development mode
python -m app.main

# Test translation
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "source_lang": "en", "target_lang": "hi"}'
```

---

## 📖 Documentation

- **[QUICK_START.md](docs/QUICK_START.md)** - Beginner setup guide
- **[DOCKER_GUIDE.md](docs/DOCKER_GUIDE.md)** - Docker deployment
- **[QUANTIZED_MODEL_MIGRATION.md](docs/QUANTIZED_MODEL_MIGRATION.md)** - CT2 migration guide
- **[RUNPOD_BENCHMARKING_GUIDE.md](docs/RUNPOD_BENCHMARKING_GUIDE.md)** - Performance testing
- **[OFFLINE_UI_SETUP.md](docs/OFFLINE_UI_SETUP.md)** - Offline configuration

---

## 📜 License

This project is for internal use only.

---

## 🙏 Credits

- **Base Model**: Meta AI (NLLB-200-distilled-600M)
- **INT8 Model**: Rewatiramans/nllb-200-distilled-600M-8bit
- **Inference Engine**: CTranslate2 by OpenNMT
- **Framework**: FastAPI, Transformers, PEFT
- **UI Design**: Custom minimal dark mode interface

---

## 📞 Support

For issues or questions, contact the development team.

---

**Built with ❤️ for NICO AI**

*Powered by CTranslate2 INT8 Quantization*
