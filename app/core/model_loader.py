"""
Model Loader Module
Handles loading of NLLB model using CTranslate2 and tokenizer
"""

import torch
import ctranslate2
from transformers import AutoTokenizer
from app.core.config import (
    BASE_MODEL_NAME,
    HF_TOKEN,
    DEVICE,
    LANG_CODE_MAP
)
import logging

logger = logging.getLogger(__name__)


class ModelLoader:
    """Loads and manages the NLLB CT2 model and tokenizer"""
    
    def __init__(self):
        self.translator = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "int8" if self.device == "cuda" else "int8"  # INT8 for both GPU and CPU
        self.model_path = "./nllb_ct2_int8"  # INT8 quantized model directory
        
    def load_model(self):
        """
        Load NLLB CT2 model and tokenizer
        
        Returns:
            tuple: (translator, tokenizer)
        """
        try:
            logger.info(f"Loading NLLB CT2 model from: {self.model_path}")
            logger.info(f"Device: {self.device}")
            logger.info(f"Compute type: {self.compute_type}")
            
            # Load tokenizer (unchanged - CT2 uses HF tokenizers)
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,  # Tokenizer is saved in CT2 directory
                src_lang="eng_Latn",  # Default source language
                local_files_only=True,  # Enable offline mode
            )
            logger.info("Tokenizer loaded successfully")
            
            # Load CTranslate2 translator
            self.translator = ctranslate2.Translator(
                self.model_path,
                device=self.device,
                compute_type=self.compute_type,
                inter_threads=4,  # Optimize for multi-threading
                intra_threads=4
            )
            
            logger.info(f"CT2 translator loaded successfully on {self.device}")
            logger.info(f"Compute type: {self.compute_type}")
            
            # Run warmup translation
            self._warmup()
            
            return self.translator, self.tokenizer
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}", exc_info=True)
            raise
    
    def _warmup(self):
        """Run a warmup translation to ensure everything works"""
        try:
            logger.info("Running warmup translation...")
            
            # Simple warmup text
            warmup_text = "Hello"
            
            # Tokenize (CT2 requires tokens, not IDs)
            source_tokens = self.tokenizer.convert_ids_to_tokens(
                self.tokenizer.encode(warmup_text)
            )
            
            # Translate using CT2
            results = self.translator.translate_batch(
                [source_tokens],
                target_prefix=[["hin_Deva"]],  # Target language
                max_decoding_length=128,
                beam_size=1,  # Fast warmup
            )
            
            # Decode result
            target_tokens = results[0].hypotheses[0]
            target_ids = self.tokenizer.convert_tokens_to_ids(target_tokens)
            result = self.tokenizer.decode(target_ids, skip_special_tokens=True)
            
            logger.info(f"Warmup translation complete: '{warmup_text}' → '{result}'")
            
        except Exception as e:
            logger.warning(f"Warmup translation failed (non-critical): {str(e)}")
    
    def get_model_info(self):
        """Get model information for health checks"""
        return {
            "model_path": self.model_path,
            "device": str(self.device),
            "compute_type": self.compute_type,
            "engine": "CTranslate2",
            "loaded": self.translator is not None,
        }
