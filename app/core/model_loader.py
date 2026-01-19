"""
Model Loader Module
Handles loading of NLLB base model and tokenizer
"""

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from app.core.config import (
    BASE_MODEL_NAME,
    HF_TOKEN,
    DEVICE,
    TORCH_DTYPE,
    LANG_CODE_MAP
)
import logging

logger = logging.getLogger(__name__)


class ModelLoader:
    """Loads and manages the NLLB base model and tokenizer"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = DEVICE
        
    def load_model(self):
        """
        Load NLLB base model and tokenizer
        
        Returns:
            tuple: (model, tokenizer)
        """
        try:
            logger.info(f"Loading NLLB base model: {BASE_MODEL_NAME}")
            logger.info(f"Device: {self.device}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                BASE_MODEL_NAME,
                token=HF_TOKEN,
                src_lang="eng_Latn",  # Default source language
            )
            logger.info("Tokenizer loaded successfully")
            
            # Load model
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                BASE_MODEL_NAME,
                token=HF_TOKEN,
                torch_dtype=TORCH_DTYPE,
            )
            
            # Move model to device
            self.model = self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            logger.info(f"Model loaded successfully on {self.device}")
            logger.info(f"Model dtype: {self.model.dtype}")
            
            # Run warmup translation
            self._warmup()
            
            return self.model, self.tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}", exc_info=True)
            raise
    
    def _warmup(self):
        """Run a warmup translation to ensure everything works"""
        try:
            logger.info("Running warmup translation...")
            
            # Simple warmup text
            warmup_text = "Hello"
            
            # Tokenize
            inputs = self.tokenizer(
                warmup_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=128
            ).to(self.device)
            
            # Set forced_bos_token_id for target language
            # NLLB tokenizer uses convert_tokens_to_ids for language codes
            forced_bos_token_id = self.tokenizer.convert_tokens_to_ids("hin_Deva")
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    forced_bos_token_id=forced_bos_token_id,
                    max_length=128,
                    num_beams=1,  # Fast warmup
                )
            
            # Decode
            result = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            
            logger.info(f"Warmup translation complete: '{warmup_text}' → '{result}'")
            
        except Exception as e:
            logger.warning(f"Warmup translation failed (non-critical): {str(e)}")
    
    def get_model_info(self):
        """Get model information for health checks"""
        return {
            "model_name": BASE_MODEL_NAME,
            "device": str(self.device),
            "dtype": str(self.model.dtype) if self.model else None,
            "loaded": self.model is not None,
        }
