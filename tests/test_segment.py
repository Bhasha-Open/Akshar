"""
Tests for segmentation module.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from akshara.segment import (
    segment_aksharas,
    identify_script,
    detect_code_switches,
    analyze_text_composition
)


class TestSegment(unittest.TestCase):
    
    def test_segment_aksharas_simple(self):
        """Test simple akshara segmentation."""
        text = "नमस्ते"
        aksharas = segment_aksharas(text)
        # should get grapheme clusters
        self.assertIsInstance(aksharas, list)
        self.assertTrue(len(aksharas) > 0)
    
    def test_segment_aksharas_conjuncts(self):
        """Test that conjuncts stay together."""
        text = "क्षेत्र"
        aksharas = segment_aksharas(text)
        
        # क्ष should be one akshara
        self.assertTrue(any('क्ष' in a for a in aksharas))
    
    def test_identify_script_devanagari(self):
        """Test Devanagari script identification."""
        self.assertEqual(identify_script('न'), 'devanagari')
        self.assertEqual(identify_script('म'), 'devanagari')
    
    def test_identify_script_roman(self):
        """Test Roman script identification."""
        self.assertEqual(identify_script('a'), 'roman')
        self.assertEqual(identify_script('Z'), 'roman')
    
    def test_identify_script_digits(self):
        """Test digit identification."""
        self.assertEqual(identify_script('5'), 'digit')
    
    def test_identify_script_punctuation(self):
        """Test punctuation identification."""
        self.assertEqual(identify_script('.'), 'punct')
        self.assertEqual(identify_script(' '), 'punct')
    
    def test_detect_code_switches_pure_devanagari(self):
        """Test with pure Devanagari text."""
        text = "नमस्ते दुनिया"
        switches = detect_code_switches(text)
        
        # should have segments
        self.assertTrue(len(switches) > 0)
        # all should be devanagari
        for _, script in switches:
            if script != 'punct':
                self.assertEqual(script, 'devanagari')
    
    def test_detect_code_switches_pure_roman(self):
        """Test with pure Roman text."""
        text = "hello world"
        switches = detect_code_switches(text)
        
        # should detect roman script
        self.assertTrue(any(script == 'roman' for _, script in switches))
    
    def test_detect_code_switches_mixed(self):
        """Test with mixed script text (Hinglish)."""
        text = "aaj मौसम अच्छा hai"
        switches = detect_code_switches(text)
        
        # should detect both scripts
        scripts = [script for _, script in switches]
        self.assertIn('roman', scripts)
        self.assertIn('devanagari', scripts)
        
        # should have multiple switches
        self.assertTrue(len(switches) >= 3)
    
    def test_analyze_text_composition(self):
        """Test text composition analysis."""
        text = "hello नमस्ते"
        analysis = analyze_text_composition(text)
        
        # should return dict with expected keys
        self.assertIn('akshara_count', analysis)
        self.assertIn('script_switches', analysis)
        self.assertIn('devanagari_ratio', analysis)
        self.assertIn('roman_ratio', analysis)
        
        # ratios should be between 0 and 1
        self.assertTrue(0 <= analysis['devanagari_ratio'] <= 1)
        self.assertTrue(0 <= analysis['roman_ratio'] <= 1)


if __name__ == '__main__':
    unittest.main()

