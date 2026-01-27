"""
API Routes Module
FastAPI endpoints for translation service
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from app.schemas.api_models import (
    TranslateRequest,
    TranslateResponse,
    HealthResponse,
    MetricsResponse,
    TranslationMetrics
)
from app.core.config import MAX_DOCUMENT_LENGTH_CHARS
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()

# These will be injected by main.py
translation_engine = None
chunker = None
metrics_collector = None
adapter_manager = None
model_info = None
translation_cache = None  # NEW


def set_dependencies(engine, chunk, metrics, adapter_mgr, mdl_info, cache=None):
    """Set dependencies from main app"""
    global translation_engine, chunker, metrics_collector, adapter_manager, model_info, translation_cache
    translation_engine = engine
    chunker = chunk
    metrics_collector = metrics
    adapter_manager = adapter_mgr
    model_info = mdl_info
    translation_cache = cache  # NEW


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns service status and model information
    """
    try:
        adapter_info = adapter_manager.get_adapter_info() if adapter_manager else {}
        
        return HealthResponse(
            status="ready" if translation_engine else "loading",
            model_loaded=translation_engine is not None,
            active_adapter=adapter_info.get("active_adapter"),
            device=model_info.get("device", "unknown"),
            adapters_available=list(adapter_info.get("adapters_loaded", {}).keys()),
            warmup_completed=True,
            using_adapters=adapter_info.get("using_adapters", False)
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Health check failed")


@router.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    Translate text (short translations)
    For texts up to 5000 characters
    """
    try:
        if not translation_engine:
            raise HTTPException(status_code=503, detail="Translation service not ready")
        
        # Prepare decoding params
        decoding_params = None
        if request.decoding_params:
            decoding_params = request.decoding_params.dict(exclude_none=True)
        
        # Translate
        result = translation_engine.translate(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            decoding_params=decoding_params
        )
        
        # Record metrics
        direction = f"{request.source_lang}_{request.target_lang}"
        if metrics_collector:
            metrics_collector.record_translation(result["metrics"], direction)
        
        # Return response
        return TranslateResponse(
            translated_text=result["translated_text"],
            source_lang=result["source_lang"],
            target_lang=result["target_lang"],
            metrics=TranslationMetrics(**result["metrics"])
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post("/translate/long")
async def translate_long(request: Request):
    """
    Translate long documents with progress streaming
    Uses Server-Sent Events (SSE) to stream progress
    """
    try:
        # Parse request body
        body = await request.json()
        text = body.get("text", "")
        source_lang = body.get("source_lang", "")
        target_lang = body.get("target_lang", "")
        decoding_params = body.get("decoding_params")
        
        # Validate
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(text) > MAX_DOCUMENT_LENGTH_CHARS:
            raise HTTPException(
                status_code=400,
                detail=f"Text exceeds maximum length of {MAX_DOCUMENT_LENGTH_CHARS} characters"
            )
        
        if source_lang not in ["en", "hi"] or target_lang not in ["en", "hi"]:
            raise HTTPException(status_code=400, detail="Invalid language codes")
        
        if source_lang == target_lang:
            raise HTTPException(status_code=400, detail="Source and target languages must be different")
        
        if not translation_engine or not chunker:
            raise HTTPException(status_code=503, detail="Translation service not ready")
        
        # Create streaming generator
        async def generate_translation():
            try:
                # Step 1: Chunking
                yield {
                    "event": "progress",
                    "data": json.dumps({
                        "status": "chunking",
                        "progress": 0,
                        "message": "Splitting text into chunks..."
                    })
                }
                
                chunks = chunker.chunk_text(text)
                total_chunks = len(chunks)
                
                logger.info(f"Split into {total_chunks} chunks for long translation")
                
                # Step 2: Translate each chunk
                translated_chunks = []
                
                for i, chunk in enumerate(chunks):
                    # Calculate progress
                    progress = int(((i + 1) / total_chunks) * 100)
                    
                    # Translate chunk
                    result = translation_engine.translate(
                        text=chunk["text"],
                        source_lang=source_lang,
                        target_lang=target_lang,
                        decoding_params=decoding_params
                    )
                    
                    translated_chunks.append(result["translated_text"])
                    
                    # Send progress update
                    yield {
                        "event": "progress",
                        "data": json.dumps({
                            "status": "translating",
                            "progress": progress,
                            "message": f"Translating chunk {i + 1}/{total_chunks}...",
                            "chunk_result": result["translated_text"]
                        })
                    }
                    
                    # Small delay to allow client to process
                    await asyncio.sleep(0.1)
                
                # Step 3: Combine results while preserving paragraph structure
                # Join chunks with space, but the chunks already contain paragraph breaks
                full_translation = " ".join(translated_chunks)
                
                # Send completion
                yield {
                    "event": "complete",
                    "data": json.dumps({
                        "translated_text": full_translation,
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                        "total_chunks": total_chunks
                    })
                }
                
                # Record metrics
                direction = f"{source_lang}_{target_lang}"
                if metrics_collector:
                    metrics_collector.record_translation(
                        {"inference_time_ms": 0, "adapter_switch_time_ms": 0},
                        direction
                    )
                
            except Exception as e:
                logger.error(f"Long translation failed: {str(e)}", exc_info=True)
                yield {
                    "event": "error",
                    "data": json.dumps({"error": str(e)})
                }
        
        return EventSourceResponse(generate_translation())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Long translation setup failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Get aggregated metrics
    Returns statistics about translations performed
    """
    try:
        if not metrics_collector:
            raise HTTPException(status_code=503, detail="Metrics not available")
        
        metrics = metrics_collector.get_metrics()
        
        # Add cache stats if available
        if translation_cache:
            metrics["cache_stats"] = translation_cache.get_stats()
        
        return MetricsResponse(**metrics)
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@router.post("/cache/clear")
async def clear_cache():
    """
    Clear translation cache
    Useful for testing and debugging
    """
    try:
        if not translation_cache:
            raise HTTPException(status_code=503, detail="Cache not available")
        
        translation_cache.clear()
        logger.info("Translation cache cleared via API")
        
        return {
            "message": "Cache cleared successfully",
            "stats": translation_cache.get_stats()
        }
        
    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear cache")

