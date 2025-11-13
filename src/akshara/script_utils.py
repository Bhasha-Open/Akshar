"""
script utils - detect which indic script text is in
"""

from typing import Dict, List
import unicodedata


class ScriptAnalyzer:
    """check what script chars belong to"""
    
    # unicode ranges - looked these up from unicode.org
    SCRIPT_RANGES = {
        'devanagari': (0x0900, 0x097F),
        'bengali': (0x0980, 0x09FF),
        'gujarati': (0x0A80, 0x0AFF),
        'gurmukhi': (0x0A00, 0x0A7F),
        'tamil': (0x0B80, 0x0BFF),
        'telugu': (0x0C00, 0x0C7F),
        'kannada': (0x0C80, 0x0CFF),
        'malayalam': (0x0D00, 0x0D7F),
    }
    # TODO: add more scripts? oriya, sinhala etc
    
    def identify_scripts(self, text: str) -> Dict[str, int]:
        """find which scripts are in text"""
        scr_counts = {}
        
        for ch in text:
            cp = ord(ch)
            
            for scr, (start, end) in self.SCRIPT_RANGES.items():
                if start <= cp <= end:
                    scr_counts[scr] = scr_counts.get(scr, 0) + 1
                    break
        
        return scr_counts
    
    def is_indic_script(self, char: str) -> bool:
        """check if char is any indic script"""
        cp = ord(char)
        
        for start, end in self.SCRIPT_RANGES.values():
            if start <= cp <= end:
                return True
        
        return False
    
    def get_character_name(self, char: str) -> str:
        """get unicode name"""
        try:
            return unicodedata.name(char)
        except:
            return f"U+{ord(char):04X}"
    
    def analyze_text(self, text: str) -> Dict:
        """get stats about scripts in text"""
        scripts = self.identify_scripts(text)
        indic_cnt = sum(1 for c in text if self.is_indic_script(c))
        
        return {
            'total_chars': len(text),
            'indic_chars': indic_cnt,
            'scripts': scripts,
            'is_multilingual': len(scripts) > 1
        }


def identify_scripts(text: str) -> Dict[str, int]:
    """which indic scripts are in text"""
    analyzer = ScriptAnalyzer()
    return analyzer.identify_scripts(text)


def analyze_script(text: str) -> Dict:
    """full script analysis"""
    analyzer = ScriptAnalyzer()
    return analyzer.analyze_text(text)

