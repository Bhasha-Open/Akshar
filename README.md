# Akshar

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/bhasha-open/Akshar/issues)

Akshar is a linguistically-aware tokenizer for Hindi, Sanskrit, and Hinglish. Unlike standard tokenizers that treat Indic text as character sequences, Akshar understands **grapheme clusters**aksharras), detects **code-switch boundaries** in mixed-script text, and applies **phonetic normalization** for Romanized Hindi. It supports both **BPE** and **Unigram** models and can be trained directly on raw multilingual corpora without pre-tokenization.

## Technical highlights

- **Grapheme-cluster aware**: Preserves Devanagari conjuncts (क्ष, ज्ञ, त्र) as single units using Unicode regex `\X` pattern
- **Code-switch detection**: Automatically identifies script boundaries in Hinglish text (Roman ↔ Devanagari transitions)
- **Semantic normalization**: Lowercases Roman script while preserving Devanagari case, handles social media variations
- **Phonetic signatures**: Aligns Romanized Hindi variants (nahi/nahii/nahee) to canonical forms
- **Language agnostic training**: Trains on raw sentences without pre-tokenization, handles mixed Hindi-English-Sanskrit corpus
- **Multiple subword algorithms**: Supports SentencePiece Unigram and HuggingFace BPE tokenization
- **Morphological segmentation**: Optional Morfessor-based morpheme analysis for Hindi and Sanskrit
- **Fast and lightweight**: Pure Python implementation with minimal dependencies
- **Reversible tokenization**: Preserves whitespace using meta-symbols for lossless detokenization

## Comparisons with other implementations

| Feature                       |         Akshar         |    IndicNLP    | SentencePiece | HF Tokenizers |
| :---------------------------- | :----------------------: | :-------------: | :-----------: | :-----------: |
| Grapheme-cluster preservation |           Yes           |     Partial     |      No      |      No      |
| Code-switch detection         |           Yes           |       No       |      No      |      No      |
| Hinglish normalization        |           Yes           |     Limited     |      No      |      No      |
| Pre-tokenization required?    |            No            |       Yes       |      No      |      No      |
| Morphological segmentation    |      Yes (optional)      |       Yes       |      No      |      No      |
| Phonetic analysis             |           Yes           |       Yes       |      No      |      No      |
| Multi-script support          | Yes (Roman + Devanagari) | Yes (all Indic) |      Yes      |      Yes      |
| Trained model required?       |    No (fallback mode)    |       No       |      Yes      |      Yes      |
| Python library                |           Yes           |       Yes       |      Yes      |      Yes      |

Note: IndicNLP provides broader Indic language support and mature normalization. Akshar specializes in code-mixing scenarios and modern ML tokenization.

## Overview

### What is Akshar?

Akshar is designed for **Hindi-Sanskrit-Hinglish** text where:

- Words may use Devanagari script (नमस्ते) or Roman script (namaste) or both
- Conjuncts must stay intact (क्षेत्र should not become क + ् + ष + े + त + ् + र)
- Script switches mid-sentence ("aaj मौसम बहुत nice hai")
- Social media text has elongations ("yaaaar" → "yaar")

Standard tokenizers (GPT2, BERT, SentencePiece) treat each Unicode codepoint independently, breaking visual units. Akshar uses grapheme-cluster regex to keep conjuncts together and detects script changes for proper boundary detection.

### The number of unique tokens is predetermined

Like SentencePiece, Akshar trains models with fixed vocabulary size (e.g., 8k, 16k, 24k). This is specified during training:

```bash
python scripts/train_spm.py --vocab_size 24000 corpus.txt
```

The vocabulary size determines model capacity vs. tokenization granularity tradeoff.

### Trains from raw sentences

No pre-tokenization needed. Feed raw Hindi/Sanskrit/Hinglish text:

```
आज मौसम बहुत अच्छा है
yaar aaj ka din bohot badhiya hai
मैं California में रहता हूं
```

