"""
Training script for SentencePiece Unigram model.

This prepares data and trains an Akshar tokenizer using SentencePiece.
"""

import argparse
import sys
from pathlib import Path

# add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from Akshar.normalize import normalize_text
from Akshar.segment import segment_by_script


def preprocess_corpus(input_file, output_file, normalize=True):
    """
    Preprocess raw corpus before training.
    
    Applies normalization and optionally segments by script.
    """
    print(f"Preprocessing {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    processed = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if normalize:
            line = normalize_text(line)
        
        processed.append(line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in processed:
            f.write(line + '\n')
    
    print(f"Wrote {len(processed)} lines to {output_file}")


def train_sentencepiece(
    input_file,
    model_prefix,
    vocab_size=24000,
    character_coverage=0.9997,
    model_type='unigram'
):
    """
    Train SentencePiece model with Akshar-friendly settings.
    
    Args:
        input_file: Path to training corpus
        model_prefix: Output model prefix (will create .model and .vocab)
        vocab_size: Target vocabulary size
        character_coverage: Character coverage (high for Indic scripts)
        model_type: 'unigram' (recommended) or 'bpe'
    """
    try:
        import sentencepiece as spm
    except ImportError:
        print("ERROR: SentencePiece not installed.")
        print("Install with: pip install sentencepiece")
        sys.exit(1)
    
    print("\n=== Training SentencePiece Model ===\n")
    print(f"Input: {input_file}")
    print(f"Model prefix: {model_prefix}")
    print(f"Vocab size: {vocab_size}")
    print(f"Character coverage: {character_coverage}")
    print(f"Model type: {model_type}")
    print()
    
    # train with settings optimized for multi-script Indian languages
    spm.SentencePieceTrainer.Train(
        input=input_file,
        model_prefix=model_prefix,
        vocab_size=vocab_size,
        character_coverage=character_coverage,
        model_type=model_type,
        
        # important for mixed scripts
        split_by_unicode_script=True,
        split_by_whitespace=True,
        
        # preserve case since we handle it in normalization
        normalization_rule_name='identity',
        
        # use byte fallback for rare characters
        byte_fallback=True,
        
        # special tokens
        unk_piece='<unk>',
        bos_piece='<s>',
        eos_piece='</s>',
        pad_piece='<pad>',
        
        # control tokens
        control_symbols=['<mask>'],
        
        # max sentence length for training
        max_sentence_length=4192
    )
    
    print(f"\nTraining complete!")
    print(f"Model saved to: {model_prefix}.model")
    print(f"Vocab saved to: {model_prefix}.vocab")


def main():
    parser = argparse.ArgumentParser(
        description="Train SentencePiece model for Akshar tokenizer"
    )
    
    parser.add_argument('input', help='Input corpus file')
    parser.add_argument('--output', default='Akshar', help='Output model prefix')
    parser.add_argument('--vocab-size', type=int, default=24000, 
                       help='Vocabulary size (default: 24000)')
    parser.add_argument('--coverage', type=float, default=0.9997,
                       help='Character coverage (default: 0.9997)')
    parser.add_argument('--model-type', default='unigram',
                       choices=['unigram', 'bpe'],
                       help='Model type (default: unigram)')
    parser.add_argument('--no-preprocess', action='store_true',
                       help='Skip preprocessing step')
    
    args = parser.parse_args()
    
    input_file = args.input
    
    # preprocess if needed
    if not args.no_preprocess:
        preprocessed = Path(args.output).with_suffix('.preprocessed.txt')
        preprocess_corpus(input_file, preprocessed)
        input_file = preprocessed
    
    # train model
    train_sentencepiece(
        input_file=input_file,
        model_prefix=args.output,
        vocab_size=args.vocab_size,
        character_coverage=args.coverage,
        model_type=args.model_type
    )


if __name__ == '__main__':
    main()

