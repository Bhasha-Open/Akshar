"""
Visualization helpers for akshar tokenizer.

Provides utilities for displaying token boundaries, akshars, and script switches.
"""

from typing import List, Tuple
import json


def colorize_by_script(text_segments: List[Tuple[str, str]]) -> str:
    """
    Generate ANSI colored output for terminal display.
    
    Args:
        text_segments: List of (text, script) tuples from detect_code_switches
    
    Returns:
        String with ANSI color codes
    """
    # ANSI color codes
    COLORS = {
        'devanagari': '\033[94m',  # blue
        'roman': '\033[92m',        # green
        'digit': '\033[93m',        # yellow
        'punct': '\033[90m',        # gray
        'other': '\033[95m',        # magenta
    }
    RESET = '\033[0m'
    
    result = []
    for segment, script in text_segments:
        color = COLORS.get(script, RESET)
        result.append(f"{color}{segment}{RESET}")
    
    return ''.join(result)


def format_token_boundaries(text: str, tokens: List[str]) -> str:
    """
    Show token boundaries with visual markers.
    
    Example output:
        ▁aaj | ▁मौसम | ▁बहुत | ▁अच्छा | ▁है
    """
    return " | ".join(tokens)


def format_akshar_boundaries(akshars: List[str]) -> str:
    """
    Display akshars with boundaries marked.
    
    Example:
        [क] [्] [ष] [े] [त] [्] [र] [े]
    """
    return " ".join(f"[{a}]" for a in akshars)


def generate_html_visualization(analysis: dict) -> str:
    """
    Generate HTML for rich visualization of tokenization.
    
    This can be used in Streamlit or saved as standalone HTML.
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; padding: 20px; }
            .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .label { font-weight: bold; color: #333; }
            .devanagari { color: #0066cc; background: #e6f2ff; padding: 2px 4px; }
            .roman { color: #009900; background: #e6ffe6; padding: 2px 4px; }
            .token { display: inline-block; border: 1px solid #999; padding: 3px 6px; 
                     margin: 2px; border-radius: 3px; background: #f9f9f9; }
            .akshar { display: inline-block; border: 1px dashed #ccc; padding: 2px 4px; 
                       margin: 1px; font-family: monospace; }
            .stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
            .stat-item { padding: 10px; background: #f5f5f5; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>akshar Analysis</h1>
    """
    
    # original text
    html += f"""
        <div class="section">
            <div class="label">Original Text:</div>
            <div style="font-size: 18px; margin-top: 5px;">{analysis['original']}</div>
        </div>
    """
    
    # normalized text
    html += f"""
        <div class="section">
            <div class="label">Normalized Text:</div>
            <div style="font-size: 18px; margin-top: 5px;">{analysis['normalized']}</div>
        </div>
    """
    
    # code switches with coloring
    html += '<div class="section"><div class="label">Script Boundaries:</div><div style="margin-top: 5px;">'
    for segment, script in analysis['code_switches']:
        css_class = script if script in ['devanagari', 'roman'] else 'token'
        html += f'<span class="{css_class}">{segment}</span>'
    html += '</div></div>'
    
    # akshars
    html += '<div class="section"><div class="label">akshars (Grapheme Clusters):</div><div style="margin-top: 5px;">'
    for akshar in analysis['akshars']:
        html += f'<span class="akshar">{akshar}</span>'
    html += '</div></div>'
    
    # tokens
    html += '<div class="section"><div class="label">Tokens:</div><div style="margin-top: 5px;">'
    for token in analysis['tokens']:
        html += f'<span class="token">{token}</span>'
    html += '</div></div>'
    
    # statistics
    html += '<div class="section"><div class="label">Statistics:</div><div class="stats" style="margin-top: 10px;">'
    for key, value in analysis['stats'].items():
        if isinstance(value, float):
            formatted = f"{value:.1%}" if 'ratio' in key else f"{value:.2f}"
        else:
            formatted = str(value)
        label = key.replace('_', ' ').title()
        html += f'<div class="stat-item"><strong>{label}:</strong> {formatted}</div>'
    html += '</div></div>'
    
    html += """
    </body>
    </html>
    """
    
    return html


def export_analysis_json(analysis: dict, output_path: str):
    """
    Export analysis to JSON file for external tools.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)


def print_comparison_table(texts: List[str], tokenizer):
    """
    Print comparison table showing how different texts tokenize.
    Useful for debugging and evaluation.
    """
    print("\n" + "=" * 80)
    print(f"{'Text':<40} | {'Tokens':<10} | {'akshars':<10}")
    print("=" * 80)
    
    for text in texts:
        analysis = tokenizer.explain(text)
        token_count = len(analysis['tokens'])
        akshar_count = len(analysis['akshars'])
        
        # truncate long text for display
        display_text = text if len(text) <= 37 else text[:34] + "..."
        print(f"{display_text:<40} | {token_count:<10} | {akshar_count:<10}")
    
    print("=" * 80 + "\n")

