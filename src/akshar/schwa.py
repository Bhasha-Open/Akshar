"""
Schwa-deletion modeling for Hindi.

We annotate positions where an inherent vowel is likely dropped in pronunciation.
This is strictly non-destructive — we mark positions but do not rewrite text.
"""

import regex as re
from typing import List, Tuple, Dict


def predict_schwa_deletion(word: str) -> List[int]:
    """
    Predict likely schwa deletion positions in a word.
    
    Parameters
    ----------
    word : str
        Single word (Devanagari).
    
    Returns
    -------
    List[int]
        Sorted unique indices where schwa is commonly dropped.
    """
    deletions = []
    
    # schwa deletion rules for hindi
    # final consonant clusters often drop schwa
    # pattern: consonant + halant + consonant at end
    final_cluster = re.compile(r'([क-ह])्([क-ह])([^क-ह]*)$', re.UNICODE)
    if final_cluster.search(word):
        # schwa before final cluster likely deleted
        match = final_cluster.search(word)
        if match:
            deletions.append(match.start(1))
    
    # medial consonant clusters
    # pattern: C + halant + C (not at word boundary)
    medial_cluster = re.compile(r'([क-ह])्([क-ह])', re.UNICODE)
    for match in medial_cluster.finditer(word):
        pos = match.start(1)
        # not at start or end
        if pos > 0 and match.end(2) < len(word):
            deletions.append(pos)
    
    return sorted(set(deletions))


def annotate_schwa_deletions(text: str) -> List[Tuple[str, List[int]]]:
    """
    Annotate schwa-deletion positions for each whitespace-delimited token.
    
    Returns
    -------
    List[Tuple[str, List[int]]]
        Pairs of (word, deletion_indices).
    """
    words = text.split()
    result = []
    
    for word in words:
        deletions = predict_schwa_deletion(word)
        result.append((word, deletions))
    
    return result

