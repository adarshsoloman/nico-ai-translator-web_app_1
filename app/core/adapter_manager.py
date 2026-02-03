"""
Adapter Manager Module
Handles adapter management (temporarily disabled for CT2 integration)
"""

import threading
import time
# from peft import PeftModel  # DISABLED: CT2 doesn't support PEFT adapters
from app.core.config import ADAPTER_PATHS
import logging
import os

logger = logging.getLogger(__name__)


class AdapterManager:
    """Manages adapters - currently using base CT2 model only"""
    
    def __init__(self, base_translator, tokenizer):
        self.base_translator = base_translator  # CT2 translator
        self.tokenizer = tokenizer
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Adapter state (disabled for now)
        self.peft_model = None
        self.active_adapter = None
        self.adapters_loaded = {}
        
        # Metrics
        self.switch_times = []
        
    def load_adapters(self):
        """
        Load adapters
        
        NOTE: CT2 does not support dynamic adapter loading like PEFT.
        For now, we'll use the base CT2 model only.
        
        TODO: Implement one of:
        - Option 1: Merge adapters into separate CT2 models
        - Option 2: Keep PEFT for adapter support (hybrid approach)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.warning("=" * 60)
            logger.warning("ADAPTER LOADING DISABLED FOR CT2 INTEGRATION")
            logger.warning("Using CT2 base model only (no domain-specific adapters)")
            logger.warning("=" * 60)
            
            # For now, just return False to indicate no adapters loaded
            # The base translator will be used for all translations
            return False
            
        except Exception as e:
            logger.error(f"Failed to load adapters: {str(e)}", exc_info=True)
            logger.warning("Falling back to base model only")
            self.peft_model = None
            return False
    
    def switch_adapter(self, direction: str):
        """
        Switch to a different adapter (DISABLED for CT2)
        
        Args:
            direction: Translation direction ("en_hi" or "hi_en")
            
        Returns:
            float: Switch time in milliseconds (always 0.0 for CT2 base model)
        """
        # No adapter switching needed - always use base translator
        return 0.0
    
    def get_model(self):
        """
        Get the current translator (CT2 base translator)
        
        Returns:
            translator: Current active CT2 translator
        """
        return self.base_translator  # Always return base CT2 translator
    
    def get_adapter_info(self):
        """Get adapter information for health checks"""
        return {
            "adapters_loaded": {},
            "active_adapter": "base",
            "using_adapters": False,
            "avg_switch_time_ms": 0.0,
            "note": "CT2 integration - adapters disabled, using base model only"
        }
