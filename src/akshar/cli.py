"""
Command-line interface for Akshar.

Commands
--------
tokenize:
    Tokenize text from an argument or file, with optional model and formats.
detokenize:
    Convert tokens back to text (best-effort heuristics per model type).
explain:
    Print a human-readable breakdown of the processing pipeline.
train:
    Train a SentencePiece or BPE tokenizer from a corpus.
"""

import argparse
import sys
import json
from pathlib import Path

from .tokenizer import aksharTokenizer
from .normalize import normalize_text


def tokenize_command(args):
    """Handle the 'tokenize' subcommand.
    
    Parameters
    ----------
    args:
        argparse.Namespace with fields:
        - text (str | None)
        - input (str | None) path to a text file
        - model (str | None) model path if using SP/BPE
        - model_type (str) 'sentencepiece' or 'bpe'
        - format (str) 'text' | 'json' | 'id'
        - output (str | None) file to write output
    """
    # check if model file exists when provided
    if args.model and not Path(args.model).exists():
        print(f"Error: Model file not found: {args.model}", file=sys.stderr)
        print(f"  Current directory: {Path.cwd()}", file=sys.stderr)
        print(f"  To train a model: akshar train <corpus.txt> --output models/akshar --vocab-size 24000", file=sys.stderr)
        sys.exit(1)
    
    tokenizer = aksharTokenizer(
        model_path=args.model,
        model_type=args.model_type
    )
    
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = args.text
    
    if not text:
        print("Error: No text provided. Use --input or provide text as argument.", file=sys.stderr)
        sys.exit(1)
    
    # determine output format
    output_format = args.format
    
    # handle output
    if output_format == 'id':
        if not args.model:
            print("Error: --model required for ID output", file=sys.stderr)
            sys.exit(1)
        if tokenizer.model is None:
            print(f"Error: Failed to load model from {args.model}", file=sys.stderr)
            print(f"  Make sure the model file exists and is valid.", file=sys.stderr)
            sys.exit(1)
        try:
            ids = tokenizer.encode(text)
            output = ' '.join(map(str, ids))
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        tokens = tokenizer.tokenize(text)
        if output_format == 'json':
            output = json.dumps(tokens, ensure_ascii=False, indent=2)
        else:
            output = ' '.join(tokens)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        print(output)


def detokenize_command(args):
    """Handle the 'detokenize' subcommand.
    
    Parameters
    ----------
    args:
        argparse.Namespace with fields:
        - tokens (str | None) space-separated tokens if not using --input
        - input (str | None) file path containing tokens or JSON list
        - output (str | None) destination path
        - model (str | None), model_type (str) for model-aware heuristics
    """
    tokenizer = aksharTokenizer(
        model_path=args.model,
        model_type=args.model_type
    )
    
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
            # try to parse as JSON first
            try:
                tokens = json.loads(content)
            except json.JSONDecodeError:
                # assume space-separated tokens
                tokens = content.split()
    else:
        tokens = args.tokens.split()
    
    text = tokenizer.detokenize(tokens)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(text)
    else:
        print(text)


def explain_command(args):
    """Handle 'explain' - print a detailed pipeline breakdown.
    
    Shows normalized text, akshars, script segments, tokens, and stats.
    """
    tokenizer = aksharTokenizer(
        model_path=args.model,
        model_type=args.model_type
    )
    
    analysis = tokenizer.explain(args.text)
    
    # pretty print the analysis
    print("\n=== akshar Analysis ===\n")
    print(f"Original: {analysis['original']}")
    print(f"Normalized: {analysis['normalized']}")
    print(f"\nakshars ({len(analysis['akshars'])}):")
    print("  " + " | ".join(analysis['akshars']))
    
    print(f"\nCode Switches ({len(analysis['code_switches'])}):")
    for segment, script in analysis['code_switches']:
        print(f"  [{script:12}] {segment!r}")
    
    print(f"\nTokens ({len(analysis['tokens'])}):")
    print("  " + " | ".join(analysis['tokens']))
    
    print(f"\nStatistics:")
    for key, value in analysis['stats'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2%}" if 'ratio' in key else f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")


def preprocess_corpus(input_file, output_file):
    """Preprocess a corpus file with Akshar normalization.
    
    Returns
    -------
    str
        Path to the written output_file.
    """
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


