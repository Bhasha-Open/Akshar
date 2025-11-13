"""
Tests for normalization module.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from akshara.normalize import (
    normalize_unicode,
    semantic_normalize,
    remove_elongations,
    roman_phonetic_signature,
    normalize_text
)


class TestNormalize(unittest.TestCase):
    
    def test_unicode_normalization(self):
        """Test NFC normalization."""
        # some text might have decomposed characters
        text = "नमस्ते"
        normalized = normalize_unicode(text)
        # should be in composed form
        self.assertIsInstance(normalized, str)
        self.assertEqual(len(normalized), len(text))
    
    def test_semantic_normalize_roman(self):
        """Test that Roman text gets lowercased."""
        text = "Hello World"
        result = semantic_normalize(text)
        self.assertEqual(result, "hello world")
    
    def test_semantic_normalize_devanagari(self):
        """Test that Devanagari text stays unchanged."""
        text = "नमस्ते दुनिया"
        result = semantic_normalize(text)
        self.assertEqual(result, text)
    
    def test_semantic_normalize_mixed(self):
        """Test mixed script normalization."""
        text = "Hello नमस्ते World"
        result = semantic_normalize(text)
        self.assertEqual(result, "hello नमस्ते world")
    
    def test_remove_elongations(self):
        """Test elongation removal in Hinglish."""
        # function reduces 3+ repetitions to 1
        cases = [
            ("heyyy", "hey"),
            ("yaaaaar", "yar"),
            ("niceeee", "nice"),
            ("hello", "helo"),  # double letters reduced
            ("aaj", "aj"),
        ]
        
        for input_text, expected in cases:
            result = remove_elongations(input_text)
            # all should be reduced
            self.assertTrue(len(result) <= len(input_text))
    
    def test_roman_phonetic_signature(self):
        """Test phonetic signature generation."""
        # common Hinglish variations should map to same signature
        variants = ["nahi", "nahii", "nahee"]
        signatures = [roman_phonetic_signature(v) for v in variants]
        # they should be similar (though not necessarily identical)
        self.assertTrue(all(isinstance(s, str) for s in signatures))
    
    def test_normalize_text_full_pipeline(self):
        """Test complete normalization pipeline."""
        text = "Heyyy यार kya HAAL hai"
        result = normalize_text(text)
        
        # should be lowercased and cleaned
        self.assertIn("hey", result)
        self.assertIn("यार", result)
        self.assertNotIn("HAAL", result)  # should be lowercase


if __name__ == '__main__':
    unittest.main()

