"""
Tests for main tokenizer class.
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from akshar.tokenizer import AksharTokenizer


class TestTokenizer(unittest.TestCase):
    
    def setUp(self):
        """Initialize tokenizer for tests."""
        # without model - will fall back to akshar segmentation
        self.tokenizer = AksharTokenizer()
    
    def test_initialization(self):
        """Test tokenizer initialization."""
        self.assertIsNotNone(self.tokenizer)
        self.assertIsNone(self.tokenizer.model)
    
    def test_preprocess(self):
        """Test text preprocessing."""
        text = "Hello नमस्ते"
        result = self.tokenizer.preprocess(text)
        
        # Roman should be lowercase
        self.assertIn('hello', result)
        self.assertIn('नमस्ते', result)
    
    def test_tokenize_without_model(self):
        """Test tokenization without loaded model (falls back to akshars)."""
        text = "नमस्ते"
        tokens = self.tokenizer.tokenize(text)
        
        self.assertIsInstance(tokens, list)
        self.assertTrue(len(tokens) > 0)
    
    def test_tokenize_with_metadata(self):
        """Test tokenization with metadata return."""
        text = "hello नमस्ते"
        result = self.tokenizer.tokenize(text, return_metadata=True)
        
        self.assertIsInstance(result, dict)
        self.assertIn('tokens', result)
        self.assertIn('token_count', result)
        self.assertIn('original_text', result)
        self.assertIn('akshar_count', result)
    
    def test_explain(self):
        """Test explain method."""
        text = "aaj मौसम अच्छा है"
        analysis = self.tokenizer.explain(text)
        
        # should return comprehensive analysis
        self.assertIn('original', analysis)
        self.assertIn('normalized', analysis)
        self.assertIn('akshars', analysis)
        self.assertIn('code_switches', analysis)
        self.assertIn('tokens', analysis)
        self.assertIn('stats', analysis)
    
    def test_explain_pure_hindi(self):
        """Test explain on pure Hindi text."""
        text = "आज मौसम बहुत अच्छा है"
        analysis = self.tokenizer.explain(text)
        
        # should have high devanagari ratio
        self.assertGreater(analysis['stats']['devanagari_ratio'], 0.8)
    
    def test_explain_hinglish(self):
        """Test explain on Hinglish text."""
        text = "yaar aaj ka मौसम बहुत अच्छा hai"
        analysis = self.tokenizer.explain(text)
        
        # should have both scripts
        self.assertGreater(analysis['stats']['devanagari_ratio'], 0)
        self.assertGreater(analysis['stats']['roman_ratio'], 0)
    
    def test_vocab_size_no_model(self):
        """Test vocab_size when no model loaded."""
        size = self.tokenizer.vocab_size()
        self.assertEqual(size, 0)


if __name__ == '__main__':
    unittest.main()