def train_command(args):
    """Handle 'train' - train SentencePiece or BPE on a corpus.
    
    Parameters
    ----------
    args:
        argparse.Namespace containing corpus path, output prefix, and options.
    """
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    output_prefix = Path(args.output)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    
    if args.model_type == 'sentencepiece':
        try:
            import sentencepiece as spm
        except ImportError:
            print("Error: SentencePiece not installed.", file=sys.stderr)
            print("Install with: pip install sentencepiece", file=sys.stderr)
            sys.exit(1)
        
        # preprocess if needed
        train_file = input_file
        if not args.no_preprocess:
            preprocessed = output_prefix.with_suffix('.preprocessed.txt')
            preprocess_corpus(input_file, preprocessed)
            train_file = preprocessed
        
        print("\n=== Training SentencePiece Model ===\n")
        print(f"Input: {train_file}")
        print(f"Model prefix: {output_prefix}")
        print(f"Vocab size: {args.vocab_size}")
        print(f"Character coverage: {args.coverage}")
        print(f"Model type: {args.spm_model_type}")
        print()
        
        spm.SentencePieceTrainer.Train(
            input=str(train_file),
            model_prefix=str(output_prefix),
            vocab_size=args.vocab_size,
            character_coverage=args.coverage,
            model_type=args.spm_model_type,
            split_by_unicode_script=True,
            split_by_whitespace=True,
            normalization_rule_name='identity',
            byte_fallback=True,
            unk_piece='<unk>',
            bos_piece='<s>',
            eos_piece='</s>',
            pad_piece='<pad>',
            control_symbols=['<mask>'],
            max_sentence_length=4192
        )
        
        print(f"\nTraining complete!")
        print(f"Model saved to: {output_prefix}.model")
        print(f"Vocab saved to: {output_prefix}.vocab")
        
    elif args.model_type == 'bpe':
        try:
            from tokenizers import Tokenizer, models, pre_tokenizers, trainers, normalizers
            from tokenizers.processors import TemplateProcessing
        except ImportError:
            print("Error: HuggingFace tokenizers not installed.", file=sys.stderr)
            print("Install with: pip install tokenizers", file=sys.stderr)
            sys.exit(1)
        
        # preprocess if needed
        train_file = input_file
        if not args.no_preprocess:
            preprocessed = output_prefix.with_suffix('.preprocessed.txt')
            preprocess_corpus(input_file, preprocessed)
            train_file = preprocessed
        
        print("\n=== Training BPE Tokenizer ===\n")
        print(f"Input: {train_file}")
        print(f"Output: {output_prefix}")
        print(f"Vocab size: {args.vocab_size}")
        print()
        
        tokenizer = Tokenizer(models.BPE())
        tokenizer.normalizer = normalizers.NFKC()
        tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
        
        trainer = trainers.BpeTrainer(
            vocab_size=args.vocab_size,
            min_frequency=args.min_freq,
            special_tokens=['<pad>', '<unk>', '<s>', '</s>', '<mask>'],
            show_progress=True
        )
        
        tokenizer.train(files=[str(train_file)], trainer=trainer)
        
        tokenizer.post_processor = TemplateProcessing(
            single="<s> $A </s>",
            pair="<s> $A </s> <s> $B </s>",
            special_tokens=[
                ("<s>", tokenizer.token_to_id("<s>")),
                ("</s>", tokenizer.token_to_id("</s>")),
            ],
        )
        
        output_path = str(output_prefix) + '.json'
        tokenizer.save(output_path)
        
        print(f"\nTraining complete!")
        print(f"Tokenizer saved to: {output_path}")


def main():
    """Main CLI entry point. Dispatches to subcommands."""
    parser = argparse.ArgumentParser(
        description="akshar: Linguistically-aware tokenizer for Hindi, Sanskrit, and Hinglish"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # tokenize command
    tokenize_parser = subparsers.add_parser('tokenize', help='Tokenize text')
    tokenize_parser.add_argument('text', nargs='?', help='Text to tokenize')
    tokenize_parser.add_argument('-i', '--input', help='Input file')
    tokenize_parser.add_argument('-o', '--output', help='Output file')
    tokenize_parser.add_argument('-m', '--model', help='Path to trained model')
    tokenize_parser.add_argument('--model-type', default='sentencepiece',
                                choices=['sentencepiece', 'bpe'])
    tokenize_parser.add_argument('--format', default='text', choices=['text', 'json', 'id'],
                                help='Output format: text (tokens), json, or id (token IDs, requires --model)')
    
    # detokenize command
    detokenize_parser = subparsers.add_parser('detokenize', help='Detokenize tokens')
    detokenize_parser.add_argument('tokens', nargs='?', help='Space-separated tokens')
    detokenize_parser.add_argument('-i', '--input', help='Input file (tokens)')
    detokenize_parser.add_argument('-o', '--output', help='Output file')
    detokenize_parser.add_argument('-m', '--model', help='Path to trained model')
    detokenize_parser.add_argument('--model-type', default='sentencepiece',
                                  choices=['sentencepiece', 'bpe'])
    
    # explain command
    explain_parser = subparsers.add_parser('explain', help='Analyze text in detail')
    explain_parser.add_argument('text', help='Text to analyze')
    explain_parser.add_argument('-m', '--model', help='Path to trained model')
    explain_parser.add_argument('--model-type', default='sentencepiece',
                               choices=['sentencepiece', 'bpe'])
    
    # train command
    train_parser = subparsers.add_parser('train', help='Train a tokenizer model')
    train_parser.add_argument('input', help='Input corpus file')
    train_parser.add_argument('--output', required=True, help='Output model prefix (e.g., models/akshar)')
    train_parser.add_argument('--vocab-size', type=int, default=24000,
                             help='Vocabulary size (default: 24000)')
    train_parser.add_argument('--model-type', default='sentencepiece',
                            choices=['sentencepiece', 'bpe'],
                            help='Model type (default: sentencepiece)')
    train_parser.add_argument('--coverage', type=float, default=0.9997,
                            help='Character coverage for SentencePiece (default: 0.9997)')
    train_parser.add_argument('--spm-model-type', default='unigram',
                            choices=['unigram', 'bpe'],
                            help='SentencePiece model type (default: unigram)')
    train_parser.add_argument('--min-freq', type=int, default=2,
                            help='Minimum frequency for BPE (default: 2)')
    train_parser.add_argument('--no-preprocess', action='store_true',
                            help='Skip preprocessing step')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'tokenize':
        tokenize_command(args)
    elif args.command == 'detokenize':
        detokenize_command(args)
    elif args.command == 'explain':
        explain_command(args)
    elif args.command == 'train':
        train_command(args)


if __name__ == '__main__':
    main()

