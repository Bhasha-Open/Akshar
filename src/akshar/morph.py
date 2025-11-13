"""
morph segmentation - uses morfessor models from indic_nlp_resources
"""

from pathlib import Path
from typing import List, Optional


class MorphSegmenter:
    """
    morph segmenter for hindi/sanskrit
    
    uses morfessor for unsupervised segmentation
    falls back to returning whole word if no model
    """
    
    def __init__(self, language='hi'):
        self.language = language
        self.model = None
        self._try_load_model()
    
    def _try_load_model(self):
        """try loading morfessor model"""
        try:
            import morfessor
            
            res_dir = Path(__file__).parent / "resources"
            model_file = res_dir / f"{self.language}.model"
            
            if model_file.exists():
                io = morfessor.MorfessorIO()
                # try text format first (most common)
                try:
                    self.model = io.read_any_model(str(model_file))
                except:
                    # fallback to binary
                    self.model = io.read_binary_model_file(str(model_file))
        except ImportError:
            # morfessor not installed
            pass
        except Exception:
            # model loading failed - silent fail
            pass
    
    def segment_word(self, word: str) -> List[str]:
        """segment word into morphemes"""
        if self.model is not None:
            try:
                # use viterbi algo
                seg = self.model.viterbi_segment(word)
                return list(seg[0])
            except:
                pass
        
        # fallback
        return [word]
    
    def segment_text(self, text: str) -> List[str]:
        """segment all words in text"""
        words = text.split()
        result = []
        
        for w in words:
            morphs = self.segment_word(w)
            result.extend(morphs)
        
        return result
    
    def is_model_loaded(self) -> bool:
        """check if model loaded"""
        return self.model is not None


# global singletons
_hindi_seg = None
_sanskrit_seg = None


def get_hindi_segmenter() -> MorphSegmenter:
    """get hindi segmenter (singleton)"""
    global _hindi_seg
    if _hindi_seg is None:
        _hindi_seg = MorphSegmenter('hi')
    return _hindi_seg


def get_sanskrit_segmenter() -> MorphSegmenter:
    """get sanskrit segmenter (singleton)"""
    global _sanskrit_seg
    if _sanskrit_seg is None:
        _sanskrit_seg = MorphSegmenter('sa')
    return _sanskrit_seg


def segment_hindi(text: str) -> List[str]:
    """segment hindi text"""
    return get_hindi_segmenter().segment_text(text)


def segment_sanskrit(text: str) -> List[str]:
    """segment sanskrit text"""
    return get_sanskrit_segmenter().segment_text(text)

