"""
Vedic/Sanskrit helpers: svara marks, metre, and danda punctuation.
"""

import regex as re
from typing import List, Tuple, Dict


# svara marks (vedic accent marks)
SVARA_MARKS = [
    0x0950,  # ऐ
    0x0951,  # ॑ (udatta)
    0x0952,  # ॒ (anudatta)
    0x0953,  # ॓
    0x0954,  # ॔
]


def is_svara_mark(char: str) -> bool:
    """Return True if the character is a Vedic svara mark."""
    return ord(char) in SVARA_MARKS


def preserve_svara_marks(text: str) -> List[str]:
    """
    Segment text while keeping svara marks attached to base syllables.
    """
    segments = []
    current = []
    i = 0
    
    while i < len(text):
        char = text[i]
        
        if is_svara_mark(char):
            # attach to current syllable
            current.append(char)
            i += 1
        elif char.isspace():
            if current:
                segments.append(''.join(current))
                current = []
            i += 1
        else:
            # check if next char is svara
            if i + 1 < len(text) and is_svara_mark(text[i + 1]):
                current.append(char)
                current.append(text[i + 1])
                i += 2
            else:
                current.append(char)
                i += 1
    
    if current:
        segments.append(''.join(current))
    
    return segments


def handle_sanskrit_punctuation(text: str) -> List[str]:
    """
    Split on danda (।) and double danda (॥) and return them as standalone tokens.
    """
    # split on dandas but keep them as separate tokens
    parts = re.split(r'([।॥])', text)
    
    result = []
    for part in parts:
        if part in ['।', '॥']:
            result.append(part)
        elif part.strip():
            # split remaining text on whitespace
            words = part.split()
            result.extend(words)
    
    return [r for r in result if r]


def count_mora(syllable: str) -> int:
    """
    Count mora weight for a syllable: 1=light, 2=heavy (coarse rule-of-thumb).
    """
    # heavy if ends with long vowel, anusvara, visarga, or consonant cluster
    if re.search(r'[ा-ौंः]$|[क-ह]्[क-ह]$', syllable):
        return 2
    return 1


def analyze_metre(text: str) -> Dict:
    """
    Analyze light/heavy syllable counts for a simplistic metrical view.
    """
    syllables = preserve_svara_marks(text)
    
    mora_counts = [count_mora(syl) for syl in syllables if syl.strip()]
    
    return {
        'syllables': syllables,
        'mora_counts': mora_counts,
        'total_mora': sum(mora_counts),
        'light_syllables': sum(1 for m in mora_counts if m == 1),
        'heavy_syllables': sum(1 for m in mora_counts if m == 2),
    }

