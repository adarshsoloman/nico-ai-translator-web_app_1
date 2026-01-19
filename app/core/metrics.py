"""
Metrics Collection Module
Tracks and aggregates translation metrics
"""

import time
from typing import Dict, List
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and aggregates translation metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.requests_by_direction = defaultdict(int)
        self.inference_times = []
        self.adapter_switch_times = []
        self.tokens_processed = 0
        
    def record_translation(self, metrics: dict, direction: str):
        """
        Record metrics from a translation request
        
        Args:
            metrics: Metrics dictionary from translation
            direction: Translation direction (e.g., "en_hi")
        """
        self.total_requests += 1
        self.requests_by_direction[direction] += 1
        
        if "inference_time_ms" in metrics:
            self.inference_times.append(metrics["inference_time_ms"])
        
        if "adapter_switch_time_ms" in metrics:
            self.adapter_switch_times.append(metrics["adapter_switch_time_ms"])
        
        if "input_tokens" in metrics and "output_tokens" in metrics:
            self.tokens_processed += metrics["input_tokens"] + metrics["output_tokens"]
    
    def get_metrics(self) -> dict:
        """
        Get aggregated metrics
        
        Returns:
            Dictionary of aggregated metrics
        """
        uptime_seconds = int(time.time() - self.start_time)
        
        avg_inference_time = (
            sum(self.inference_times) / len(self.inference_times)
            if self.inference_times else 0
        )
        
        avg_adapter_switch_time = (
            sum(self.adapter_switch_times) / len(self.adapter_switch_times)
            if self.adapter_switch_times else 0
        )
        
        return {
            "total_requests": self.total_requests,
            "avg_inference_time_ms": round(avg_inference_time, 2),
            "avg_adapter_switch_time_ms": round(avg_adapter_switch_time, 2),
            "requests_by_direction": dict(self.requests_by_direction),
            "total_tokens_processed": self.tokens_processed,
            "uptime_seconds": uptime_seconds,
        }
    
    def reset(self):
        """Reset all metrics"""
        self.start_time = time.time()
        self.total_requests = 0
        self.requests_by_direction = defaultdict(int)
        self.inference_times = []
        self.adapter_switch_times = []
        self.tokens_processed = 0
        logger.info("Metrics reset")
