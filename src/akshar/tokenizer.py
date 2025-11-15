"""
main tokenizer - wraps sentencepiece/bpe with our intelligence layers
"""

import os
from pathlib import Path
from typing import List, Optional, Union

from .normalize import normalize_text
from .segment import segment_akshars, detect_code_switches, analyze_text_composition


class aksharTokenizer:
    """
    tokenizer for hindi/sanskrit/hinglish
    
    does normalization -> akshar segmentation -> code-switch detection 
    then applies SP/BPE if model is loaded
    """
    
    def __init__(
        self, 
        model_path: Optional[str] = None,
        model_type: str = "sentencepiece",
        normalize_roman: bool = True,
        clean_hinglish: bool = True
    ):
        self.model_path = model_path
        self.normalize_roman = normalize_roman
        self.clean_hinglish = clean_hinglish
        self.model = None
        self._configured_model_type = model_type  # store configured type
        
        if model_path and os.path.exists(model_path):
            self._load_model()
        else:
            # no model loaded - use akshar segmentation
            self.model_type = "akshar"
    
    def _load_model(self):
        """load SP or BPE model"""
        # use configured model type when loading
        model_type = self._configured_model_type
        
        if model_type == "sentencepiece":
            try:
                import sentencepiece as spm
                self.model = spm.SentencePieceProcessor()
                self.model.Load(self.model_path)
                self.model_type = "sentencepiece"
            except ImportError:
                raise ImportError("need sentencepiece: pip install sentencepiece")
        elif model_type == "bpe":
            try:
                from tokenizers import Tokenizer
                self.model = Tokenizer.from_file(self.model_path)
                self.model_type = "bpe"
            except ImportError:
                raise ImportError("need tokenizers: pip install tokenizers")
        else:
            raise ValueError(f"unknown model_type: {model_type}")
    
    def preprocess(self, text: str) -> str:
        """run normalization before tokenizing"""
        return normalize_text(
            text,
            normalize_roman=self.normalize_roman,
            clean_hinglish=self.clean_hinglish
        )
    
    def tokenize(self, text: str, return_metadata: bool = False) -> Union[List[str], dict]:
        """
        tokenize text
        
        if no model loaded, falls back to akshar-level tokens
        """
        norm = self.preprocess(text)
        
        if return_metadata:
            meta = analyze_text_composition(norm)
        
        # use model if we have one, otherwise just segment akshars
        if self.model is None:
            tokens = segment_akshars(norm)
        elif self.model_type == "sentencepiece":
            tokens = self.model.EncodeAsPieces(norm)
        elif self.model_type == "bpe":
            enc = self.model.encode(norm)
            tokens = enc.tokens
        
        if return_metadata:
            meta['tokens'] = tokens
            meta['token_count'] = len(tokens)
            meta['original_text'] = text
            meta['normalized_text'] = norm
            return meta
        
        return tokens
    
    def encode(self, text: str) -> List[int]:
        """get token IDs"""
        norm = self.preprocess(text)
        
        if self.model is None:
            raise ValueError("need model for IDs")
        
        if self.model_type == "sentencepiece":
            return self.model.EncodeAsIds(norm)
        elif self.model_type == "bpe":
            return self.model.encode(norm).ids
    
    def decode(self, ids: List[int]) -> str:
        """IDs -> text"""
        if self.model is None:
            raise ValueError("need model to decode")
        
        if self.model_type == "sentencepiece":
            return self.model.DecodeIds(ids)
        elif self.model_type == "bpe":
            return self.model.decode(ids)
    
    def detokenize(self, tokens: List[str]) -> str:
        """tokens -> text"""
        if self.model_type == "sentencepiece":
            # SP uses ▁ for space
            txt = ''.join(tokens)
            txt = txt.replace('▁', ' ')
            return txt.strip()
        elif self.model_type == "bpe":
            # BPE uses ## or Ġ
            txt = ' '.join(tokens)
            txt = txt.replace(' ##', '')
            txt = txt.replace('Ġ', ' ')
            return txt.strip()
        else:
            return ''.join(tokens)
    
    def explain(self, text: str) -> dict:
        """
        show all the processing steps for debugging
        
        useful to see whats happening inside
        """
        norm = self.preprocess(text)
        akshars = segment_akshars(norm)
        switches = detect_code_switches(norm)
        stats = analyze_text_composition(norm)
        tokens = self.tokenize(text)
        
        return {
            'original': text,
            'normalized': norm,
            'akshars': akshars,
            'code_switches': switches,
            'tokens': tokens,
            'stats': stats
        }
    
    def vocab_size(self) -> int:
        """get vocab size"""
        if self.model is None:
            return 0
        
        if self.model_type == "sentencepiece":
            return self.model.GetPieceSize()
        elif self.model_type == "bpe":
            return self.model.get_vocab_size()
        
        return 0
    

