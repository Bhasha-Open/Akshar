"""
akshar segmentation + code-switch detection

keeps devanagari clusters together (क्ष, ज्ञ etc) and 
finds where script changes in hinglish text
"""

import regex as re
import unicodedata
from typing import List, Tuple, Dict


# regex \X matches full grapheme clusters - neat trick
akshar_PAT = re.compile(r'\X', re.UNICODE)

# Devanagari matras (vowel signs) - ranges from Unicode spec
# 0x0900-0x0902: anusvara, visarga
# 0x093E-0x094C: vowel signs (ा, ि, ी, ु, ू, े, ै, ो, ौ, etc)
# Note: halant (्, 0x094D) is NOT a matra - it's part of conjunct formation
MATRA_RANGES = [
    (0x0900, 0x0902),  # anusvara, visarga
    (0x093E, 0x094C),  # vowel signs
    (0x0951, 0x0954),  # additional marks
]

def is_matra(char):
    """check if char is a devanagari matra (vowel sign) - excludes halant"""
    cp = ord(char)
    for start, end in MATRA_RANGES:
        if start <= cp <= end:
            return True
    return False


def segment_akshars(text, matras=False, separate_matras=None):
    """
    split into akshars (grapheme clusters)
    
    Args:
        text: input text
        matras: if True, separate matras (vowel signs) and conjuncts from consonants.
                splits conjuncts like च्छ into ['च', '्', 'छ'] and matras like मौ into ['म', 'ौ']
        separate_matras: deprecated, use 'matras' instead. kept for backward compatibility
    
    Returns:
        list of akshar segments
    
    Examples:
        >>> segment_akshars("मौसम")
        ['मौ', 'स', 'म']  # default: preserves grapheme clusters
        
        >>> segment_akshars("मौसम", matras=True)
        ['म', 'ौ', 'स', 'म']  # separates matras
        
        >>> segment_akshars("च्छा", matras=True)
        ['च', '्', 'छ', 'ा']  # separates conjuncts and matras
    """
    # handle deprecated parameter
    if separate_matras is not None:
        matras = separate_matras
    
    if not matras:
        return akshar_PAT.findall(text)
    
    # get grapheme clusters first
    clusters = akshar_PAT.findall(text)
    
    # now split matras and halants from each cluster
    result = []
    HALANT = 0x094D  # ्
    
    for cluster in clusters:
        if not cluster:
            continue
        
        # split cluster into parts: base chars, halants, matras
        parts = []
        current = []
        
        for char in cluster:
            cp = ord(char)
            
            if is_matra(char):
                # save current base if any
                if current:
                    parts.append(''.join(current))
                    current = []
                # add matra as separate part
                parts.append(char)
            elif cp == HALANT:
                # save current base if any
                if current:
                    parts.append(''.join(current))
                    current = []
                # add halant as separate part
                parts.append(char)
            else:
                current.append(char)
        
        # add remaining base
        if current:
            parts.append(''.join(current))
        
        # if we split, add all parts; otherwise add original cluster
        if parts:
            result.extend(parts)
        else:
            result.append(cluster)
    
    return result


def identify_script(char):
    """figure out if char is devanagari, roman, digit, etc"""
    cp = ord(char)
    
    # devanagari unicode range
    if 0x0900 <= cp <= 0x097F:
        return 'devanagari'
    
    # a-z A-Z
    if (0x0041 <= cp <= 0x005A) or (0x0061 <= cp <= 0x007A):
        return 'roman'
    
    if char.isdigit():
        return 'digit'
    
    # punct/whitespace - dont care about script changes here
    if char in ' .,!?;:\'"()-[]{}':
        return 'punct'
    
    return 'other'


def detect_code_switches(text):
    """
    find where script changes - for hinglish text
    
    returns: [(segment, script_type), ...]
    eg "aaj मौसम" -> [("aaj ", "roman"), ("मौसम", "devanagari")]
    """
    if not text:
        return []
    
    segs = []
    curr_seg = []
    curr_script = None
    
    for ch in text:
        scr = identify_script(ch)
        
        # punct/digits dont count as switches
        if scr in ('punct', 'digit'):
            curr_seg.append(ch)
            continue
        
        if curr_script is None:
            curr_script = scr
            curr_seg.append(ch)
        elif scr == curr_script:
            curr_seg.append(ch)
        else:
            # switched! save current & start new
            if curr_seg:
                segs.append((''.join(curr_seg), curr_script))
            curr_seg = [ch]
            curr_script = scr
    
    # last one
    if curr_seg:
        segs.append((''.join(curr_seg), curr_script))
    
    return segs


def segment_by_script(text):
    """split text purely on script boundaries - used for training data prep"""
    switches = detect_code_switches(text)
    return [seg for seg, _ in switches]


