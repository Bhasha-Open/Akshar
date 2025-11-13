"""
Command-line interface for akshar tokenizer.

Provides simple commands for tokenization, detokenization, and analysis.
"""

import argparse
import sys
import json
from pathlib import Path

from .tokenizer import aksharTokenizer


def tokenize_command(args):
    """Handle 'tokenize' command."""
    tokenizer = aksharTokenizer(
        model_path=args.model,
        model_type=args.model_type
    )
    
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = args.text
    
    tokens = tokenizer.tokenize(text)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.format == 'json':
                json.dump(tokens, f, ensure_ascii=False, indent=2)
            else:
                f.write(' '.join(tokens))
    else:
        if args.format == 'json':
            print(json.dumps(tokens, ensure_ascii=False, indent=2))
        else:
            print(' '.join(tokens))


def detokenize_command(args):
    """Handle 'detokenize' command."""
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
    """Handle 'explain' command - detailed analysis."""
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


def main():
    """Main CLI entry point."""
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
    tokenize_parser.add_argument('--format', default='text', choices=['text', 'json'])
    
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


if __name__ == '__main__':
    main()

