"""
Training script for HuggingFace BPE tokenizer.

Alternative to SentencePiece, using the tokenizers library.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from akshar.normalize import normalize_text


def preprocess_corpus(input_file, output_file):
    """Preprocess corpus with Akshar normalization."""
    print(f"Preprocessing {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    processed = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        processed.append(normalize_text(line))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in processed:
            f.write(line + '\n')
    
    print(f"Wrote {len(processed)} lines to {output_file}")
    return str(output_file)


def train_bpe_tokenizer(
    input_file,
    output_path,
    vocab_size=24000,
    min_frequency=2
):
    """
    Train BPE tokenizer using HuggingFace tokenizers library.
    
    Args:
        input_file: Training corpus
        output_path: Where to save the trained tokenizer
        vocab_size: Target vocabulary size
        min_frequency: Minimum frequency for token pairs
    """
    try:
        from tokenizers import Tokenizer, models, pre_tokenizers, trainers, normalizers
        from tokenizers.processors import TemplateProcessing
    except ImportError:
        print("ERROR: HuggingFace tokenizers not installed.")
        print("Install with: pip install tokenizers")
        sys.exit(1)
    
    print("\n=== Training BPE Tokenizer ===\n")
    print(f"Input: {input_file}")
    print(f"Output: {output_path}")
    print(f"Vocab size: {vocab_size}")
    print()
    
    # initialize BPE model
    tokenizer = Tokenizer(models.BPE())
    
    # we handle normalization ourselves, so keep it minimal here
    tokenizer.normalizer = normalizers.NFKC()
    
    # split by whitespace and punctuation
    tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
    
    # configure trainer
    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=min_frequency,
        special_tokens=['<pad>', '<unk>', '<s>', '</s>', '<mask>'],
        show_progress=True
    )
    
    # train on corpus
    tokenizer.train(files=[input_file], trainer=trainer)
    
    # add post-processing for special tokens
    tokenizer.post_processor = TemplateProcessing(
        single="<s> $A </s>",
        pair="<s> $A </s> <s> $B </s>",
        special_tokens=[
            ("<s>", tokenizer.token_to_id("<s>")),
            ("</s>", tokenizer.token_to_id("</s>")),
        ],
    )
    
    # save
    tokenizer.save(output_path)
    
    print(f"\nTraining complete!")
    print(f"Tokenizer saved to: {output_path}")
    
    # quick test
    test_text = "आज मौसम बहुत अच्छा है"
    encoding = tokenizer.encode(test_text)
    print(f"\nTest encoding: {test_text}")
    print(f"Tokens: {encoding.tokens}")


def main():
    parser = argparse.ArgumentParser(
        description="Train BPE tokenizer for Akshar"
    )
    
    parser.add_argument('input', help='Input corpus file')
    parser.add_argument('--output', default='Akshar_bpe.json',
                       help='Output tokenizer file')
    parser.add_argument('--vocab-size', type=int, default=24000,
                       help='Vocabulary size (default: 24000)')
    parser.add_argument('--min-freq', type=int, default=2,
                       help='Minimum frequency (default: 2)')
    parser.add_argument('--no-preprocess', action='store_true',
                       help='Skip preprocessing')
    
    args = parser.parse_args()
    
    input_file = args.input
    
    if not args.no_preprocess:
        preprocessed = Path(args.output).with_suffix('.preprocessed.txt')
        input_file = preprocess_corpus(input_file, preprocessed)
    
    train_bpe_tokenizer(
        input_file=input_file,
        output_path=args.output,
        vocab_size=args.vocab_size,
        min_frequency=args.min_freq
    )


if __name__ == '__main__':
    main()

