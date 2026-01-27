# Translation Result Caching - Implementation Plan

## Overview

Implement an LRU (Least Recently Used) cache for translation results to significantly speed up repeated translations, particularly beneficial for government documents with repetitive content.

## Goal

- **Primary**: Cache translation results to avoid redundant GPU/CPU computation
- **Secondary**: Track cache performance metrics (hit rate, size)
- **Tertiary**: Provide cache management capabilities

---

## Proposed Changes

### Core Components

#### [NEW] `app/core/cache.py`

**Translation Result Cache Implementation**:

```python
from functools import lru_cache
from collections import OrderedDict
import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime

class TranslationCache:
    """LRU cache for translation results"""
    
    def __init__(self, max_size: int = 500):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self.created_at = datetime.now()
        
    def _generate_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key from translation parameters"""
        combined = f"{text}|{source_lang}|{target_lang}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached translation if exists"""
        key = self._generate_key(text, source_lang, target_lang)
        
        if key in self.cache:
            self.hits += 1
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, text: str, source_lang: str, target_lang: str, result: Dict[str, Any]):
        """Store translation result in cache"""
        key = self._generate_key(text, source_lang, target_lang)
        
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            self.cache.popitem(last=False)
        
        self.cache[key] = result
        self.cache.move_to_end(key)
    
    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests
        }
```

---

#### [MODIFY] `app/core/translator.py`

**Integrate cache into translation flow**:

Changes at lines ~24-30 (constructor):
```python
def __init__(self, model, tokenizer, adapter_manager, cache=None):
    self.model = model
    self.tokenizer = tokenizer
    self.adapter_manager = adapter_manager
    self.device = DEVICE
    self.cache = cache  # Add cache reference
```

Changes at lines ~76-85 (translate method):
```python
def translate(self, text: str, source_lang: str, target_lang: str, decoding_params: dict = None):
    """Translate with caching support"""
    start_time = time.time()
    
    try:
        # Validate input
        is_valid, error_msg = self.validate_input(text, source_lang, target_lang)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Check cache first
        if self.cache:
            cached_result = self.cache.get(text, source_lang, target_lang)
            if cached_result:
                logger.info(f"Cache hit for translation")
                # Add cache hit indicator to metrics
                cached_result["metrics"]["from_cache"] = True
                return cached_result
        
        # ... rest of translation logic ...
        
        # Store in cache before returning
        if self.cache:
            self.cache.set(text, source_lang, target_lang, result)
        
        result["metrics"]["from_cache"] = False
        return result
```

---

#### [MODIFY] `app/schemas/api_models.py`

**Add cache metrics to response models**:

```python
class TranslationMetrics(BaseModel):
    inference_time_ms: float
    adapter_switch_time_ms: float
    total_time_ms: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    tokens_per_second: Optional[float] = None
    from_cache: bool = False  # NEW: Indicates if result from cache

class CacheStats(BaseModel):
    size: int
    max_size: int
    hits: int
    misses: int
    hit_rate_percent: float
    total_requests: int

class MetricsResponse(BaseModel):
    total_translations: int
    translations_by_direction: Dict[str, int]
    average_inference_time_ms: float
    average_adapter_switch_time_ms: float
    cache_stats: Optional[CacheStats] = None  # NEW
```

---

#### [MODIFY] `app/main.py`

**Initialize cache and inject into translator**:

Changes at lines ~50-60:
```python
from app.core.cache import TranslationCache

# Initialize cache
translation_cache = TranslationCache(max_size=500)
logger.info("✓ Translation cache initialized (max_size=500)")

# Initialize translation engine with cache
translation_engine = TranslationEngine(
    model=model,
    tokenizer=tokenizer,
    adapter_manager=adapter_manager,
    cache=translation_cache  # Inject cache
)
```

Pass cache to routes:
```python
routes.set_dependencies(
    engine=translation_engine,
    chunk=chunker,
    metrics=metrics_collector,
    adapter_mgr=adapter_manager,
    mdl_info=model_info,
    cache=translation_cache  # NEW
)
```

---

#### [MODIFY] `app/api/routes.py`

**Add cache stats to metrics endpoint and optional clear endpoint**:

Add global cache reference:
```python
translation_cache = None

def set_dependencies(engine, chunk, metrics, adapter_mgr, mdl_info, cache):
    global translation_engine, chunker, metrics_collector, adapter_manager, model_info, translation_cache
    translation_engine = engine
    chunker = chunk
    metrics_collector = metrics
    adapter_manager = adapter_mgr
    model_info = mdl_info
    translation_cache = cache  # NEW
```

Update metrics endpoint (lines ~230-245):
```python
@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get aggregated metrics including cache stats"""
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
```

Add cache clear endpoint (optional):
```python
@router.post("/cache/clear")
async def clear_cache():
    """Clear translation cache (for testing/debugging)"""
    try:
        if not translation_cache:
            raise HTTPException(status_code=503, detail="Cache not available")
        
        translation_cache.clear()
        logger.info("Translation cache cleared")
        
        return {"message": "Cache cleared successfully", "stats": translation_cache.get_stats()}
        
    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to clear cache")
```

---

## Verification Plan

### Automated Tests

**Test cache hit/miss**:
```python
# Test 1: Cache miss on first request
result1 = translate("Hello", "en", "hi")
assert result1["metrics"]["from_cache"] == False

# Test 2: Cache hit on repeated request
result2 = translate("Hello", "en", "hi")
assert result2["metrics"]["from_cache"] == True

# Test 3: Different text = cache miss
result3 = translate("Goodbye", "en", "hi")
assert result3["metrics"]["from_cache"] == False
```

### Manual Verification

1. **Start application**: `python -m uvicorn app.main:app --reload`
2. **Translate same text twice**: Note the response time difference
3. **Check metrics**: `curl http://localhost:8000/metrics`
4. **Verify cache stats**: Should show hits, misses, hit_rate
5. **Clear cache** (optional): `curl -X POST http://localhost:8000/cache/clear`

---

## Expected Performance Impact

**For repeated translations**:
- ⚡ Response time: ~2000ms → ~5ms (400x faster)
- 💾 Memory usage: ~50-100 MB for 500 entries
- 🎯 Expected hit rate: 20-40% for government docs

**Cache size calculation**:
- Average translation result: ~100-200 KB
- 500 entries: ~50-100 MB total
- Acceptable for most systems

---

## Success Criteria

- ✅ Cache correctly stores and retrieves translations
- ✅ LRU eviction works when cache is full
- ✅ Cache stats accurately track hits/misses
- ✅ Metrics endpoint includes cache statistics
- ✅ Cached responses are 400x+ faster than fresh translations
- ✅ No memory leaks or unbounded growth

---

## Implementation Timeline

**Total Estimate**: 45-60 minutes

1. **Create cache module** (15 min)
2. **Integrate with translator** (15 min)
3. **Update schemas and routes** (10 min)
4. **Testing and verification** (10 min)
5. **Documentation** (10 min)
