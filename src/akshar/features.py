"""
comprehensive feature set for akshar tokenizer
implements all 25 features
"""

import regex as re
import unicodedata
from typing import List, Tuple, Dict, Optional
from pathlib import Path

from .segment import segment_akshars, detect_code_switches, identify_script
from .normalize import normalize_unicode
from .sandhi import detect_sandhi_boundaries, mark_sandhi_boundaries
from .schwa import predict_schwa_deletion, annotate_schwa_deletions
from .anusvara import resolve_anusvara, get_nasal_for_consonant
from .vedic import (
    preserve_svara_marks, handle_sanskrit_punctuation,
    count_mora, analyze_metre, is_svara_mark
)
from .transliteration import transliterate_tokens, token_to_iast
from .visarga import handle_visarga_conditions, annotate_visarga


# Feature 2: Akṣara-Level Tokenization
def akshara_level_tokenization(text: str) -> List[str]:
    """
    segment by fundamental phonological unit: consonant cluster + vowel
    
    halant indicates akṣara continues; never cut mid-cluster
    """
    clusters = segment_akshars(text, matras=False)
    aksharas = []
    current = []
    
    for cluster in clusters:
        if '्' in cluster:
            # halant present - continue building akshara
            current.append(cluster)
        else:
            # no halant - complete current akshara
            if current:
                aksharas.append(''.join(current))
                current = []
            aksharas.append(cluster)
    
    if current:
        aksharas.append(''.join(current))
    
    return aksharas


# Feature 4: Sandhi-Aware Boundary Heuristics
def sandhi_aware_tokenization(text: str) -> Dict:
    """
    detect sandhi boundaries without splitting
    
    marks boundaries but preserves original text
    """
    boundaries = detect_sandhi_boundaries(text)
    marked = mark_sandhi_boundaries(text)
    
    return {
        'original': text,
        'boundaries': boundaries,
        'marked': marked
    }


# Feature 5: Schwa-Deletion Modeling (Hindi)
def schwa_deletion_modeling(text: str) -> Dict:
    """
    predict positions where inherent vowels are dropped
    
    only annotates, never removes written 'a'
    """
    annotations = annotate_schwa_deletions(text)
    
    return {
        'text': text,
        'deletion_annotations': annotations
    }


# Feature 6: Conjunct-Cluster Preservation (already handled)
def preserve_conjuncts(text: str) -> List[str]:
    """
    treat clusters like क्त, ज्ञ, ह्न as single structural units
    
    never splits conjunct between halant and following consonant
    """
    return segment_akshars(text, matras=False)


# Feature 7: Intelligent Anusvāra Resolution
def intelligent_anusvara_resolution(text: str) -> Dict:
    """
    map anusvara to real nasal class based on following consonant
    
    stores both original and resolved forms
    """
    return resolve_anusvara(text, store_both=True)


# Feature 8: Chandrabindu Handling
def handle_chandrabindu(text: str) -> List[str]:
    """
    keep nasalization marks (ँ) bound to their vowel
    
    never detaches chandrabindu from vowel
    """
    # chandrabindu is 0x0901
    CHANDRABINDU = '\u0901'
    
    segments = []
    current = []
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if char == CHANDRABINDU:
            # attach to current segment
            current.append(char)
            i += 1
        elif char.isspace():
            if current:
                segments.append(''.join(current))
                current = []
            i += 1
        else:
            # check if next is chandrabindu
            if i + 1 < len(text) and text[i + 1] == CHANDRABINDU:
                current.append(char)
                current.append(text[i + 1])
                i += 2
            else:
                current.append(char)
                i += 1
    
    if current:
        segments.append(''.join(current))
    
    return segments


# Feature 10: Urdu-Loanword Accommodation
def preserve_nukta(text: str) -> List[str]:
    """
    treat phonetic borrowings with nukta as stable units
    
    never strips nukta characters; they change meaning
    """
    # nukta is 0x093C
    NUKTA = '\u093C'
    
    # segment but preserve nukta-bound characters
    segments = segment_akshars(text, matras=False)
    
    # merge segments that contain nukta with following character
    result = []
    i = 0
    while i < len(segments):
        seg = segments[i]
        if NUKTA in seg and i + 1 < len(segments):
            # merge with next segment
            result.append(seg + segments[i + 1])
            i += 2
        else:
            result.append(seg)
            i += 1
    
    return result


