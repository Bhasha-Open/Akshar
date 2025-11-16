"""
Anusvāra handling for Devanagari.

Resolves anusvāra (ं) to an appropriate homorganic nasal based on the following
consonant’s place of articulation. We return both forms so callers can decide
how aggressive they want to be when rewriting.
"""

import regex as re
from typing import Dict, Tuple, List


# nasal mappings based on place of articulation
NASAL_MAP = {
    'velar': 'ङ',      # before क, ख, ग, घ
    'palatal': 'ञ',    # before च, छ, ज, झ
    'retroflex': 'ण',  # before ट, ठ, ड, ढ
    'dental': 'न',     # before त, थ, द, ध
    'labial': 'म',     # before प, फ, ब, भ
}


def get_nasal_for_consonant(cons: str) -> str:
    """Return the homorganic nasal for a given consonant.
    
    Parameters
    ----------
    cons : str
        Single Devanagari consonant.
    
    Returns
    -------
    str
        One of 'ङ', 'ञ', 'ण', 'न', 'म' or 'ं' as fallback.
    """
    cp = ord(cons) if cons else 0
    
    # velar: क-घ (0x0915-0x0918)
    if 0x0915 <= cp <= 0x0918:
        return NASAL_MAP['velar']
    
    # palatal: च-झ (0x091A-0x091D)
    if 0x091A <= cp <= 0x091D:
        return NASAL_MAP['palatal']
    
    # retroflex: ट-ढ (0x091F-0x0922)
    if 0x091F <= cp <= 0x0922:
        return NASAL_MAP['retroflex']
    
    # dental: त-ध (0x0924-0x0927)
    if 0x0924 <= cp <= 0x0927:
        return NASAL_MAP['dental']
    
    # labial: प-भ (0x092A-0x092D)
    if 0x092A <= cp <= 0x092D:
        return NASAL_MAP['labial']
    
    # default to anusvara
    return 'ं'


def resolve_anusvara(text: str, store_both: bool = True) -> Dict[str, str]:
    """
    Resolve anusvāra (ं) into a homorganic nasal, conservatively.
    
    Parameters
    ----------
    text : str
        Input string.
    store_both : bool
        If True, return both 'original' and 'resolved' (non-destructive).
    
    Returns
    -------
    Dict[str, str]
        Mapping with 'original' and 'resolved' keys (or only 'resolved').
    
    Examples
    --------
        >>> resolve_anusvara("संस्कृत")
        {'original': 'संस्कृत', 'resolved': 'संसकृत'}  # example, depends on following consonant
    """
    original = text
    resolved = text
    
    # find anusvara followed by consonant
    pattern = re.compile(r'ं([क-ह])', re.UNICODE)
    
    matches = list(pattern.finditer(text))
    if matches:
        # build resolved version
        result = list(text)
        offset = 0
        
        for match in reversed(matches):
            cons = match.group(1)
            nasal = get_nasal_for_consonant(cons)
            pos = match.start() + offset
            result[pos] = nasal
        
        resolved = ''.join(result)
    
    if store_both:
        return {
            'original': original,
            'resolved': resolved
        }
    else:
        return {'resolved': resolved}

