"""
Visarga behavior annotations.

Visarga behaves differently before sibilants and vowels. We provide annotations
to capture these contexts without rewriting input.
"""

import regex as re
from typing import List, Tuple, Dict


def handle_visarga_conditions(text: str) -> List[Tuple[int, str, str]]:
    """
    Detect and annotate visarga behavior around sibilants and vowels.
    
    Returns
    -------
    List[Tuple[int, str, str]]
        (position, original_span, transformation_label) tuples.
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
    Annotate visarga-related contexts without modifying the text.
    
    Returns
    -------
    Dict
        original, annotations, and a boolean 'has_visarga'.
    """
    annotations = handle_visarga_conditions(text)
    
    return {
        'original': text,
        'visarga_annotations': annotations,
        'has_visarga': 'ः' in text
    }

