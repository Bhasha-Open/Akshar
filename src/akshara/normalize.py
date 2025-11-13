"""
Text normalization for hindi/sanskrit/hinglish mix.

handles unicode stuff, lowercasing latin, and cleaning up 
the messy hinglish text you get from twitter etc
"""

import unicodedata
import regex as re


def normalize_unicode(text):
    # just use NFC, seems to work fine
    # tried NFD before but it breaks some conjuncts
    return unicodedata.normalize('NFC', text)


def semantic_normalize(text):
    """lowercase english but keep devanagari as-is"""
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
    # handles "heyyy" -> "hey", "yaaaaar" -> "yaar" etc
    # keep doubles tho, cuz "book" vs "bok" matters
    return re.sub(r'(.)\1{2,}', r'\1', text)


def roman_phonetic_signature(word):
    """
    phonetic sig for roman text - helps match hinglish variants
    eg: nahi/nahii/nahee all map to same sig
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
    # remove weird chars from social media - emojis, special unicode etc
    # keep basic stuff only
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
    """clean up hinglish text - remove elongations, garbage chars"""
    text = filter_garbage(text)
    text = remove_elongations(text)
    return text


def normalize_text(text, normalize_roman=True, clean_hinglish=True):
    """
    main normalization func
    
    does: unicode norm -> lowercase english -> clean hinglish stuff
    """
    text = normalize_unicode(text)
    
    if normalize_roman:
        text = semantic_normalize(text)
    
    if clean_hinglish:
        text = normalize_hinglish(text)
    
    return text

