"""
Configuration module for NICO AI Translator
Centralized configuration for all application settings
"""

import os
import torch
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# BASE PATHS
# ============================================================================

BASE_DIR = Path(__file__).parent.parent.parent
ADAPTERS_DIR = BASE_DIR / "adapters"
LOGS_DIR = BASE_DIR / "logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Base model from HuggingFace
BASE_MODEL_NAME = "facebook/nllb-200-distilled-600M"

# HuggingFace token for model download (loaded from .env file)
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError(
        "HF_TOKEN not found in environment variables. "
        "Please create a .env file with your HuggingFace token. "
        "See .env.example for template."
    )

# Adapter paths (will be auto-detected from adapters folder)
ADAPTER_PATHS = {
    "en_hi": str(ADAPTERS_DIR / "nllb_lora_en_to_hi"),
    "hi_en": str(ADAPTERS_DIR / "nllb_lora_hi_to_en"),
}

# Device configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TORCH_DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

# ============================================================================
# LANGUAGE CONFIGURATION
# ============================================================================

# API language codes → NLLB tokenizer codes
LANG_CODE_MAP = {
    "en": "eng_Latn",
    "hi": "hin_Deva"
}

SUPPORTED_LANGUAGES = ["en", "hi"]

# ============================================================================
# DECODING PARAMETERS
# ============================================================================

DEFAULT_DECODING_PARAMS = {
    "max_length": 256,  # Reduced from 512 to 256for faster inference
    "num_beams": 2,     # Reduced from 5 to 2 for 2-3x speedup
    "early_stopping": True,
    "no_repeat_ngram_size": 3,
}

# Parameter constraints for validation
PARAM_CONSTRAINTS = {
    "max_length": (1, 1024),
    "num_beams": (1, 10),
    "temperature": (0.1, 2.0),
}

# ============================================================================
# INPUT VALIDATION
# ============================================================================

MAX_INPUT_LENGTH_CHARS = 5000  # For short translations
MAX_INPUT_LENGTH_TOKENS = 512

# ============================================================================
# CHUNKING CONFIGURATION (for long documents)
# ============================================================================

CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_SENTENCES = 1  # Number of sentences to overlap between chunks
MAX_DOCUMENT_LENGTH_CHARS = 50000

# Timeout for long translations
LONG_TRANSLATION_TIMEOUT_SECONDS = 600  # 10 minutes

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = "INFO"  # INFO, WARNING, ERROR
LOG_FORMAT = "json"  # json or text
LOG_FILE_PATH = str(LOGS_DIR / "translation.log")
MASK_INPUT_TEXT = False  # Set to True for privacy

# ============================================================================
# API CONFIGURATION
# ============================================================================

API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True  # Set to False in production

# CORS settings for local development
CORS_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# ============================================================================
# METRICS CONFIGURATION
# ============================================================================

# Track metrics in memory (resets on restart)
ENABLE_METRICS = True
