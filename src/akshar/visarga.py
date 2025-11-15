"""
visarga condition handling
visarga behaves differently before sibilants or vowels
"""

import regex as re
from typing import List, Tuple, Dict


def handle_visarga_conditions(text: str) -> List[Tuple[int, str, str]]:
    """
    detect and annotate visarga behavior
    
    returns list of (position, original, transformation) tuples
    does not modify text, only annotates
    """
    annotations = []
    
    # visarga before sibilants (श, ष, स)
    visarga_sibilant = re.compile(r'ः([शषस])', re.UNICODE)
    for match in visarga_sibilant.finditer(text):
        sibilant = match.group(1)
        # visarga + sibilant -> sibilant with halant
        transformed = sibilant + '्'
        annotations.append((match.start(), 'ः' + sibilant, transformed))
    
    # visarga before vowels
    visarga_vowel = re.compile(r'ः([अ-औ])', re.UNICODE)
    for match in visarga_vowel.finditer(text):
        vowel = match.group(1)
        # visarga + vowel -> potential sandhi boundary
        annotations.append((match.start(), 'ः' + vowel, 'sandhi_boundary'))
    
    return annotations


def annotate_visarga(text: str) -> Dict:
    """
    annotate visarga conditions without modifying text
    
    returns dict with original and annotations
    """
    annotations = handle_visarga_conditions(text)
    
    return {
        'original': text,
        'visarga_annotations': annotations,
        'has_visarga': 'ः' in text
    }

