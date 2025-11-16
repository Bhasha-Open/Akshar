"""
Sandhi detection and non-destructive boundary marking.

We offer simple heuristics for likely sandhi positions in Sanskrit/Hindi text.
Use this to annotate or visualize where phonological boundaries may be present
without rewriting the underlying text.
"""

import regex as re
from typing import List, Tuple, Dict


def detect_sandhi_boundaries(text: str) -> List[Tuple[int, str]]:
    """
    Detect likely sandhi boundaries using a few common patterns.
    
    Parameters
    ----------
    text : str
        Input Devanagari text.
    
    Returns
    -------
    List[Tuple[int, str]]
        Sorted list of (position, boundary_type) markers.
    """
    boundaries = []
    
    # common sandhi patterns
    # visarga + vowel -> potential boundary
    visarga_vowel = re.compile(r'ः([अ-औ])', re.UNICODE)
    for match in visarga_vowel.finditer(text):
        boundaries.append((match.start(), 'visarga_vowel'))
    
    # anusvara + consonant -> potential boundary
    anusvara_cons = re.compile(r'ं([क-ह])', re.UNICODE)
    for match in anusvara_cons.finditer(text):
        boundaries.append((match.start(), 'anusvara_cons'))
    
    # vowel + vowel -> potential sandhi
    vowel_vowel = re.compile(r'([अ-औ])([अ-औ])', re.UNICODE)
    for match in vowel_vowel.finditer(text):
        boundaries.append((match.start() + 1, 'vowel_vowel'))
    
    return sorted(boundaries, key=lambda x: x[0])


def mark_sandhi_boundaries(text: str) -> str:
    """
    Insert zero-width markers at detected sandhi boundaries.
    
    Returns
    -------
    str
        Same string but with zero-width spaces at boundary positions.
    """
    boundaries = detect_sandhi_boundaries(text)
    if not boundaries:
        return text
    
    # insert markers (using zero-width space for non-destructive marking)
    result = list(text)
    offset = 0
    for pos, btype in boundaries:
        # use invisible marker
        result.insert(pos + offset, '\u200B')  # zero-width space
        offset += 1
    
    return ''.join(result)

