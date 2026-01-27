# 🚀 NICO AI Translator - Quick Start Guide

**For: Senior Team Members**  
**Setup Time: ~10 minutes**

---

## Prerequisites

Before you start, make sure you have:

1. ✅ **Docker Desktop** installed
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: Run `docker --version` in terminal

2. ✅ **HuggingFace Account** (free)
   - Sign up: https://huggingface.co/join
   - Get token: https://huggingface.co/settings/tokens
   - Create a token with "Read" access

---

## 🎯 Quick Start (3 Steps)

### Step 1: Extract & Navigate
```bash
# Extract the project folder and navigate to it
cd path/to/4_nico-ai-phase1-nllb_base+lora_adapters
```

### Step 2: Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your HuggingFace token
# Replace 'your_huggingface_token_here' with your actual token
```

**Your `.env` file should look like:**
```
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Start the Application
```bash
# Start with Docker Compose (one command!)
docker-compose up -d
```

**That's it!** 🎉

---

## 📱 Access the Application

Once the container is running (wait ~2-3 minutes for first-time model download):

- **Web Interface:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 🔍 Verify It's Working

### Check Container Status
```bash
docker ps
```
You should see `nico-ai-translator` with status `Up` and `healthy`

### Check Logs
```bash
docker-compose logs -f
```
Look for:
```
✓ Application startup complete!
Device: cpu
Ready to accept requests
```

### Test the API
```bash
curl http://localhost:8000/health
```
Should return:
```json
{
  "status": "ready",
  "model_loaded": true,
  "device": "cpu",
  "using_adapters": true
}
```

---

## 🧪 Test Translation

### Via Web Interface
1. Open http://localhost:8000
2. Enter text: "Hello, how are you?"
3. Select: English → Hindi
4. Click "Translate"
5. See result: "नमस्ते, आप कैसे हैं?"

### Via API (curl)
```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "source_lang": "en",
    "target_lang": "hi"
  }'
```

### Via API Docs (Interactive)
1. Go to http://localhost:8000/docs
2. Click on `POST /translate`
3. Click "Try it out"
4. Enter sample data
5. Click "Execute"

---

## 🛠️ Common Commands

```bash
# View logs (live)
docker-compose logs -f

# Stop the application
docker-compose down

# Restart the application
docker-compose restart

# Rebuild and restart (after code changes)
docker-compose up -d --build

# Check container status
docker ps

# Remove everything (including volumes)
docker-compose down -v
```

---

## ⚠️ Troubleshooting

### Container exits immediately
**Check logs:**
```bash
docker-compose logs
```
**Common issue:** Missing or invalid HF_TOKEN in `.env`

### Port 8000 already in use
**Solution:** Edit `docker-compose.yml` and change port:
```yaml
ports:
  - "8080:8000"  # Use 8080 instead
```
Then access at http://localhost:8080

### "Out of memory" error
**Solution:** Increase Docker memory limit
- Docker Desktop → Settings → Resources → Memory
- Set to at least 8GB

### Model download is slow
**This is normal!** First-time setup downloads ~2.4GB NLLB model
- Takes 5-10 minutes depending on internet speed
- Subsequent starts are instant (model is cached)

---

## 📊 What to Expect

### First Startup
- **Time:** 5-10 minutes (model download)
- **Disk Space:** ~5GB
- **Memory:** ~4-6GB RAM

### Subsequent Startups
- **Time:** 30-60 seconds
- **Memory:** ~4-6GB RAM

### Translation Performance
- **Short text (<100 words):** 1-3 seconds
- **Medium text (100-500 words):** 3-10 seconds
- **Long text (500+ words):** 10-30 seconds

---

## 🎓 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check service status |
| `/translate` | POST | Translate short text (<5000 chars) |
| `/translate/long` | POST | Translate long documents (up to 50K chars) |
| `/metrics` | GET | Get translation statistics |

**Full documentation:** http://localhost:8000/docs

---

## 📁 Project Structure

```
.
├── app/                    # Application code
│   ├── api/               # FastAPI routes
│   ├── core/              # Core logic (model, translator, etc.)
│   ├── static/            # Frontend UI
│   └── main.py            # Entry point
├── adapters/              # LoRA adapters
│   ├── nllb_lora_en_to_hi/
│   └── nllb_lora_hi_to_en/
├── Dockerfile             # Docker build instructions
├── docker-compose.yml     # Docker orchestration
├── requirements.txt       # Python dependencies
└── DOCKER_GUIDE.md       # Detailed Docker guide
```

---

## 🆘 Need Help?

1. **Check logs:** `docker-compose logs -f`
2. **Check health:** `curl http://localhost:8000/health`
3. **Read detailed guide:** See `DOCKER_GUIDE.md`
4. **Contact developer:** [Your contact info]

---

## 🔒 Security Notes

- ✅ The `.env` file is gitignored (never commit it!)
- ✅ HuggingFace token is only used to download the model
- ✅ Application runs fully offline after initial setup
- ✅ No data is sent to external servers

---

## 📝 Notes

- **Device:** Currently uses CPU (slower but works everywhere)
- **GPU Support:** Can be enabled with NVIDIA GPU + CUDA setup
- **Offline:** Works completely offline after first-time model download
- **Languages:** Currently supports English ↔ Hindi only

---

**Built with ❤️ for NICO AI**

For detailed technical documentation, see `TECHNICAL_OVERVIEW.md`
