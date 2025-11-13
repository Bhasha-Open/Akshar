"""
Streamlit web application for interactive Akshara tokenization.

This provides a visual interface to explore how text is tokenized,
showing aksharas, script boundaries, and token breakdowns.
"""

import streamlit as st
import sys
from pathlib import Path

# make sure we can import akshara
sys.path.insert(0, str(Path(__file__).parent.parent))

from akshara.tokenizer import AksharaTokenizer
from akshara.viz import colorize_by_script, format_token_boundaries, generate_html_visualization


st.set_page_config(
    page_title="Akshara Tokenizer",
    page_icon="🔤",
    layout="wide"
)

# header
st.title("Akshara: Smart Tokenizer for Hindi, Sanskrit & Hinglish")
st.markdown(
    "A linguistically-aware tokenizer that understands Devanagari aksharas, "
    "detects code-switch boundaries, and handles Hinglish intelligently."
)

# sidebar for settings
st.sidebar.header("Settings")

model_path = st.sidebar.text_input(
    "Model Path (optional)",
    help="Path to trained SentencePiece or BPE model"
)

model_type = st.sidebar.selectbox(
    "Model Type",
    ["sentencepiece", "bpe"],
    index=0
)

normalize_roman = st.sidebar.checkbox("Normalize Roman Script", value=True)
clean_hinglish = st.sidebar.checkbox("Clean Hinglish", value=True)

# initialize tokenizer
@st.cache_resource
def load_tokenizer(model_path, model_type, normalize_roman, clean_hinglish):
    return AksharaTokenizer(
        model_path=model_path if model_path else None,
        model_type=model_type,
        normalize_roman=normalize_roman,
        clean_hinglish=clean_hinglish
    )

tokenizer = load_tokenizer(model_path, model_type, normalize_roman, clean_hinglish)

# main input area
st.header("Input Text")

example_texts = {
    "Hindi": "आज मौसम बहुत अच्छा है",
    "Sanskrit": "क्षेत्रे धर्मक्षेत्रे समवेता युयुत्सवः",
    "Hinglish": "aaj मौसम बहुत अच्छा hai yaar",
    "Mixed": "मैं California में रहता हूं और हिंदी बोलता हूं",
    "Elongated Hinglish": "yaaaar aaj ka mausam bohot achaaaa hai"
}

example_choice = st.selectbox("Choose Example", ["Custom"] + list(example_texts.keys()))

if example_choice == "Custom":
    text = st.text_area("Enter text to tokenize:", height=100)
else:
    text = st.text_area("Enter text to tokenize:", value=example_texts[example_choice], height=100)

