"""
akshar segmentation + code-switch detection

keeps devanagari clusters together (क्ष, ज्ञ etc) and 
finds where script changes in hinglish text
"""

import regex as re
from typing import List, Tuple


# regex \X matches full grapheme clusters - neat trick
AKSHARA_PAT = re.compile(r'\X', re.UNICODE)


def segment_aksharas(text):
    """
    split into aksharas (grapheme clusters)
    
    wont break stuff like क्ष or ज्ञ which are multiple unicode points
    but one visual unit
    """
    return AKSHARA_PAT.findall(text)


def identify_script(char):
    """figure out if char is devanagari, roman, digit, etc"""
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
    find where script changes - for hinglish text
    
    returns: [(segment, script_type), ...]
    eg "aaj मौसम" -> [("aaj ", "roman"), ("मौसम", "devanagari")]
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
    """split text purely on script boundaries - used for training data prep"""
    switches = detect_code_switches(text)
    return [seg for seg, _ in switches]


def analyze_text_composition(text):
    """
    get stats about text - how much devanagari vs roman, switches, etc
    """
    aksharas = segment_aksharas(text)
    switches = detect_code_switches(text)
    
    total = len(text)
    dev_chars = sum(len(s) for s, scr in switches if scr == 'devanagari')
    roman_chars = sum(len(s) for s, scr in switches if scr == 'roman')
    
    # tried normalizing by aksharas instead of chars but this works better
    # also tried: total / len(aksharas) for density but didnt help much
    return {
        'akshara_count': len(aksharas),
        'script_switches': len(switches) - 1,  # n segments = n-1 switches
        'devanagari_ratio': dev_chars / total if total > 0 else 0,
        'roman_ratio': roman_chars / total if total > 0 else 0,
    }


# experimental: tried clustering similar aksharas but too slow
# def cluster_aksharas(text):
#     aksharas = segment_aksharas(text)
#     # group by first char? or phonetic sig?
#     # TODO: revisit this later
#     pass

