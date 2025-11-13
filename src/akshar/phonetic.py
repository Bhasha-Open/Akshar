"""
phonetic analysis - loads csv with phonetic props for devanagari
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional


class PhoneticAnalyzer:
    """analyze phonetics - aspirated, voiced, nasal etc"""
    
    def __init__(self):
        self.char_props = {}
        self._load_data()
    
    def _load_data(self):
        """load phonetic CSV - got this from indic_nlp_resources"""
        res_dir = Path(__file__).parent / "resources"
        pfile = res_dir / "all_script_phonetic_data.csv"
        
        if not pfile.exists():
            return
        
        # tried caching this in pickle but csv is fast enough
        with open(pfile, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ch = row['Devanagari']
                self.char_props[ch] = {
                    'itrans': row['ITRANS'],
                    'is_vowel': row['is_vowel'] == '1',
                    'is_consonant': row['is_consonant'] == '1',
                    'nukta': row['nukta'] == '1',
                    'halanta': row['halanta'] == '1',
                    'anusvara': row['anusvara'] == '1',
                    'aspirated': row['aspirated'] == '1',
                    'voiced': row['voiced'] == '1',
                    'nasal': row['nasal'] == '1',
                    'velar': row['velar'] == '1',
                    'palatal': row['palatal'] == '1',
                    'retroflex': row['retroflex'] == '1',
                    'dental': row['dental'] == '1',
                    'labial': row['labial'] == '1',
                }
    
    def get_properties(self, char: str) -> Optional[Dict]:
        """get phonetic props for a char"""
        return self.char_props.get(char)
    
    def is_vowel(self, char: str) -> bool:
        props = self.get_properties(char)
        return props['is_vowel'] if props else False
    
    def is_consonant(self, char: str) -> bool:
        props = self.get_properties(char)
        return props['is_consonant'] if props else False
    
    def is_aspirated(self, char: str) -> bool:
        # ख, घ, छ, झ, ठ, ढ, थ, ध, फ, भ
        props = self.get_properties(char)
        return props['aspirated'] if props else False
    
    def is_voiced(self, char: str) -> bool:
        props = self.get_properties(char)
        return props['voiced'] if props else False
    
    def is_nasal(self, char: str) -> bool:
        # न, म, ङ, ञ, ण
        props = self.get_properties(char)
        return props['nasal'] if props else False
    
    def get_place_of_articulation(self, char: str) -> Optional[str]:
        """where in mouth the sound is made"""
        props = self.get_properties(char)
        if not props:
            return None
        
        # check in order
        if props['velar']:
            return 'velar'
        elif props['palatal']:
            return 'palatal'
        elif props['retroflex']:
            return 'retroflex'
        elif props['dental']:
            return 'dental'
        elif props['labial']:
            return 'labial'
        
        return None
    
    def analyze_word(self, word: str) -> Dict:
        """count vowels/consonants/nasals etc in word"""
        vcnt = 0
        ccnt = 0
        acnt = 0
        ncnt = 0
        
        for ch in word:
            if self.is_vowel(ch):
                vcnt += 1
            elif self.is_consonant(ch):
                ccnt += 1
                if self.is_aspirated(ch):
                    acnt += 1
                if self.is_nasal(ch):
                    ncnt += 1
        
        return {
            'vowels': vcnt,
            'consonants': ccnt,
            'aspirated': acnt,
            'nasals': ncnt,
            'total_chars': len(word)
        }


# global singleton - lazy init
_analyzer = None

def get_phonetic_analyzer() -> PhoneticAnalyzer:
    """get the analyzer (singleton)"""
    global _analyzer
    if _analyzer is None:
        _analyzer = PhoneticAnalyzer()
    return _analyzer


def analyze_phonetics(text: str) -> Dict:
    """quick phonetic analysis of text"""
    return get_phonetic_analyzer().analyze_word(text)

