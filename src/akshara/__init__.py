"""
Akshara: A linguistically-aware tokenizer for Hindi, Sanskrit, and Hinglish.

This tokenizer understands Devanagari aksharas, detects code-switch boundaries,
normalizes Hinglish semantically, and uses phonetic signatures to align 
Romanized Hindi with native Devanagari forms.
"""

__version__ = "0.1.0"
__author__ = "Bhasha Open"

from .tokenizer import AksharaTokenizer
from .segment import segment_aksharas, detect_code_switches
from .normalize import normalize_text, normalize_hinglish
from .morph import (
    segment_hindi,
    segment_sanskrit,
    get_hindi_segmenter,
    get_sanskrit_segmenter
)
from .phonetic import (
    get_phonetic_analyzer,
    analyze_phonetics,
)
from .script_utils import (
    identify_scripts,
    analyze_script,
)

__all__ = [
    # core
    "AksharaTokenizer",
    "segment_aksharas",
    "detect_code_switches",
    "normalize_text",
    "normalize_hinglish",
    
    # morphology
    "segment_hindi",
    "segment_sanskrit",
    "get_hindi_segmenter",
    "get_sanskrit_segmenter",
    
    # phonetics
    "get_phonetic_analyzer",
    "analyze_phonetics",
    
    # script analysis
    "identify_scripts",
    "analyze_script",
]

