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
        Split text into sentences while preserving paragraph breaks
        
        Args:
            text: Input text
            
        Returns:
            List of sentences with paragraph markers
        """
        # First, split by paragraphs (double newlines or more)
        paragraphs = re.split(r'\n\s*\n', text)
        
        sentences = []
        for i, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
                
            # Split paragraph into sentences
            para_sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$', paragraph)
            para_sentences = [s.strip() for s in para_sentences if s and s.strip()]
            
            # Add sentences from this paragraph
            sentences.extend(para_sentences)
            
            # Add paragraph break marker (except after last paragraph)
            if i < len(paragraphs) - 1 and para_sentences:
                sentences.append("__PARAGRAPH_BREAK__")
        
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
    
    def _join_sentences(self, sentences: List[str]) -> str:
        """
        Join sentences while preserving paragraph breaks
        
        Args:
            sentences: List of sentences (may include __PARAGRAPH_BREAK__ markers)
            
        Returns:
            Joined text with proper paragraph breaks
        """
        result = []
        for sentence in sentences:
            if sentence == "__PARAGRAPH_BREAK__":
                result.append("\n\n")
            else:
                result.append(sentence)
        
        # Join with spaces, but paragraph breaks are already added
        text = ""
        for i, part in enumerate(result):
            if part == "\n\n":
                text += part
            elif i > 0 and result[i-1] != "\n\n":
                text += " " + part
            else:
                text += part
        
        return text
    
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
                        chunk_text = self._join_sentences(current_chunk)
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
                    chunk_text = self._join_sentences(current_chunk)
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
                chunk_text = self._join_sentences(current_chunk)
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