if st.button("Analyze") or text:
    if text:
        # get full analysis
        analysis = tokenizer.explain(text)
        
        # create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview", "Aksharas", "Script Boundaries", "Tokens", "Statistics"
        ])
        
        with tab1:
            st.subheader("Overview")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original Text:**")
                st.code(analysis['original'], language=None)
                
                st.markdown("**Normalized Text:**")
                st.code(analysis['normalized'], language=None)
            
            with col2:
                st.markdown("**Quick Stats:**")
                st.metric("Aksharas", analysis['stats']['akshara_count'])
                st.metric("Tokens", len(analysis['tokens']))
                st.metric("Script Switches", analysis['stats']['script_switches'])
        
        with tab2:
            st.subheader("Grapheme Clusters (Aksharas)")
            st.markdown(
                "These are the visual units that should never be split. "
                "Notice how conjuncts like क्ष stay together."
            )
            
            # display aksharas in a nice grid
            akshara_html = '<div style="display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px;">'
            for idx, akshara in enumerate(analysis['aksharas']):
                akshara_html += f'''
                <div style="border: 1px solid #ddd; padding: 8px 12px; 
                            border-radius: 4px; background: #f9f9f9; font-size: 18px;">
                    <div style="font-size: 10px; color: #666;">{idx}</div>
                    <div>{akshara}</div>
                </div>
                '''
            akshara_html += '</div>'
            st.markdown(akshara_html, unsafe_allow_html=True)
            
            st.markdown(f"**Total: {len(analysis['aksharas'])} aksharas**")
        
        with tab3:
            st.subheader("Code-Switch Detection")
            st.markdown(
                "Showing where the text switches between Devanagari and Roman scripts."
            )
            
            # visualize script boundaries
            for idx, (segment, script) in enumerate(analysis['code_switches']):
                color = '#e6f2ff' if script == 'devanagari' else '#e6ffe6'
                text_color = '#0066cc' if script == 'devanagari' else '#009900'
                
                st.markdown(f'''
                <div style="display: inline-block; background: {color}; 
                            padding: 10px 15px; margin: 5px; border-radius: 5px;">
                    <div style="font-size: 10px; color: #666;">Segment {idx} - {script}</div>
                    <div style="font-size: 18px; color: {text_color}; font-weight: 500;">{segment}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # composition breakdown
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Devanagari Content", 
                         f"{analysis['stats']['devanagari_ratio']:.1%}")
            with col2:
                st.metric("Roman Content", 
                         f"{analysis['stats']['roman_ratio']:.1%}")
        
        with tab4:
            st.subheader("Token Breakdown")
            
            if tokenizer.model is None:
                st.info(
                    "No model loaded. Showing akshara-level tokenization. "
                    "Load a trained model to see subword tokenization."
                )
            
            # display tokens
            token_html = '<div style="display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px;">'
            for idx, token in enumerate(analysis['tokens']):
                # escape special characters for display
                display_token = token.replace('▁', '·')  # replace space marker
                token_html += f'''
                <div style="border: 1px solid #999; padding: 8px 12px; 
                            border-radius: 4px; background: #fff3e0;">
                    <div style="font-size: 10px; color: #666;">{idx}</div>
                    <div style="font-family: monospace; font-size: 14px;">{display_token}</div>
                </div>
                '''
            token_html += '</div>'
            st.markdown(token_html, unsafe_allow_html=True)
            
            st.markdown(f"**Total: {len(analysis['tokens'])} tokens**")
            
            # show compression ratio
            if tokenizer.model:
                char_count = len(analysis['normalized'])
                token_count = len(analysis['tokens'])
                compression = char_count / token_count if token_count > 0 else 0
                st.metric("Characters per Token", f"{compression:.2f}")
        
        with tab5:
            st.subheader("Statistics")
            
            stats = analysis['stats']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Akshara Count", stats['akshara_count'])
                st.metric("Token Count", len(analysis['tokens']))
            
            with col2:
                st.metric("Script Switches", stats['script_switches'])
                if tokenizer.model:
                    st.metric("Vocab Size", tokenizer.vocab_size())
            
            with col3:
                st.metric("Devanagari Ratio", f"{stats['devanagari_ratio']:.1%}")
                st.metric("Roman Ratio", f"{stats['roman_ratio']:.1%}")
            
            # detailed breakdown
            st.markdown("---")
            st.markdown("**Detailed Breakdown:**")
            
            breakdown_data = {
                "Metric": ["Original Length", "Normalized Length", "Aksharas", "Tokens", 
                          "Avg Chars/Akshara", "Avg Chars/Token"],
                "Value": [
                    len(analysis['original']),
                    len(analysis['normalized']),
                    stats['akshara_count'],
                    len(analysis['tokens']),
                    f"{len(analysis['normalized']) / stats['akshara_count']:.2f}" 
                        if stats['akshara_count'] > 0 else "0",
                    f"{len(analysis['normalized']) / len(analysis['tokens']):.2f}" 
                        if len(analysis['tokens']) > 0 else "0"
                ]
            }
            st.table(breakdown_data)

# footer
st.markdown("---")
st.markdown(
    """
    **Akshara** is built by Bhasha Open.  
    A smart tokenizer that treats Indian languages with the structural intelligence they deserve.
    
    [GitHub](https://github.com) | [Documentation](#)
    """
)

