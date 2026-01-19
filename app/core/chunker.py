"""
Text Chunker Module
Handles intelligent text splitting for long document translation
"""

import re
from typing import List
from app.core.config import CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_SENTENCES
import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """Splits long documents into translation-friendly chunks"""
    
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.chunk_size_tokens = CHUNK_SIZE_TOKENS
        self.overlap_sentences = CHUNK_OVERLAP_SENTENCES
        
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using simple regex
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting on period, exclamation, question mark
        # followed by space and capital letter or end of string
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$', text)
        
        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        tokens = self.tokenizer(text, return_tensors="pt", truncation=False)
        return tokens['input_ids'].shape[1]
    
    def chunk_text(self, text: str) -> List[dict]:
        """
        Split text into chunks based on token count
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        try:
            # Split into sentences
            sentences = self.split_into_sentences(text)
            
            if not sentences:
                return [{"text": text, "chunk_id": 0, "token_count": self.count_tokens(text)}]
            
            chunks = []
            current_chunk = []
            current_tokens = 0
            chunk_id = 0
            
            for sentence in sentences:
                sentence_tokens = self.count_tokens(sentence)
                
                # If single sentence exceeds chunk size, split it further
                if sentence_tokens > self.chunk_size_tokens:
                    # If we have accumulated sentences, save them first
                    if current_chunk:
                        chunk_text = " ".join(current_chunk)
                        chunks.append({
                            "text": chunk_text,
                            "chunk_id": chunk_id,
                            "token_count": current_tokens
                        })
                        chunk_id += 1
                        current_chunk = []
                        current_tokens = 0
                    
                    # Split long sentence by clauses (commas, semicolons)
                    clauses = re.split(r'([,;])', sentence)
                    clause_chunk = []
                    clause_tokens = 0
                    
                    for clause in clauses:
                        clause_token_count = self.count_tokens(clause)
                        if clause_tokens + clause_token_count > self.chunk_size_tokens and clause_chunk:
                            # Save current clause chunk
                            clause_text = "".join(clause_chunk)
                            chunks.append({
                                "text": clause_text,
                                "chunk_id": chunk_id,
                                "token_count": clause_tokens
                            })
                            chunk_id += 1
                            clause_chunk = [clause]
                            clause_tokens = clause_token_count
                        else:
                            clause_chunk.append(clause)
                            clause_tokens += clause_token_count
                    
                    # Save remaining clauses
                    if clause_chunk:
                        clause_text = "".join(clause_chunk)
                        chunks.append({
                            "text": clause_text,
                            "chunk_id": chunk_id,
                            "token_count": clause_tokens
                        })
                        chunk_id += 1
                    
                    continue
                
                # Check if adding this sentence would exceed chunk size
                if current_tokens + sentence_tokens > self.chunk_size_tokens and current_chunk:
                    # Save current chunk
                    chunk_text = " ".join(current_chunk)
                    chunks.append({
                        "text": chunk_text,
                        "chunk_id": chunk_id,
                        "token_count": current_tokens
                    })
                    chunk_id += 1
                    
                    # Start new chunk with overlap
                    if self.overlap_sentences > 0 and len(current_chunk) > self.overlap_sentences:
                        current_chunk = current_chunk[-self.overlap_sentences:]
                        current_tokens = sum(self.count_tokens(s) for s in current_chunk)
                    else:
                        current_chunk = []
                        current_tokens = 0
                
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
            
            # Save final chunk
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "chunk_id": chunk_id,
                    "token_count": current_tokens
                })
            
            logger.info(f"Split text into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Chunking failed: {str(e)}", exc_info=True)
            # Fallback: return entire text as single chunk
            return [{"text": text, "chunk_id": 0, "token_count": self.count_tokens(text)}]
