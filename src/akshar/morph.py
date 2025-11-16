"""
Morphological segmentation using (optional) Morfessor models.

If models are not available, we fall back gracefully and return whole words
so the caller doesn’t get surprised by missing dependencies.
"""

from pathlib import Path
from typing import List, Optional


class MorphSegmenter:
    """
    Morphological segmenter for Hindi/Sanskrit based on Morfessor.
    
    If the model cannot be loaded, the segmenter returns the input word intact.
    """
    
    def __init__(self, language='hi'):
        self.language = language
        self.model = None
        self._try_load_model()
    
    def _try_load_model(self):
        """Attempt to load a Morfessor model from a few known locations."""
        try:
            import morfessor
        except ImportError:
            # morfessor not installed
            return
        
        # try multiple locations for model files
        possible_paths = [
            Path(__file__).parent / "resources" / f"{self.language}.model",
            Path(__file__).parent.parent.parent / "indic_nlp_resources" / "morph" / "morfessor" / f"{self.language}.model",
        ]
        
        model_file = None
        for path in possible_paths:
            if path.exists():
                model_file = path
                break
        
        if model_file:
            try:
                io = morfessor.MorfessorIO()
                # try text format first (most common)
                try:
                    self.model = io.read_any_model(str(model_file))
                except:
                    # fallback to binary
                    try:
                        self.model = io.read_binary_model_file(str(model_file))
                    except:
                        # model format not recognized
                        pass
            except Exception:
                # model loading failed - silent fail
                pass
    
    def segment_word(self, word: str) -> List[str]:
        """Segment a single word into morphemes (if model available)."""
        if self.model is not None:
            try:
                # use viterbi algo
                seg = self.model.viterbi_segment(word)
                return list(seg[0])
            except:
                pass
        
        # fallback: basic segmentation using heuristics
        # try to split on common morpheme boundaries
        from .segment import segment_akshars
        
        # for now, just return word-level or akshar-level
        # could add more sophisticated heuristics here
        return [word]
    
    def segment_text(self, text: str) -> List[str]:
        """Segment a whitespace-delimited string into morphemes."""
        words = text.split()
        result = []
        
        for w in words:
            morphs = self.segment_word(w)
            result.extend(morphs)
        
        return result
    
    def is_model_loaded(self) -> bool:
        """Return True if a Morfessor model was loaded successfully."""
        return self.model is not None


# global singletons
_hindi_seg = None
_sanskrit_seg = None


def get_hindi_segmenter() -> MorphSegmenter:
    """Get a cached Hindi segmenter instance (singleton)."""
    global _hindi_seg
    if _hindi_seg is None:
        _hindi_seg = MorphSegmenter("hi")
    return _hindi_seg


def get_sanskrit_segmenter() -> MorphSegmenter:
    """Get a cached Sanskrit segmenter instance (singleton)."""
    global _sanskrit_seg
    if _sanskrit_seg is None:
        _sanskrit_seg = MorphSegmenter('sa')
    return _sanskrit_seg


def segment_hindi(text: str) -> List[str]:
    """Segment Hindi text into morphemes or words (fallback)."""
    return get_hindi_segmenter().segment_text(text)


def segment_sanskrit(text: str) -> List[str]:
    """Segment Sanskrit text into morphemes or words (fallback)."""
    return get_sanskrit_segmenter().segment_text(text)