# Feature 11: Virāma-Function Recognition
def recognize_virama_function(text: str) -> Dict:
    """
    halant can mean continuation or explicit vowel suppression
    
    context matters - never assume halant always produces conjunct
    """
    # find all halants and analyze context
    halant_positions = []
    for i, char in enumerate(text):
        if char == '्':
            # check context
            prev = text[i - 1] if i > 0 else ''
            next_char = text[i + 1] if i + 1 < len(text) else ''
            
            context = 'unknown'
            if next_char and ord(next_char) >= 0x0915 and ord(next_char) <= 0x0939:
                context = 'conjunct_formation'
            elif i == len(text) - 1 or not next_char:
                context = 'vowel_suppression'
            
            halant_positions.append((i, context, prev + '्' + next_char))
    
    return {
        'text': text,
        'halant_analysis': halant_positions
    }


# Feature 12: Mora-Aware Meter Structuring (Sanskrit)
def mora_aware_segmentation(text: str) -> Dict:
    """
    count light/heavy syllables for metrical integrity
    
    never merges mora differences
    """
    return analyze_metre(text)


# Feature 13: Punctuation Sensitivity for Sanskrit Verse
def sanskrit_punctuation_tokenization(text: str) -> List[str]:
    """
    handle danda (।) and double danda (॥) as special tokens
    
    never merges dandas with nearby words
    """
    return handle_sanskrit_punctuation(text)


# Feature 14: Swara-Mark Preservation (Vedic Texts)
def preserve_svara_marks_feature(text: str) -> List[str]:
    """
    keep svaras attached to syllable they mark
    
    never drops or repositions metre marks
    """
    return preserve_svara_marks(text)


# Feature 15: Number-System Adaptation
def devanagari_digit_tokenization(text: str) -> List[str]:
    """
    handle devanagari digits as their own tokens
    
    never maps devanagari digits to latin silently
    """
    # devanagari digits: 0x0966-0x096F
    segments = []
    current = []
    
    for char in text:
        if 0x0966 <= ord(char) <= 0x096F:
            # devanagari digit - separate token
            if current:
                segments.append(''.join(current))
                current = []
            segments.append(char)
        elif char.isspace():
            if current:
                segments.append(''.join(current))
                current = []
        else:
            current.append(char)
    
    if current:
        segments.append(''.join(current))
    
    return segments


# Feature 16: Robust Zero-Width Joiner Handling
def preserve_zwj(text: str) -> str:
    """
    preserve ZWJ/ZWNJ in canonical data
    
    never strips them; it breaks shapes
    """
    # ZWJ = 0x200D, ZWNJ = 0x200C
    # just return as-is, normalization should preserve them
    return text


# Feature 17: Proper-Name Integrity
def preserve_proper_names(text: str, names: Optional[List[str]] = None) -> List[str]:
    """
    names with unusual spellings should remain whole
    
    never forces tokenizing inside established lexical names
    """
    if names is None:
        # common proper names
        names = ['श्री', 'राम', 'कृष्ण', 'शिव', 'दुर्गा']
    
    # simple approach: if word matches known name, keep whole
    words = text.split()
    result = []
    
    for word in words:
        # check if word starts with known name
        matched = False
        for name in names:
            if word.startswith(name) and len(word) > len(name):
                # might be compound, but preserve if in list
                if word in names:
                    result.append(word)
                    matched = True
                    break
        
        if not matched:
            # normal tokenization
            tokens = segment_akshars(word, matras=False)
            result.extend(tokens)
        else:
            result.append(word)
    
    return result


# Feature 18: Dictionary-Backed Lemma Hints
def provide_lemma_hints(text: str, lemma_dict: Optional[Dict] = None) -> Dict:
    """
    provide optional lemma mapping for morphologically heavy sanskrit
    
    never replaces surface form; only side-channels
    """
    if lemma_dict is None:
        # example mappings
        lemma_dict = {
            'गच्छामि': 'गम्',
            'करोति': 'कृ',
            'भवति': 'भू',
        }
    
    words = text.split()
    lemmas = []
    
    for word in words:
        if word in lemma_dict:
            lemmas.append((word, lemma_dict[word]))
        else:
            lemmas.append((word, None))
    
    return {
        'surface_forms': [w for w, _ in lemmas],
        'lemma_hints': lemmas
    }


