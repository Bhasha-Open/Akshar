"""
Segmentation utilities: akshar-level splits and code-switch detection.

We keep Devanagari grapheme clusters intact (e.g., क्ष, ज्ञ) and expose helpers
for measuring composition and locating script switches in mixed Hinglish text.
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
    """Return True if the char is a Devanagari matra (vowel sign).

    Notes
    -----
    This excludes the halant (virama) which participates in conjuncts.
    """
    cp = ord(char)
    for start, end in MATRA_RANGES:
        if start <= cp <= end:
            return True
    return False


def segment_akshars(text, matras=False, separate_matras=None):
    """
    Split text into akshars (Unicode grapheme clusters).
    
    Parameters
    ----------
    text:
        Input string (any script).
    matras:
        If True, separate matras (vowel signs) and halants from bases inside each
        grapheme cluster. If False, keep clusters intact (recommended).
    separate_matras:
        Deprecated alias for ``matras``; kept for backward compatibility.
    
    Returns
    -------
    list[str]
        Sequence of akshars or parts (if ``matras=True``).
    
    Examples
    --------
    Default (preserve clusters):
        >>> segment_akshars("मौसम")
        ['मौ', 'स', 'म']
        
    Separate matras:
        >>> segment_akshars("मौसम", matras=True)
        ['म', 'ौ', 'स', 'म']
        
    Separate conjuncts and matras:
        >>> segment_akshars("च्छा", matras=True)
        ['च', '्', 'छ', 'ा']
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
    """Classify a single character as 'devanagari', 'roman', 'digit', 'punct', or 'other'."""
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
    Chunk text by script and return labeled segments.
    
    Parameters
    ----------
    text:
        Input string, possibly mixed scripts (Hinglish).
    
    Returns
    -------
    list[tuple[str, str]]
        List of (segment, script_label) where script_label ∈
        {'devanagari','roman','digit','punct','other'}.
    
    Examples
    --------
        >>> detect_code_switches(\"aaj मौसम\")
        [('aaj ', 'roman'), ('मौसम', 'devanagari')]
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
    """Split text on script boundaries (helper used for data prep)."""
    switches = detect_code_switches(text)
    return [seg for seg, _ in switches]


def analyze_text_composition(text):
    """
    Compute simple composition stats for a normalized string.

    Returns
    -------
    dict
        - akshar_count
        - script_switches (n segments - 1)
        - devanagari_ratio
        - roman_ratio
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
    Word-level tokenization for Hindi with optional morphology.
    
    Parameters
    ----------
    text:
        Hindi text to tokenize.
    use_morphology:
        If True and Morfessor model is available, use it to split words.
    
    Returns
    -------
    List[str]
        Word tokens (danda/double danda kept separate).
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
    Word-level tokenization for Sanskrit with light heuristics.
    
    Parameters
    ----------
    text:
        Sanskrit text to tokenize.
    use_morphology:
        If True and Morfessor is available, use it.
    
    Returns
    -------
    List[str]
        Word tokens, keeping danda/double danda standalone.
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
    Word tokenization with basic language routing.
    
    Parameters
    ----------
    text:
        Text to tokenize.
    language:
        'hindi', 'sanskrit', or 'auto' (default). Auto uses a simple heuristic.
    use_morphology:
        If True, use morphology when available.
    
    Returns
    -------
    List[str]
        Word tokens.
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

