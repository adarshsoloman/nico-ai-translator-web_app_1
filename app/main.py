"""
Main Application Module
FastAPI application initialization and startup
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.logging.logger import setup_logging
from app.core.model_loader import ModelLoader
from app.core.adapter_manager import AdapterManager
from app.core.translator import TranslationEngine
from app.core.chunker import TextChunker
from app.core.metrics import MetricsCollector
from app.core.cache import TranslationCache  # NEW
from app.api import routes
from app.core.config import CORS_ORIGINS

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global instances
model_loader = None
adapter_manager = None
translation_engine = None
chunker = None
metrics_collector = None
translation_cache = None  # NEW


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("=" * 60)
    logger.info("NICO AI Translator - Starting Up")
    logger.info("=" * 60)
    
    global model_loader, adapter_manager, translation_engine, chunker, metrics_collector, translation_cache
    
    try:
        # Initialize metrics collector
        logger.info("Initializing metrics collector...")
        metrics_collector = MetricsCollector()
        
        # Load model
        logger.info("Loading NLLB base model...")
        model_loader = ModelLoader()
        model, tokenizer = model_loader.load_model()
        logger.info("✓ Model loaded successfully")
        
        # Initialize adapter manager
        logger.info("Initializing adapter manager...")
        adapter_manager = AdapterManager(model, tokenizer)
        adapters_loaded = adapter_manager.load_adapters()
        
        if adapters_loaded:
            logger.info("✓ LoRA adapters loaded successfully")
        else:
            logger.warning("⚠ Using base model only (adapters not loaded)")
        
        # Initialize chunker
        logger.info("Initializing text chunker...")
        chunker = TextChunker(tokenizer)
        logger.info("✓ Text chunker ready")
        
        # Initialize translation cache
        logger.info("Initializing translation cache...")
        translation_cache = TranslationCache(max_size=500)
        logger.info("✓ Translation cache ready (max_size=500)")
        
        # Initialize translation engine with cache
        logger.info("Initializing translation engine...")
        translation_engine = TranslationEngine(model, tokenizer, adapter_manager, cache=translation_cache)
        logger.info("✓ Translation engine ready")
        
        # Set dependencies in routes
        model_info = model_loader.get_model_info()
        routes.set_dependencies(
            translation_engine,
            chunker,
            metrics_collector,
            adapter_manager,
            model_info,
            translation_cache  # NEW
        )
        
        logger.info("=" * 60)
        logger.info("✓ Application startup complete!")
        logger.info("=" * 60)
        logger.info(f"Device: {model_info['device']}")
        logger.info(f"Using adapters: {adapter_manager.get_adapter_info().get('using_adapters', False)}")
        logger.info("Ready to accept requests")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    logger.info("Goodbye!")


# Create FastAPI app
app = FastAPI(
    title="NICO AI Translator",
    description="Local offline translation service using NLLB + LoRA adapters",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router)

# Mount static files (frontend)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    from app.core.config import API_HOST, API_PORT, API_RELOAD
    
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD
    )
