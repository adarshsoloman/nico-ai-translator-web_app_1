"""
Translation Result Cache Module

Implements LRU (Least Recently Used) cache for translation results
to avoid redundant GPU/CPU computation for repeated translations.
"""

from collections import OrderedDict
import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TranslationCache:
    """
    LRU cache for translation results.
    
    Stores translation results with automatic eviction of least recently used
    entries when the cache reaches maximum capacity.
    """
    
    def __init__(self, max_size: int = 500):
        """
        Initialize translation cache.
        
        Args:
            max_size: Maximum number of translations to cache (default: 500)
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self.created_at = datetime.now()
        logger.info(f"Translation cache initialized with max_size={max_size}")
    
    def _generate_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Generate cache key from translation parameters.
        
        Args:
            text: Input text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            MD5 hash of combined parameters
        """
        combined = f"{text}|{source_lang}|{target_lang}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached translation if exists.
        
        Args:
            text: Input text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Cached translation result or None if not found
        """
        key = self._generate_key(text, source_lang, target_lang)
        
        if key in self.cache:
            self.hits += 1
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            logger.debug(f"Cache hit for key: {key[:8]}...")
            return self.cache[key]
        
        self.misses += 1
        logger.debug(f"Cache miss for key: {key[:8]}...")
        return None
    
    def set(self, text: str, source_lang: str, target_lang: str, result: Dict[str, Any]):
        """
        Store translation result in cache.
        
        Args:
            text: Input text that was translated
            source_lang: Source language code
            target_lang: Target language code
            result: Translation result to cache
        """
        key = self._generate_key(text, source_lang, target_lang)
        
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = next(iter(self.cache))
            self.cache.popitem(last=False)
            logger.debug(f"Cache full, evicted oldest entry: {oldest_key[:8]}...")
        
        self.cache[key] = result
        self.cache.move_to_end(key)
        logger.debug(f"Cached translation for key: {key[:8]}...")
    
    def clear(self):
        """Clear all cached entries and reset statistics."""
        cache_size = len(self.cache)
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info(f"Cache cleared ({cache_size} entries removed)")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary containing cache metrics:
            - size: Current number of cached entries
            - max_size: Maximum cache capacity
            - hits: Number of cache hits
            - misses: Number of cache misses
            - hit_rate_percent: Cache hit rate as percentage
            - total_requests: Total cache lookups
        """
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
