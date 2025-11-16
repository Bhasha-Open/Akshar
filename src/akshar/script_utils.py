"""
Script utilities: identify Indic scripts and basic script stats.
"""

from typing import Dict, List
import unicodedata


class ScriptAnalyzer:
    """Tiny helper to identify scripts and compute simple stats."""
    
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
        """Count characters per recognized script in the text."""
        scr_counts = {}
        
        for ch in text:
            cp = ord(ch)
            
            for scr, (start, end) in self.SCRIPT_RANGES.items():
                if start <= cp <= end:
                    scr_counts[scr] = scr_counts.get(scr, 0) + 1
                    break
        
        return scr_counts
    
    def is_indic_script(self, char: str) -> bool:
        """Return True if the character belongs to any tracked Indic block."""
        cp = ord(char)
        
        for start, end in self.SCRIPT_RANGES.values():
            if start <= cp <= end:
                return True
        
        return False
    
    def get_character_name(self, char: str) -> str:
        """Return the Unicode name, falling back to code point."""
        try:
            return unicodedata.name(char)
        except:
            return f"U+{ord(char):04X}"
    
    def analyze_text(self, text: str) -> Dict:
        """Compute basic stats: total, Indic count, per-script counts, multilingual flag."""
        scripts = self.identify_scripts(text)
        indic_cnt = sum(1 for c in text if self.is_indic_script(c))
        
        return {
            'total_chars': len(text),
            'indic_chars': indic_cnt,
            'scripts': scripts,
            'is_multilingual': len(scripts) > 1
        }


def identify_scripts(text: str) -> Dict[str, int]:
    """Convenience wrapper over ScriptAnalyzer.identify_scripts."""
    analyzer = ScriptAnalyzer()
    return analyzer.identify_scripts(text)


def analyze_script(text: str) -> Dict:
    """Convenience wrapper over ScriptAnalyzer.analyze_text."""
    analyzer = ScriptAnalyzer()
    return analyzer.analyze_text(text)