Akshar handles normalization, script detection, and segmentation internally. This is crucial for Hinglish where word boundaries are ambiguous.

### Whitespace is treated as a basic symbol

Input text is normalized, then segmented preserving whitespace info. For example:

```
Input:  "aaj मौसम अच्छा है"
akshars: ['a', 'a', 'j', ' ', 'मौ', 'स', 'म', ' ', 'अ', 'च्छा', ' ', 'है']
```

Whitespace is preserved as tokens, enabling perfect reconstruction:

```python
original = ''.join(tokens)
```

This makes Akshar suitable for round-trip encoding in NMT systems.

## Installation

### Python module

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install regex sentencepiece tokenizers morfessor
```

Optional dependencies:

- `streamlit` - for web visualizer
- `pandas` - for batch analysis
- `morfessor` - for morphological segmentation

### Build from source

```bash
git clone https://github.com/bhasha-open/Akshar.git
cd Akshar
pip install -e .
```

Run tests to verify:

```bash
python -m pytest tests/
```

## Usage instructions

### Train Akshar Model

Prepare a corpus file (one sentence per line):

```bash
python scripts/train_spm.py data/corpus.txt \
  --output models/Akshar \
  --vocab_size 24000 \
  --model_type unigram
```

Parameters:

- `--vocab_size`: vocabulary size (8000, 16000, 24000 recommended)
- `--model_type`: `unigram` or `bpe`
- `--character_coverage`: 0.9995 for Indic scripts (default)

For BPE training:

```bash
python scripts/train_bpe.py data/corpus.txt \
  --output models/Akshar.json \
  --vocab_size 24000
```

### Tokenize text

Without a trained model (fallback to akshar-level):

```python
from Akshar import AksharTokenizer

tokenizer = AksharTokenizer()
tokens = tokenizer.tokenize("आज मौसम अच्छा है")
# ['आ', 'ज', ' ', 'मौ', 'स', 'म', ' ', 'अ', 'च्छा', ' ', 'है']
```

With trained model:

```python
tokenizer = AksharTokenizer(
    model_path="models/Akshar.model",
    model_type="sentencepiece"
)

tokens = tokenizer.tokenize("आज मौसम अच्छा है")
# ['▁आज', '▁मौसम', '▁अच्', 'छा', '▁है']  # depends on training
```

### Encode to IDs

```python
ids = tokenizer.encode("नमस्ते दुनिया")
# [245, 892, 1034, 567]  # example IDs

text = tokenizer.decode(ids)
# "नमस्ते दुनिया"
```

### Detailed analysis

```python
analysis = tokenizer.explain("aaj मौसम बहुत nice hai")

print(analysis['code_switches'])
# [('aaj ', 'roman'), ('मौसम बहुत ', 'devanagari'), ('nice hai', 'roman')]

print(analysis['stats'])
# {'akshar_count': 23, 'script_switches': 2, 'devanagari_ratio': 0.48, ...}
```

### Command-line usage

```bash
# tokenize
Akshar tokenize "आज मौसम अच्छा है"

# with model
Akshar tokenize --model models/Akshar.model "आज का मौसम"

# explain
Akshar explain "yaar aaj मौसम bohot nice hai"

# detokenize
Akshar detokenize "▁आज ▁मौसम ▁अच्छा ▁है"
```

### Word-level tokenization (IndicNLP style)

For word-level tokens instead of subwords:

```python
def word_tokenize(text):
    tokenizer = AksharTokenizer()
    normalized = tokenizer.preprocess(text)
    words = normalized.split()
    return words

tokens = word_tokenize("aaj मौसम बहुत अच्छा है")
# ['aaj', 'मौसम', 'बहुत', 'अच्छा', 'है']
```

This uses Akshar's normalization but returns words, not subwords.

## Advanced features

### Morphological segmentation

Requires `morfessor` library:

```python
from Akshar import segment_hindi, get_hindi_segmenter

# segment words into morphemes
morphemes = segment_hindi("समझना")  
# ['समझ', 'ना']

