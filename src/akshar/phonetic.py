"""
Phonetic analysis utilities for Indic scripts (focus: Devanagari).

This module loads a compact phonetic property table (from
``resources/all_script_phonetic_data.csv``) and exposes a small analyzer
to answer questions like "is this consonant aspirated?" or "how many
nasals are in this word?".

The analyzer aims to be predictable rather than exhaustive; if a
character is missing in the CSV we simply return falsy/None instead
of guessing.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional


class PhoneticAnalyzer:
    """Light-weight phonetic analyzer for Devanagari.

    The analyzer keeps a map of character → properties (aspirated, voiced,
    nasal, place of articulation, etc.) loaded from a static CSV. Callers
    typically keep a singleton around for repeated queries.

    Examples:
        Basic usage:

        >>> from akshar.phonetic import PhoneticAnalyzer
        >>> pa = PhoneticAnalyzer()
        >>> pa.is_consonant("क")
        True
        >>> pa.is_aspirated("ख")
        True
        >>> pa.get_place_of_articulation("ट")
        'retroflex'
        >>> pa.analyze_word("भारत")
        {'vowels': 2, 'consonants': 3, 'aspirated': 0, 'nasals': 0, 'total_chars': 5}
    """
    
    def __init__(self):
        self.char_props = {}
        self._load_data()
    
    def _load_data(self):
        """Populate the internal property map from CSV.

        The CSV is expected to have boolean columns like ``is_vowel``,
        ``aspirated``, and articulatory columns like ``velar``.
        Missing file is tolerated (the analyzer will just return defaults).
        """
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
        """Return the phonetic property dict for a single character.

        Args:
            char: Single Devanagari character.

        Returns:
            Dict with boolean flags like ``is_vowel``, ``is_consonant``,
            ``aspirated``, ``voiced``, plus place flags (``velar`` etc.);
            ``None`` if the character is unknown.

        Examples:
            >>> from akshar.phonetic import PhoneticAnalyzer
            >>> PhoneticAnalyzer().get_properties("क")["is_consonant"]
            True
        """
        return self.char_props.get(char)
    
    def is_vowel(self, char: str) -> bool:
        """Whether the character is a vowel.

        Args:
            char: Single Devanagari character.

        Returns:
            True if marked as vowel in the data; False otherwise.
        """
        props = self.get_properties(char)
        return props['is_vowel'] if props else False
    
    def is_consonant(self, char: str) -> bool:
        """Whether the character is a consonant.

        Args:
            char: Single Devanagari character.

        Returns:
            True if marked as consonant in the data; False otherwise.
        """
        props = self.get_properties(char)
        return props['is_consonant'] if props else False
    
    def is_aspirated(self, char: str) -> bool:
        """Whether the consonant is aspirated.

        Args:
            char: Single Devanagari consonant (others return False).

        Returns:
            True if character is aspirated; False if unknown or not aspirated.
        """
        # We keep a small in-code hint to make intent obvious while reading.
        props = self.get_properties(char)
        return props['aspirated'] if props else False
    
    def is_voiced(self, char: str) -> bool:
        """Whether the character is voiced.

        Args:
            char: Single Devanagari character.

        Returns:
            True if character is voiced; False otherwise.
        """
        props = self.get_properties(char)
        return props['voiced'] if props else False
    
    def is_nasal(self, char: str) -> bool:
        """Whether the character is nasal.

        Args:
            char: Single Devanagari character.

        Returns:
            True if character is nasal; False otherwise.
        """
        props = self.get_properties(char)
        return props['nasal'] if props else False
    
    def get_place_of_articulation(self, char: str) -> Optional[str]:
        """Place of articulation for the character, if known.

        The check is ordered: velar → palatal → retroflex → dental → labial.

        Args:
            char: Single Devanagari character.

        Returns:
            One of ``'velar'``, ``'palatal'``, ``'retroflex'``, ``'dental'``,
            ``'labial'``; ``None`` if not applicable or unknown.
        """
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
        """Summarize phonetic counts for a word (character-wise).

        Args:
            word: Devanagari string to analyze. We iterate characters naïvely;
                  grapheme-level handling is left to the caller if needed.

        Returns:
            Dict with keys:
            - ``vowels``: number of vowel characters
            - ``consonants``: number of consonant characters
            - ``aspirated``: number of aspirated consonants
            - ``nasals``: number of nasal consonants
            - ``total_chars``: length of input string (Python ``len``)

        Examples:
            >>> from akshar.phonetic import PhoneticAnalyzer
            >>> PhoneticAnalyzer().analyze_word("खग")
            {'vowels': 0, 'consonants': 2, 'aspirated': 1, 'nasals': 0, 'total_chars': 2}
        """
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
    """Return a process-local singleton analyzer instance.

    Returns:
        A cached ``PhoneticAnalyzer``. The CSV is loaded on first access.

    Examples:
        >>> from akshar.phonetic import get_phonetic_analyzer
        >>> pa = get_phonetic_analyzer()
        >>> pa.is_consonant("क")
        True
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = PhoneticAnalyzer()
    return _analyzer


def analyze_phonetics(text: str) -> Dict:
    """Convenience wrapper over ``PhoneticAnalyzer.analyze_word``.

    Args:
        text: Devanagari string to analyze character-wise.

    Returns:
        Same structure as :meth:`PhoneticAnalyzer.analyze_word`.

    Examples:
        >>> from akshar.phonetic import analyze_phonetics
        >>> analyze_phonetics("भारत")
        {'vowels': 2, 'consonants': 3, 'aspirated': 0, 'nasals': 0, 'total_chars': 5}
    """
    return get_phonetic_analyzer().analyze_word(text)

