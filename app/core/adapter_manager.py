"""
Adapter Manager Module
Handles PEFT LoRA adapter loading and switching with thread safety
"""

import threading
import time
from peft import PeftModel
from app.core.config import ADAPTER_PATHS, DEVICE
import logging
import os

logger = logging.getLogger(__name__)


class AdapterManager:
    """Manages LoRA adapters with thread-safe switching"""
    
    def __init__(self, base_model, tokenizer):
        self.base_model = base_model
        self.tokenizer = tokenizer
        self.device = DEVICE
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Adapter state
        self.peft_model = None
        self.active_adapter = None
        self.adapters_loaded = {}
        
        # Metrics
        self.switch_times = []
        
    def load_adapters(self):
        """
        Load both LoRA adapters at startup
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Loading LoRA adapters...")
            
            # Check if adapter paths exist
            for direction, path in ADAPTER_PATHS.items():
                if not os.path.exists(path):
                    logger.warning(f"Adapter path not found: {path}")
                    logger.warning(f"Will use base model only for {direction}")
                    return False
            
            # Load the first adapter (en_hi) as base
            logger.info(f"Loading adapter: en_hi from {ADAPTER_PATHS['en_hi']}")
            self.peft_model = PeftModel.from_pretrained(
                self.base_model,
                ADAPTER_PATHS['en_hi'],
                adapter_name="en_hi"
            )
            self.adapters_loaded["en_hi"] = True
            self.active_adapter = "en_hi"
            logger.info("Adapter en_hi loaded successfully")
            
            # Load the second adapter (hi_en)
            logger.info(f"Loading adapter: hi_en from {ADAPTER_PATHS['hi_en']}")
            self.peft_model.load_adapter(
                ADAPTER_PATHS['hi_en'],
                adapter_name="hi_en"
            )
            self.adapters_loaded["hi_en"] = True
            logger.info("Adapter hi_en loaded successfully")
            
            logger.info(f"All adapters loaded. Active adapter: {self.active_adapter}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load adapters: {str(e)}", exc_info=True)
            logger.warning("Falling back to base model only")
            self.peft_model = None
            return False
    
    def switch_adapter(self, direction: str):
        """
        Switch to a different adapter
        
        Args:
            direction: Translation direction ("en_hi" or "hi_en")
            
        Returns:
            float: Switch time in milliseconds
        """
        with self.lock:
            start_time = time.time()
            
            try:
                # If no adapters loaded, return immediately
                if self.peft_model is None:
                    logger.debug("No adapters loaded, using base model")
                    return 0.0
                
                # If already on the correct adapter, no switch needed
                if self.active_adapter == direction:
                    logger.debug(f"Already using adapter: {direction}")
                    return 0.0
                
                # Switch adapter
                logger.debug(f"Switching adapter from {self.active_adapter} to {direction}")
                self.peft_model.set_adapter(direction)
                self.active_adapter = direction
                
                # Calculate switch time
                switch_time_ms = (time.time() - start_time) * 1000
                self.switch_times.append(switch_time_ms)
                
                logger.debug(f"Adapter switched to {direction} in {switch_time_ms:.2f}ms")
                return switch_time_ms
                
            except Exception as e:
                logger.error(f"Failed to switch adapter: {str(e)}", exc_info=True)
                return 0.0
    
    def get_model(self):
        """
        Get the current model (PEFT model if adapters loaded, else base model)
        
        Returns:
            model: Current active model
        """
        return self.peft_model if self.peft_model is not None else self.base_model
    
    def get_adapter_info(self):
        """Get adapter information for health checks"""
        return {
            "adapters_loaded": self.adapters_loaded,
            "active_adapter": self.active_adapter,
            "using_adapters": self.peft_model is not None,
            "avg_switch_time_ms": sum(self.switch_times) / len(self.switch_times) if self.switch_times else 0,
        }
