"""
Tokenizer orchestration for Akshar.

This module wraps optional subword models (SentencePiece/BPE) with Akshar’s
linguistic steps: normalization, akshar segmentation, and code-switch analysis.
When no model is provided, we fall back to akshar-level tokens that respect
grapheme clusters (conjuncts etc.).
"""

import os
from pathlib import Path
from typing import List, Optional, Union

from .normalize import normalize_text
from .segment import segment_akshars, detect_code_switches, analyze_text_composition


class aksharTokenizer:
    """
    High-level tokenizer for Hindi/Sanskrit/Hinglish text.

    Pipeline:
        normalize_text → segment_akshars (for analysis) → optional SP/BPE encode

    If a model is not loaded, the tokenizer returns akshar-level tokens that
    never split grapheme clusters.

    Parameters
    ----------
    model_path:
        Path to a trained model. For SentencePiece this is typically ``.model``;
        for BPE this is usually a ``.json`` file from HuggingFace tokenizers.
    model_type:
        One of ``"sentencepiece"`` or ``"bpe"``. Ignored if ``model_path`` is None.
    normalize_roman:
        Whether to lowercase/normalize Roman script during preprocessing.
    clean_hinglish:
        Whether to apply Hinglish cleanup (elongations, garbage filter, etc.).

    Examples
    --------
    No model (akshar-level tokens):
        >>> from akshar.tokenizer import aksharTokenizer
        >>> tk = aksharTokenizer()
        >>> tk.tokenize("मौसम अच्छा है")
        ['मौ', 'स', 'म', ' ', 'अ', 'च्', 'छ', 'ा', ' ', 'है']

    With SentencePiece:
        >>> tk = aksharTokenizer(model_path="models/akshar.model", model_type="sentencepiece")
        >>> tk.tokenize("aaj मौसम बहुत अच्छा hai")
        ['▁aaj', '▁', 'मौ', 'सम', '▁बहुत', '▁अच्छा', '▁hai']
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
        """Load the configured subword model (SentencePiece or BPE).

        Raises
        ------
        ImportError
            If the required backend library is not installed.
        ValueError
            If ``model_type`` is not one of the supported values.
        """
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
        """Apply Akshar normalization prior to tokenization.

        Parameters
        ----------
        text:
            Input string (may contain mixed scripts).

        Returns
        -------
        str
            Normalized text with Roman cleaned (config-dependent).
        """
        return normalize_text(
            text,
            normalize_roman=self.normalize_roman,
            clean_hinglish=self.clean_hinglish
        )
    
    def tokenize(self, text: str, return_metadata: bool = False) -> Union[List[str], dict]:
        """
        Tokenize text using the configured model or akshar fallback.

        Parameters
        ----------
        text:
            Input string.
        return_metadata:
            If True, return a dict with composition stats in addition to tokens.

        Returns
        -------
        List[str] | dict
            Tokens or a metadata dict with tokens and stats.

        Notes
        -----
        - Without a model, tokens are grapheme clusters that preserve conjuncts.
        - With SentencePiece/BPE, tokens follow the model’s subword scheme.
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
        """Convert text to token IDs.

        Parameters
        ----------
        text:
            Input string.

        Returns
        -------
        List[int]
            Token IDs from the loaded model.

        Raises
        ------
        ValueError
            If no model is loaded.
        """
        norm = self.preprocess(text)
        
        if self.model is None:
            raise ValueError("need model for IDs")
        
        if self.model_type == "sentencepiece":
            return self.model.EncodeAsIds(norm)
        elif self.model_type == "bpe":
            return self.model.encode(norm).ids
    
    def decode(self, ids: List[int]) -> str:
        """Convert token IDs back to text.

        Parameters
        ----------
        ids:
            Sequence of token IDs.

        Returns
        -------
        str
            Decoded string per the loaded model.

        Raises
        ------
        ValueError
            If no model is loaded.
        """
        if self.model is None:
            raise ValueError("need model to decode")
        
        if self.model_type == "sentencepiece":
            return self.model.DecodeIds(ids)
        elif self.model_type == "bpe":
            return self.model.decode(ids)
    
    def detokenize(self, tokens: List[str]) -> str:
        """Join tokens back into a string.

        Parameters
        ----------
        tokens:
            Sequence of token strings (model-dependent).

        Returns
        -------
        str
            Reconstructed text (heuristic per model type).
        """
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
        Explain all processing steps for a given input.

        Parameters
        ----------
        text:
            Input string.

        Returns
        -------
        dict
            Dictionary with original/normalized text, akshars, script segments,
            produced tokens and composition statistics.
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
        """Return vocabulary size for the loaded model (0 if none)."""
        if self.model is None:
            return 0
        
        if self.model_type == "sentencepiece":
            return self.model.GetPieceSize()
        elif self.model_type == "bpe":
            return self.model.get_vocab_size()
        
        return 0
    

