"""
Transliteration helpers.

We provide a minimal mapping for Devanagari → IAST as a demonstration and keep
the API open for adding other schemes (e.g., ITRANS) without magic.
"""

from typing import Dict, List, Tuple


# basic devanagari to IAST mapping
DEVANAGARI_TO_IAST = {
    'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'ङ': 'ṅa',
    'च': 'ca', 'छ': 'cha', 'ज': 'ja', 'झ': 'jha', 'ञ': 'ña',
    'ट': 'ṭa', 'ठ': 'ṭha', 'ड': 'ḍa', 'ढ': 'ḍha', 'ण': 'ṇa',
    'त': 'ta', 'थ': 'tha', 'द': 'da', 'ध': 'dha', 'न': 'na',
    'प': 'pa', 'फ': 'pha', 'ब': 'ba', 'भ': 'bha', 'म': 'ma',
    'य': 'ya', 'र': 'ra', 'ल': 'la', 'व': 'va',
    'श': 'śa', 'ष': 'ṣa', 'स': 'sa', 'ह': 'ha',
    'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū',
    'ऋ': 'ṛ', 'ॠ': 'ṝ', 'ऌ': 'ḷ', 'ए': 'e', 'ऐ': 'ai',
    'ओ': 'o', 'औ': 'au',
}


def token_to_iast(token: str) -> str:
    """
    Convert a Devanagari token into IAST.
    
    Notes
    -----
    This is a simplified routine; matra handling covers the common cases only.
    """
    result = []
    i = 0
    
    while i < len(token):
        char = token[i]
        
        # check for matras
        if i + 1 < len(token):
            # check for vowel signs
            next_char = token[i + 1]
            if next_char in 'ा-ौ':
                # consonant + matra
                if char in DEVANAGARI_TO_IAST:
                    base = DEVANAGARI_TO_IAST[char][:-1]  # remove 'a'
                    matra_map = {
                        'ा': 'ā', 'ि': 'i', 'ी': 'ī', 'ु': 'u', 'ू': 'ū',
                        'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au'
                    }
                    if next_char in matra_map:
                        result.append(base + matra_map[next_char])
                        i += 2
                        continue
        
        # direct mapping
        if char in DEVANAGARI_TO_IAST:
            result.append(DEVANAGARI_TO_IAST[char])
        else:
            result.append(char)
        
        i += 1
    
    return ''.join(result)


def transliterate_tokens(tokens: List[str], scheme: str = 'iast') -> List[str]:
    """
    Transliterate a token sequence to a given scheme.
    
    Parameters
    ----------
    tokens : List[str]
        Input tokens (likely akshar- or model-level).
    scheme : str
        'iast' currently supported.
    
    Returns
    -------
    List[str]
        Transliteration output, length-preserving to the extent possible.
    """
    if scheme.lower() == 'iast':
        return [token_to_iast(t) for t in tokens]
    else:
        # fallback: return as-is
        return tokens

