"""
Normalization utilities for Hindi/Sanskrit/Hinglish text.

We keep Devanagari intact while lightly normalizing Roman script and cleaning
social-media style noise. This is intentionally conservative to avoid breaking
conjuncts or script-specific semantics.
"""

import unicodedata
import regex as re


def normalize_unicode(text):
    """Apply NFC Unicode normalization.
    
    We use NFC because NFD can break conjunct shaping in Indic scripts.
    """
    return unicodedata.normalize('NFC', text)


def semantic_normalize(text):
    """Lowercase Roman characters but keep Indic scripts unchanged.
    
    Parameters
    ----------
    text : str
        Mixed-script input.
    
    Returns
    -------
    str
        Lowercased only for characters whose Unicode name contains 'LATIN'.
    """
    result = []
    for char in text:
        try:
            cname = unicodedata.name(char, '')
            if 'LATIN' in cname:
                result.append(char.lower())
            else:
                result.append(char)
        except ValueError:
            # some chars dont have names idk why
            result.append(char)
    return ''.join(result)


def remove_elongations(text):
    """Collapse 3+ repeated characters to 1 (keep doubles).
    
    Examples
    --------
        >>> remove_elongations("yaaaaar")
        'yaar'
    """
    return re.sub(r'(.)\1{2,}', r'\1', text)


def roman_phonetic_signature(word):
    """
    Compute a crude phonetic signature for Roman Hinglish variants.
    
    Examples
    --------
        >>> roman_phonetic_signature("nahee")
        'nahi'
    """
    w = word.lower()
    w = remove_elongations(w)
    
    # common hinglish patterns i noticed
    # TODO: maybe add more? check corpus for patterns
    replacements = [
        (r'ee$', 'i'),    # long i
        (r'oo$', 'u'),    # long u  
        (r'aa', 'a'),     
        (r'kh', 'k'),     # aspirated stuff
        (r'gh', 'g'),
        (r'ch', 'c'),
        (r'th', 't'),
        (r'ph', 'p'),
        (r'bh', 'b'),
        (r'dh', 'd'),
    ]
    
    for pat, repl in replacements:
        w = re.sub(pat, repl, w)
    
    return w


def filter_garbage(text):
    """Drop characters outside a conservative allowlist for noisy inputs.
    
    This keeps Devanagari, basic punctuation, ASCII alnum, and whitespace.
    """
    allowed = re.compile(
        r'[\u0900-\u097F'  # devanagari
        r'\u0980-\u09FF'   # bengali (sometimes see this mixed in)
        r'a-zA-Z0-9'       
        r'\s'              
        r'.,!?;:\'\"\-]'   
    )
    
    # might be slow for long texts but works
    cleaned = ''.join(c for c in text if allowed.match(c))
    return cleaned


def normalize_hinglish(text):
    """Clean up Hinglish text (garbage filter + elongation removal)."""
    text = filter_garbage(text)
    text = remove_elongations(text)
    return text


def normalize_text(text, normalize_roman=True, clean_hinglish=True):
    """
    Main normalization function used by the tokenizer.
    
    Steps:
      1) NFC unicode normalization
      2) Roman lowercasing (optional)
      3) Hinglish cleanup (optional)
    
    Parameters
    ----------
    text : str
        Input string.
    normalize_roman : bool
        If True, lowercase Roman letters only.
    clean_hinglish : bool
        If True, apply lightweight social-text cleanup.
    
    Returns
    -------
    str
        Normalized string.
    """
    text = normalize_unicode(text)
    
    if normalize_roman:
        text = semantic_normalize(text)
    
    if clean_hinglish:
        text = normalize_hinglish(text)
    
    return text

