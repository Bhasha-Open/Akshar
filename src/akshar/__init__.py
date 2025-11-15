"""
akshar: A linguistically-aware tokenizer for Hindi, Sanskrit, and Hinglish.

This tokenizer understands Devanagari akshars, detects code-switch boundaries,
normalizes Hinglish semantically, and uses phonetic signatures to align 
Romanized Hindi with native Devanagari forms.
"""

__version__ = "0.1.0"
__author__ = "Bhasha Open"

from .tokenizer import aksharTokenizer
from .segment import (
    segment_akshars, 
    detect_code_switches,
    word_tokenize,
    word_tokenize_hindi,
    word_tokenize_sanskrit
)
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

# comprehensive features
from .features import (
    akshara_level_tokenization,
    sandhi_aware_tokenization,
    schwa_deletion_modeling,
    preserve_conjuncts,
    intelligent_anusvara_resolution,
    handle_chandrabindu,
    preserve_nukta,
    recognize_virama_function,
    mora_aware_segmentation,
    sanskrit_punctuation_tokenization,
    preserve_svara_marks_feature,
    devanagari_digit_tokenization,
    preserve_zwj,
    preserve_proper_names,
    provide_lemma_hints,
    preserve_orthographic_variants,
    transliteration_tokenization,
    visarga_condition_tokenization,
    preserve_independent_vowels,
    emoji_tokenization,
)

__all__ = [
    # core
    "aksharTokenizer",
    "segment_akshars",
    "detect_code_switches",
    "normalize_text",
    "normalize_hinglish",
    
    # word-level tokenization
    "word_tokenize",
    "word_tokenize_hindi",
    "word_tokenize_sanskrit",
    
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
    
    # comprehensive features (20 new features - 5 duplicates removed)
    "akshara_level_tokenization",
    "sandhi_aware_tokenization",
    "schwa_deletion_modeling",
    "preserve_conjuncts",
    "intelligent_anusvara_resolution",
    "handle_chandrabindu",
    "preserve_nukta",
    "recognize_virama_function",
    "mora_aware_segmentation",
    "sanskrit_punctuation_tokenization",
    "preserve_svara_marks_feature",
    "devanagari_digit_tokenization",
    "preserve_zwj",
    "preserve_proper_names",
    "provide_lemma_hints",
    "preserve_orthographic_variants",
    "transliteration_tokenization",
    "visarga_condition_tokenization",
    "preserve_independent_vowels",
    "emoji_tokenization",
]