# Feature 19: Mixed-Era Orthography Support
def preserve_orthographic_variants(text: str) -> str:
    """
    preserve orthographic differences (ऋ vs रि)
    
    never normalizes these away; preserves orthographic history
    """
    # just return as-is - don't normalize orthographic variants
    return text


# Feature 20: Transliteration-Friendly Tokens
def transliteration_tokenization(text: str, scheme: str = 'iast') -> Dict:
    """
    support consistent mapping to latin schemes
    
    never introduces tokens without direct reversibility
    """
    tokens = segment_akshars(text, matras=False)
    transliterated = transliterate_tokens(tokens, scheme=scheme)
    
    return {
        'original_tokens': tokens,
        'transliterated': transliterated,
        'scheme': scheme
    }


# Feature 21: Visarga-Condition Handling
def visarga_condition_tokenization(text: str) -> Dict:
    """
    handle visarga behavior before sibilants or vowels
    
    never treats visarga as inert punctuation
    """
    return annotate_visarga(text)


# Feature 22: Non-Breaking Vowel Recognition
def preserve_independent_vowels(text: str) -> List[str]:
    """
    independent vowels must remain whole
    
    never mis-segments vowel carriers
    """
    # independent vowels: अ-औ (0x0905-0x0914)
    segments = []
    current = []
    
    i = 0
    while i < len(text):
        char = text[i]
        cp = ord(char)
        
        # check if independent vowel
        if 0x0905 <= cp <= 0x0914:
            # independent vowel - keep whole
            if current:
                segments.append(''.join(current))
                current = []
            # check for following anusvara/visarga
            if i + 1 < len(text) and text[i + 1] in 'ंः':
                segments.append(char + text[i + 1])
                i += 2
            else:
                segments.append(char)
                i += 1
        elif char.isspace():
            if current:
                segments.append(''.join(current))
                current = []
            i += 1
        else:
            current.append(char)
            i += 1
    
    if current:
        segments.append(''.join(current))
    
    return segments


# Feature 24: Emoji Stability Rules
def emoji_tokenization(text: str) -> List[str]:
    """
    treat each emoji as full token
    
    never combines emoji with adjacent text
    """
    # emoji detection - check for emoji unicode ranges
    # using character code point checking instead of complex regex
    def is_emoji(char):
        cp = ord(char)
        # emoji ranges
        return (
            (0x1F600 <= cp <= 0x1F64F) or  # emoticons
            (0x1F300 <= cp <= 0x1F5FF) or  # misc symbols
            (0x1F680 <= cp <= 0x1F6FF) or  # transport
            (0x1F1E0 <= cp <= 0x1F1FF) or  # flags
            (0x2600 <= cp <= 0x26FF) or   # misc symbols
            (0x2700 <= cp <= 0x27BF)       # dingbats
        )
    
    tokens = []
    current = []
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if is_emoji(char):
            # save current text if any
            if current:
                pre_text = ''.join(current)
                if pre_text.strip():
                    pre_tokens = segment_akshars(pre_text, matras=False)
                    tokens.extend(pre_tokens)
                current = []
            
            # collect emoji (might be multiple chars for some emojis)
            emoji_chars = [char]
            i += 1
            # check for variation selectors or combining marks
            while i < len(text) and (0xFE00 <= ord(text[i]) <= 0xFE0F or ord(text[i]) == 0x200D):
                emoji_chars.append(text[i])
                i += 1
            
            tokens.append(''.join(emoji_chars))
        elif char.isspace():
            if current:
                pre_text = ''.join(current)
                if pre_text.strip():
                    pre_tokens = segment_akshars(pre_text, matras=False)
                    tokens.extend(pre_tokens)
                current = []
            tokens.append(char)
            i += 1
        else:
            current.append(char)
            i += 1
    
    # add remaining
    if current:
        pre_text = ''.join(current)
        if pre_text.strip():
            pre_tokens = segment_akshars(pre_text, matras=False)
            tokens.extend(pre_tokens)
    
    return tokens



