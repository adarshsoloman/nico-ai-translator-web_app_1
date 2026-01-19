# NICO AI Translator

**Fast. Local. Offline.** 

A local, offline translation web application using NLLB-200 base model with swappable LoRA adapters for bidirectional Hindi ↔ English translation.

## Features

✨ **Bidirectional Translation**: English ↔ Hindi  
🚀 **Fast Adapter Switching**: LoRA adapters for efficient translation direction changes  
📊 **Real-time Metrics**: Track translation time, tokens, and performance  
📄 **Long Document Support**: Translate up to 50,000 characters with progress tracking  
🎨 **Modern UI**: Clean, minimal interface with word/character counting  
⚡ **Fully Offline**: No internet required after setup  

---

## Prerequisites

- **Python**: 3.9 or higher
- **GPU**: NVIDIA GPU with 4GB+ VRAM (recommended) or CPU
- **RAM**: 16GB recommended
- **HuggingFace Account**: For downloading NLLB model (free)

---

## Installation

### 1. Clone or Navigate to Project Directory

```bash
cd d:\ADARSH\15_Freelance\NICO_AI\Phase_1\2_web_app\4_nico-ai-phase1-nllb_base+lora_adapters
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
```

### 3. Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Create a `.env` file in the project root with your HuggingFace token:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your token
# Get your token from: https://huggingface.co/settings/tokens
```

Your `.env` file should look like:
```
HF_TOKEN=your_actual_huggingface_token_here
```

**Important**: Never commit the `.env` file to Git! It's already in `.gitignore`.

### 6. Download NLTK Data (for text chunking)

```powershell
python -c "import nltk; nltk.download('punkt')"
```

---

## Project Structure

```
.
├── app/
│   ├── core/
│   │   ├── config.py              # Configuration
│   │   ├── model_loader.py        # NLLB model loader
│   │   ├── adapter_manager.py     # LoRA adapter management
│   │   ├── translator.py          # Translation engine
│   │   ├── chunker.py             # Text chunking
│   │   └── metrics.py             # Metrics collection
│   ├── api/
│   │   └── routes.py              # FastAPI endpoints
│   ├── logging/
│   │   └── logger.py              # Structured logging
│   ├── schemas/
│   │   └── api_models.py          # Pydantic models
│   ├── utils/
│   │   └── timing.py              # Timing utilities
│   ├── static/
│   │   ├── index.html             # Frontend UI
│   │   ├── style.css              # Styles
│   │   └── script.js              # Frontend logic
│   └── main.py                    # FastAPI app
├── adapters/
│   ├── nllb_lora_en_to_hi/        # English → Hindi adapter
│   └── nllb_lora_hi_to_en/        # Hindi → English adapter
├── logs/                          # Application logs
├── requirements.txt               # Python dependencies
├── PRD.txt                        # Product requirements
└── README.md                      # This file
```

---

## Running the Application

### Start the Server

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Run the application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access the Application

Open your browser and navigate to:

```
http://localhost:8000
```

---

## Usage

### Short Translations (< 1000 characters)

1. Enter text in the **Input Text** area
2. Select source and target languages
3. Click **Translate**
4. View translation in the **Translation** area
5. Click **Copy Output** to copy the result

### Long Translations (> 1000 characters)

1. Paste long text (up to 50,000 characters)
2. Click **Translate**
3. Watch the **progress bar** as chunks are translated
4. View incremental results in real-time
5. Final translation appears when complete

### Keyboard Shortcuts

- **Ctrl + Enter**: Translate
- **Ctrl + K**: Clear all

---

## API Endpoints

### Health Check

```bash
GET /health
```

Returns service status, model info, and adapter status.

### Short Translation

```bash
POST /translate
Content-Type: application/json

{
  "text": "Hello, how are you?",
  "source_lang": "en",
  "target_lang": "hi"
}
```

### Long Translation (Streaming)

```bash
POST /translate/long
Content-Type: application/json

{
  "text": "...very long text...",
  "source_lang": "en",
  "target_lang": "hi"
}
```

Returns Server-Sent Events (SSE) stream with progress updates.

### Metrics

```bash
GET /metrics
```

Returns aggregated translation statistics.

---

## Configuration

Edit `app/core/config.py` to customize:

- **Model paths**: Change base model or adapter locations
- **Decoding parameters**: Adjust beam search, max length, etc.
- **Input limits**: Modify max character/token limits
- **Chunking settings**: Configure chunk size and overlap
- **Logging**: Change log level and format

---

## Troubleshooting

### Model Loading Issues

**Problem**: Model fails to load  
**Solution**: 
- Check HuggingFace token in `config.py`
- Ensure sufficient disk space (~3GB)
- Verify internet connection for first-time download

### Out of Memory (OOM)

**Problem**: CUDA out of memory error  
**Solution**:
- Reduce `max_length` in decoding params
- Use CPU instead of GPU (slower but works)
- Close other GPU-intensive applications

### Adapter Not Found

**Problem**: Adapters fail to load  
**Solution**:
- Verify adapter paths in `config.py`
- Check that adapter folders exist in `adapters/`
- Application will fall back to base model if adapters missing

### Slow Translation

**Problem**: Translation takes too long  
**Solution**:
- Ensure GPU is being used (check logs)
- Reduce `num_beams` in decoding params
- Use shorter input text

---

## Performance

### Expected Latency

- **Short text (< 100 words)**: 1-3 seconds
- **Medium text (100-500 words)**: 3-10 seconds
- **Long text (500-1000 words)**: 10-30 seconds
- **Very long text (1000+ words)**: 30 seconds - 5 minutes

### Memory Usage

- **Base Model**: ~2.4 GB VRAM
- **LoRA Adapters**: ~60 MB total
- **System RAM**: ~4-6 GB

---

## Development

### Adding New Languages

1. Train LoRA adapters for new language pair
2. Add adapter paths to `config.py`
3. Update `LANG_CODE_MAP` with NLLB language codes
4. Update frontend language dropdowns

### Extending the API

1. Add new endpoint in `app/api/routes.py`
2. Create Pydantic schema in `app/schemas/api_models.py`
3. Update frontend to call new endpoint

---

## License

This project is for internal use only.

---

## Credits

- **NLLB Model**: Meta AI (facebook/nllb-200-distilled-600M)
- **PEFT Library**: Hugging Face
- **Framework**: FastAPI, Transformers

---

## Support

For issues or questions, contact the development team.

---

**Built with ❤️ for NICO AI**