def analyze_text_composition(text):
    """
    get stats about text - how much devanagari vs roman, switches, etc
    """
    akshars = segment_akshars(text)
    switches = detect_code_switches(text)
    
    total = len(text)
    dev_chars = sum(len(s) for s, scr in switches if scr == 'devanagari')
    roman_chars = sum(len(s) for s, scr in switches if scr == 'roman')
    
    # tried normalizing by akshars instead of chars but this works better
    # also tried: total / len(akshars) for density but didnt help much
    return {
        'akshar_count': len(akshars),
        'script_switches': len(switches) - 1,  # n segments = n-1 switches
        'devanagari_ratio': dev_chars / total if total > 0 else 0,
        'roman_ratio': roman_chars / total if total > 0 else 0,
    }


def word_tokenize_hindi(text: str, use_morphology: bool = False) -> List[str]:
    """
    word-level tokenization for hindi text
    
    handles compound words, sandhi, and common hindi patterns
    uses normalization and intelligent word boundary detection
    
    Args:
        text: hindi text to tokenize
        use_morphology: if True, uses morfessor for morphological segmentation
    
    Returns:
        list of word tokens
    """
    from .normalize import normalize_text
    
    # normalize first
    normalized = normalize_text(text, normalize_roman=True, clean_hinglish=True)
    
    if use_morphology:
        from .morph import get_hindi_segmenter
        seg = get_hindi_segmenter()
        if seg.is_model_loaded():
            return seg.segment_text(normalized)
    
    # basic word splitting with some intelligence
    words = []
    current_word = []
    
    # danda and double danda should always be separate tokens
    sanskrit_punct = '।॥'
    other_punct = '.,!?;:()[]{}"\''
    
    for char in normalized:
        if char.isspace():
            if current_word:
                words.append(''.join(current_word))
                current_word = []
        elif char in sanskrit_punct:
            # danda/double danda - end current word and add as separate token
            if current_word:
                words.append(''.join(current_word))
                current_word = []
            words.append(char)  # add danda as separate token
        elif char in other_punct:
            # other punctuation - end current word
            if current_word:
                words.append(''.join(current_word))
                current_word = []
            # optionally add punctuation as token (skip for now)
        else:
            current_word.append(char)
    
    # last word
    if current_word:
        words.append(''.join(current_word))
    
    # filter empty
    return [w for w in words if w]


def word_tokenize_sanskrit(text: str, use_morphology: bool = False) -> List[str]:
    """
    word-level tokenization for sanskrit text
    
    handles sandhi rules, compound words (samasa), and sanskrit-specific patterns
    more complex than hindi due to extensive sandhi rules
    
    Args:
        text: sanskrit text to tokenize
        use_morphology: if True, uses morfessor for morphological segmentation
    
    Returns:
        list of word tokens
    """
    from .normalize import normalize_text
    
    # normalize first
    normalized = normalize_text(text, normalize_roman=True, clean_hinglish=True)
    
    if use_morphology:
        from .morph import get_sanskrit_segmenter
        seg = get_sanskrit_segmenter()
        if seg.is_model_loaded():
            return seg.segment_text(normalized)
    
    # sanskrit word boundaries are more complex
    # basic approach: split on spaces and common sandhi markers
    # for proper sandhi splitting, would need a sandhi analyzer
    
    words = []
    current_word = []
    
    # sanskrit punctuation markers - danda/double danda are special
    sanskrit_punct = '।॥'  # danda and double danda
    other_punct = '.,!?;:()[]{}"\''  # other punctuation
    
    for char in normalized:
        if char.isspace():
            if current_word:
                words.append(''.join(current_word))
                current_word = []
        elif char in sanskrit_punct:
            # danda/double danda - end current word and add as separate token
            if current_word:
                words.append(''.join(current_word))
                current_word = []
            words.append(char)  # add danda as separate token
        elif char in other_punct:
            # other punctuation - end current word
            if current_word:
                words.append(''.join(current_word))
                current_word = []
            # optionally add punctuation as token (skip for now)
        else:
            current_word.append(char)
    
    if current_word:
        words.append(''.join(current_word))
    
    return [w for w in words if w]


def word_tokenize(text: str, language: str = 'auto', use_morphology: bool = False) -> List[str]:
    """
    word-level tokenization with language detection
    
    automatically detects language or uses specified one
    falls back to simple whitespace splitting if language not supported
    
    Args:
        text: text to tokenize
        language: 'hindi', 'sanskrit', 'auto' (default: auto-detect)
        use_morphology: if True, uses morphological segmentation when available
    
    Returns:
        list of word tokens
    """
    if language == 'auto':
        # simple heuristic: check for sanskrit markers
        # could be improved with proper language detection
        if any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in text):
            # has devanagari - try to detect
            # for now, default to hindi
            language = 'hindi'
        else:
            # no devanagari - simple split
            return [w for w in text.split() if w]
    
    if language.lower() in ('hindi', 'hi', 'hin'):
        return word_tokenize_hindi(text, use_morphology=use_morphology)
    elif language.lower() in ('sanskrit', 'sa', 'san', 'skr'):
        return word_tokenize_sanskrit(text, use_morphology=use_morphology)
    else:
        # fallback to simple whitespace split
        return [w for w in text.split() if w]


# experimental: tried clustering similar akshars but too slow
# def cluster_akshars(text):
#     akshars = segment_akshars(text)
#     # group by first char? or phonetic sig?
#     # TODO: revisit this later
#     pass

