# 🐳 Docker Deployment Guide - NICO AI Translator

This guide explains how to run the NICO AI Translator using Docker.

---

## Prerequisites

- **Docker Desktop** installed ([Download here](https://www.docker.com/products/docker-desktop))
- **HuggingFace Token** (get from https://huggingface.co/settings/tokens)

---

## Quick Start (For Your Senior)

### Option 1: Using Docker Compose (Recommended ⭐)

1. **Clone/Extract the project**
   ```bash
   cd path/to/4_nico-ai-phase1-nllb_base+lora_adapters
   ```

2. **Create `.env` file with HuggingFace token**
   ```bash
   # Copy the example
   cp .env.example .env
   
   # Edit .env and add your token
   # HF_TOKEN=your_actual_token_here
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **View logs**
   ```bash
   docker-compose logs -f
   ```

6. **Stop the application**
   ```bash
   docker-compose down
   ```

---

### Option 2: Using Docker CLI

1. **Build the image**
   ```bash
   docker build -t nico-ai-translator .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name nico-translator \
     -p 8000:8000 \
     -e HF_TOKEN=your_huggingface_token \
     -v $(pwd)/logs:/app/logs \
     nico-ai-translator
   ```

3. **Check status**
   ```bash
   docker ps
   docker logs nico-translator
   ```

4. **Stop the container**
   ```bash
   docker stop nico-translator
   docker rm nico-translator
   ```

---

## What Happens During Build?

1. ✅ Downloads Python 3.10 base image
2. ✅ Installs system dependencies (curl)
3. ✅ Installs Python packages from `requirements.txt`
4. ✅ Downloads NLTK punkt data
5. ✅ Copies application code and LoRA adapters
6. ✅ Sets up health checks

**Build time:** ~5-10 minutes (first time only)  
**Image size:** ~4-5 GB (includes NLLB model cache)

---

## Troubleshooting

### Build fails with "HF_TOKEN not found"
**Solution:** Make sure `.env` file exists with valid `HF_TOKEN`

### Container exits immediately
**Solution:** Check logs with `docker logs nico-translator`

### Port 8000 already in use
**Solution:** Change port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"  # Use 8080 instead
```

### Out of memory during model loading
**Solution:** Increase Docker memory limit in Docker Desktop settings (recommend 8GB+)

---

## Health Check

The container includes automatic health checks:
- Runs every 30 seconds
- Checks `/health` endpoint
- Marks container as unhealthy if 3 consecutive failures

Check health status:
```bash
docker ps  # Look at STATUS column
```

---

## Persistence

- **Logs:** Mounted to `./logs` directory (persists across restarts)
- **Model cache:** Stored inside container (re-downloads if container is removed)

---

## Production Deployment

For production, consider:

1. **Remove `--reload` flag** in Dockerfile CMD
2. **Use specific Python version** (not `latest`)
3. **Add resource limits** in docker-compose.yml:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '4'
         memory: 8G
   ```
4. **Use secrets** for HF_TOKEN instead of .env file
5. **Set up reverse proxy** (nginx) for HTTPS

---

## GPU Support (Optional)

To use NVIDIA GPU in Docker:

1. Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

2. Update `docker-compose.yml`:
   ```yaml
   services:
     nico-translator:
       deploy:
         resources:
           reservations:
             devices:
               - driver: nvidia
                 count: 1
                 capabilities: [gpu]
   ```

3. Update Dockerfile to use CUDA-enabled PyTorch:
   ```dockerfile
   RUN pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```

---

## Commands Cheat Sheet

```bash
# Build
docker-compose build

# Start (detached)
docker-compose up -d

# Start (with logs)
docker-compose up

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# Remove everything (including volumes)
docker-compose down -v
```

---

## Support

For issues, check:
1. Container logs: `docker-compose logs`
2. Health status: `docker ps`
3. API health: `curl http://localhost:8000/health`

---

**Built with ❤️ for NICO AI**
