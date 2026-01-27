"""
Translation Engine Module
Handles tokenization, inference, and decoding with NLLB-specific language codes
"""

import torch
import time
from app.core.config import (
    LANG_CODE_MAP,
    SUPPORTED_LANGUAGES,
    DEFAULT_DECODING_PARAMS,
    MAX_INPUT_LENGTH_CHARS,
    MAX_INPUT_LENGTH_TOKENS,
    DEVICE
)
import logging

logger = logging.getLogger(__name__)


class TranslationEngine:
    """Handles translation with NLLB models"""
    
    def __init__(self, model, tokenizer, adapter_manager, cache=None):
        self.model = model
        self.tokenizer = tokenizer
        self.adapter_manager = adapter_manager
        self.device = DEVICE
        self.cache = cache  # Translation result cache
        
    def validate_input(self, text: str, source_lang: str, target_lang: str):
        """
        Validate translation input
        
        Args:
            text: Input text
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if text is empty
        if not text or not text.strip():
            return False, "Input text cannot be empty"
        
        # Check text length
        if len(text) > MAX_INPUT_LENGTH_CHARS:
            return False, f"Input text exceeds maximum length of {MAX_INPUT_LENGTH_CHARS} characters"
        
        # Check language codes
        if source_lang not in SUPPORTED_LANGUAGES:
            return False, f"Unsupported source language: {source_lang}"
        
        if target_lang not in SUPPORTED_LANGUAGES:
            return False, f"Unsupported target language: {target_lang}"
        
        # Check if source and target are the same
        if source_lang == target_lang:
            return False, "Source and target languages cannot be the same"
        
        return True, None
    
    def translate(self, text: str, source_lang: str, target_lang: str, decoding_params: dict = None):
        """
        Translate text from source to target language
        
        Args:
            text: Input text to translate
            source_lang: Source language code ("en" or "hi")
            target_lang: Target language code ("en" or "hi")
            decoding_params: Optional decoding parameters
            
        Returns:
            dict: Translation result with metrics
        """
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
                    logger.info(f"Cache hit for translation ({source_lang} → {target_lang})")
                    # Mark as from cache
                    cached_result["metrics"]["from_cache"] = True
                    return cached_result
            

            # Check if text contains multiple lines (paragraphs or line breaks)
            # Split by any newline (single or double) to preserve all formatting
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            if len(lines) > 1:
                # Translate each line separately to preserve structure
                logger.info(f"Translating {len(lines)} lines separately")
                translated_lines = []
                total_input_tokens = 0
                total_output_tokens = 0
                total_inference_time_ms = 0
                adapter_switch_time_ms = 0
                
                for i, line in enumerate(lines):
                    result = self._translate_single(line, source_lang, target_lang, decoding_params)
                    translated_lines.append(result["translated_text"])
                    total_input_tokens += result["metrics"]["input_tokens"]
                    total_output_tokens += result["metrics"]["output_tokens"]
                    total_inference_time_ms += result["metrics"]["inference_time_ms"]
                    if i == 0:
                        adapter_switch_time_ms = result["metrics"]["adapter_switch_time_ms"]
                
                # Join lines with single newlines to preserve original structure
                translated_text = "\n".join(translated_lines)
                
                # Calculate total time
                total_time_ms = (time.time() - start_time) * 1000
                tokens_per_second = (total_output_tokens / total_inference_time_ms) * 1000 if total_inference_time_ms > 0 else 0
                
                result = {
                    "translated_text": translated_text,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "metrics": {
                        "inference_time_ms": round(total_inference_time_ms, 2),
                        "adapter_switch_time_ms": round(adapter_switch_time_ms, 2),
                        "total_time_ms": round(total_time_ms, 2),
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                        "tokens_per_second": round(tokens_per_second, 2),
                        "from_cache": False
                    }
                }
                
                # Store in cache
                if self.cache:
                    self.cache.set(text, source_lang, target_lang, result)
                
                return result
            else:
                # Single line - translate normally
                result = self._translate_single(text, source_lang, target_lang, decoding_params)
                result["metrics"]["from_cache"] = False
                
                # Store in cache
                if self.cache:
                    self.cache.set(text, source_lang, target_lang, result)
                
                return result
            
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}", exc_info=True)
            raise
    
    def _translate_single(self, text: str, source_lang: str, target_lang: str, decoding_params: dict = None):
        """
        Translate a single paragraph/text block
        
        Args:
            text: Input text to translate (single paragraph)
            source_lang: Source language code
            target_lang: Target language code
            decoding_params: Optional decoding parameters
            
        Returns:
            dict: Translation result with metrics
        """
        start_time = time.time()
        
        # Determine translation direction
        direction = f"{source_lang}_{target_lang}"
        
        # Switch adapter if needed
        adapter_switch_time_ms = self.adapter_manager.switch_adapter(direction)
        
        # Get NLLB language codes
        src_lang_code = LANG_CODE_MAP[source_lang]
        tgt_lang_code = LANG_CODE_MAP[target_lang]
        
        # Set tokenizer source language
        self.tokenizer.src_lang = src_lang_code
        
        # Tokenize input
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=MAX_INPUT_LENGTH_TOKENS
        ).to(self.device)
        
        input_tokens = inputs['input_ids'].shape[1]
        
        # Prepare decoding parameters
        params = DEFAULT_DECODING_PARAMS.copy()
        if decoding_params:
            params.update(decoding_params)
        
        # Get forced_bos_token_id for target language
        forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(tgt_lang_code)
        
        # Get the current model (PEFT or base)
        current_model = self.adapter_manager.get_model()
        
        # Generate translation
        inference_start = time.time()
        with torch.no_grad():
            outputs = current_model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                **params
            )
        inference_time_ms = (time.time() - inference_start) * 1000
        
        output_tokens = outputs.shape[1]
        
        # Decode output
        translated_text = self.tokenizer.batch_decode(
            outputs,
            skip_special_tokens=True
        )[0]
        
        # Calculate total time
        total_time_ms = (time.time() - start_time) * 1000
        
        # Calculate tokens per second
        tokens_per_second = (output_tokens / inference_time_ms) * 1000 if inference_time_ms > 0 else 0
        
        # Return result with metrics
        return {
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "metrics": {
                "inference_time_ms": round(inference_time_ms, 2),
                "adapter_switch_time_ms": round(adapter_switch_time_ms, 2),
                "total_time_ms": round(total_time_ms, 2),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "tokens_per_second": round(tokens_per_second, 2),
            }
        }
