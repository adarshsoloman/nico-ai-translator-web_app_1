"""
API Models (Pydantic Schemas)
Request and response models for API endpoints
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List
from app.core.config import SUPPORTED_LANGUAGES, MAX_INPUT_LENGTH_CHARS


class DecodingParams(BaseModel):
    """Optional decoding parameters for translation"""
    max_length: Optional[int] = Field(None, ge=1, le=1024)
    num_beams: Optional[int] = Field(None, ge=1, le=10)
    temperature: Optional[float] = Field(None, ge=0.1, le=2.0)
    early_stopping: Optional[bool] = None


class TranslateRequest(BaseModel):
    """Request model for translation"""
    text: str = Field(..., min_length=1, max_length=MAX_INPUT_LENGTH_CHARS)
    source_lang: str = Field(..., pattern="^(en|hi)$")
    target_lang: str = Field(..., pattern="^(en|hi)$")
    decoding_params: Optional[DecodingParams] = None
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v
    
    @validator('target_lang')
    def languages_different(cls, v, values):
        if 'source_lang' in values and v == values['source_lang']:
            raise ValueError('Source and target languages must be different')
        return v


class TranslationMetrics(BaseModel):
    """Metrics for a translation"""
    inference_time_ms: float
    adapter_switch_time_ms: float
    total_time_ms: float
    input_tokens: int
    output_tokens: int
    tokens_per_second: float
    from_cache: bool = False  # Indicates if result was from cache


class TranslateResponse(BaseModel):
    """Response model for translation"""
    translated_text: str
    source_lang: str
    target_lang: str
    metrics: TranslationMetrics


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    model_loaded: bool
    active_adapter: Optional[str]
    device: str
    adapters_available: List[str]
    warmup_completed: bool
    using_adapters: bool


class CacheStats(BaseModel):
    """Cache statistics"""
    size: int
    max_size: int
    hits: int
    misses: int
    hit_rate_percent: float
    total_requests: int


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint"""
    total_requests: int
    avg_inference_time_ms: float
    avg_adapter_switch_time_ms: float
    requests_by_direction: Dict[str, int]
    total_tokens_processed: int
    uptime_seconds: int
    cache_stats: Optional[CacheStats] = None  # Cache performance metrics