segmenter = get_hindi_segmenter()
if segmenter.is_model_loaded():
    parts = segmenter.segment_word("करना")
    # ['कर', 'ना']
```

### Phonetic analysis

```python
from Akshar import get_phonetic_analyzer

analyzer = get_phonetic_analyzer()

# character properties
props = analyzer.get_properties('ख')
# {'aspirated': True, 'voiced': False, 'nasal': False, 'velar': True}

# word analysis  
analysis = analyzer.analyze_word("नमस्ते")
# {'vowels': 2, 'consonants': 4, 'nasals': 2, 'aspirated': 0}
```

### Script detection

```python
from Akshar import identify_scripts, analyze_script

# which scripts present
scripts = identify_scripts("Hello नमस्ते World")
# {'devanagari': 6}

# full analysis
analysis = analyze_script("मैं California जाता हूं")
# {'total_chars': 21, 'indic_chars': 14, 'is_multilingual': True, ...}
```

### Batch processing

```python
texts = [
    "आज मौसम अच्छा है",
    "yaar kya scene hai",
    "मैं India से हूं"
]

for text in texts:
    tokens = tokenizer.tokenize(text)
    analysis = tokenizer.explain(text)
    print(f"{text} → {len(tokens)} tokens, {analysis['stats']['script_switches']} switches")
```

### Feature extraction for ML

```python
from Akshar import (
    detect_code_switches,
    analyze_phonetics,
    analyze_script,
    segment_akshars
)

def extract_features(text):
    """Extract linguistic features for ML models"""
    return {
        'length': len(text),
        'akshars': len(segment_akshars(text)),
        'switches': len(detect_code_switches(text)),
        'devanagari_ratio': analyze_script(text)['indic_chars'] / len(text),
        'vowels': analyze_phonetics(text)['vowels'],
        'consonants': analyze_phonetics(text)['consonants'],
    }

features = extract_features("aaj मौसम अच्छा है")
# Use for text classification, language ID, sentiment analysis, etc.
```

## Examples

See [example_features.ipynb](example_features.ipynb) for comprehensive demos of all features.

### Pure Hindi

```python
tokenizer.explain("आज मौसम बहुत अच्छा है")
# - All Devanagari
# - Preserves conjuncts (च्छा stays together)
# - No script switches
```

### Sanskrit

```python
tokenizer.explain("क्षेत्रे धर्मक्षेत्रे समवेता युयुत्सवः")
# - Complex conjuncts preserved
# - क्ष, त्र, र्म kept as single akshars
```

### Hinglish

```python
tokenizer.explain("yaar aaj ka mausam bohot achha hai")
# - All Roman script
# - Elongations normalized (bohot → bohot)
# - Phonetic signatures applied
```

### Code-switching

```python
tokenizer.explain("मैं California में रहता हूं और programming करता हूं")
# Script switches:
# [('मैं ', 'devanagari'), ('California ', 'roman'), 
#  ('में रहता हूं और ', 'devanagari'), ('programming ', 'roman'), ...]
```

### Social media

```python
text = "yaaaar aaj ka din bohoooot badhiyaaaa hai"
normalized = tokenizer.preprocess(text)
# "yar aaj ka din bohot badhiya hai"  # elongations removed
```

## Why use Akshar?

### For researchers

- **Code-mixing experiments**: Built-in code-switch detection and analysis
- **Morphological studies**: Optional morpheme segmentation
- **Phonetic analysis**: Character-level phonetic properties
- **Feature extraction**: Ready-to-use linguistic features for ML

### For NLP engineers

- **Clean preprocessing**: Handles messy social media Hinglish
- **Reversible encoding**: Perfect reconstruction for seq2seq models
- **No pre-tokenization**: Train directly on raw mixed-script corpus
- **Transparent**: `explain()` method shows all processing steps

### For Indian language models

- **Grapheme correctness**: Never breaks visual units
- **Sanskrit support**: Handles complex conjuncts properly
- **Hinglish native**: Designed for code-mixed scenarios
- **Multi-script**: Seamless Roman + Devanagari handling

GPT2, BERT, and standard SentencePiece don't understand Indic script structure. Akshar does.

## Technical details

### Akshar segmentation algorithm

Uses Unicode regex `\X` which matches extended grapheme clusters:

```python
import regex as re
akshar_PAT = re.compile(r'\X', re.UNICODE)
akshars = akshar_PAT.findall(text)
```

This keeps क + ् + ष + े together as one unit (क्षे).

### Code-switch detection

Tracks script changes character-by-character:

```python
def identify_script(char):
    cp = ord(char)
    if 0x0900 <= cp <= 0x097F:
        return 'devanagari'
    elif (0x0041 <= cp <= 0x005A) or (0x0061 <= cp <= 0x007A):
        return 'roman'
    # ... more scripts
