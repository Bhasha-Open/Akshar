"""
schwa deletion modeling for hindi
predicts where inherent vowels are dropped in pronunciation
"""

import regex as re
from typing import List, Tuple, Dict


def predict_schwa_deletion(word: str) -> List[int]:
    """
    predict positions where schwa deletion occurs in hindi
    
    returns list of character positions where schwa would be deleted
    does not modify the text, only annotates positions
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
    annotate schwa deletion positions for each word
    
    returns list of (word, deletion_positions) tuples
    """
    words = text.split()
    result = []
    
    for word in words:
        deletions = predict_schwa_deletion(word)
        result.append((word, deletions))
    
    return result