```

When script changes, boundary detected.

### Normalization pipeline

1. Unicode NFC normalization (canonical composition)
2. Lowercase Roman characters, preserve Devanagari
3. Remove elongations (yaaaaar → yaar)
4. Filter garbage characters (keep Devanagari, Roman, digits, punct)

### Training strategy

Recommended vocab sizes:

- **8k**: Basic experiments
- **16k**: Small models
- **24k**: Production (sweet spot for Hindi+English+Sanskrit)
- **32k+**: Large multilingual models

Use Unigram for mixed-script stability, BPE for pure Devanagari.

## Project structure

```
Akshar/
├── src/Akshar/
│   ├── __init__.py          # main exports
│   ├── tokenizer.py         # AksharTokenizer class
│   ├── normalize.py         # text normalization
│   ├── segment.py           # akshar + code-switch logic
│   ├── morph.py             # morphological segmentation
│   ├── phonetic.py          # phonetic analysis
│   ├── script_utils.py      # multi-script detection
│   ├── cli.py               # command-line interface
│   ├── viz.py               # visualization helpers
│   ├── app.py               # streamlit web app
│   └── resources/           # phonetic data, morphology models
├── scripts/
│   ├── train_spm.py         # sentencepiece training
│   └── train_bpe.py         # BPE training
├── tests/
│   ├── test_normalize.py
│   ├── test_segment.py
│   └── test_tokenizer.py
├── data/
│   └── corpus.txt           # example training data
├── example_features.ipynb   # comprehensive feature demos
└── README.md
```

## Testing

Run all tests:

```bash
python -m pytest tests/ -v
```

Individual test modules:

```bash
python -m unittest tests.test_normalize
python -m unittest tests.test_segment  
python -m unittest tests.test_tokenizer
```

Test coverage:

- Unicode normalization
- Elongation removal
- Phonetic signatures
- Akshar segmentation
- Code-switch detection
- Tokenization with/without models

## Contributing

Contributions welcome! Areas that need work:

- **More Indic scripts**: Bengali, Tamil, Telugu, Gujarati, etc.
- **Better phonetic alignment**: Improve Hinglish normalization
- **Training corpora**: Share Hindi/Sanskrit/Hinglish datasets
- **Documentation**: Tutorials, examples, API docs
- **Performance**: Optimize segmentation algorithms
- **Testing**: More edge cases, multilingual tests

Submit issues or pull requests at [github.com/bhasha-open/Akshar](https://github.com/bhasha-open/Akshar)

## License

MIT License - see LICENSE file

## Citation

If you use Akshar in research:

```bibtex
@software{Akshar2025,
  title={Akshar: A Linguistically-Aware Tokenizer for Hindi, Sanskrit, and Hinglish},
  author={Bhasha Open},
  year={2025},
  url={https://github.com/bhasha-open/Akshar}
}
```

## Acknowledgments

- Built by Bhasha Open
- Inspired by SentencePiece, IndicNLP, and subword-nmt
- Phonetic data from indic_nlp_resources
- Morfessor models trained on Hindi/Sanskrit corpora

---

**Akshar treats Indian languages with the structural intelligence they deserve.**
