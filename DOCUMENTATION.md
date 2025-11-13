# Akshara Documentation Guide

This project includes comprehensive Sphinx documentation covering all features, tutorials, and API reference.

## Quick Start

### Build the documentation

```bash
cd docs
pip install -r requirements.txt
make html
```

View the built docs:

```bash
# macOS
open build/html/index.html

# Linux
xdg-open build/html/index.html

# Or use the convenience script
./build_docs.sh
```

### Live rebuild (development)

For automatic rebuilding while editing:

```bash
cd docs
make livehtml
```

Then browse to http://127.0.0.1:8000

## Documentation Structure

```
docs/source/
├── index.rst              # Main documentation index
├── installation.rst       # Installation instructions  
├── quickstart.rst         # Quick start guide
├── cli.rst                # Command-line interface reference
│
├── features/              # Feature documentation
│   ├── overview.rst       # Overview of all 22 features
│   ├── graphemes.rst      # Grapheme cluster segmentation
│   ├── codeswitch.rst     # Code-switch detection
│   ├── normalization.rst  # Text normalization
│   ├── morphology.rst     # Morphological segmentation
│   ├── phonetics.rst      # Phonetic analysis
│   └── scripts.rst        # Multi-script support
│
├── tutorials/             # Step-by-step tutorials
│   ├── basic.rst          # Basic usage patterns
│   ├── training.rst       # Training tokenization models
│   ├── hinglish.rst       # Hinglish processing
│   ├── sanskrit.rst       # Sanskrit text handling
│   └── ml_features.rst    # Feature extraction for ML
│
├── api/                   # API reference
│   ├── tokenizer.rst      # AksharaTokenizer class
│   ├── normalize.rst      # Normalization functions
│   ├── segment.rst        # Segmentation functions
│   ├── morph.rst          # Morphology functions
│   ├── phonetic.rst       # Phonetic analysis functions
│   └── script_utils.rst   # Script detection functions
│
├── comparison.rst         # Comparison with other tokenizers
├── faq.rst                # Frequently asked questions
├── contributing.rst       # Contribution guidelines
└── changelog.rst          # Version history
```

## What's Documented

### Core Documentation (✅ Complete)

- **Installation Guide**: Multiple installation methods, dependencies, troubleshooting
- **Quick Start**: 5-minute getting started guide with examples
- **CLI Reference**: Complete command-line interface documentation
- **Feature Overview**: All 22 features with examples
- **Grapheme Clusters**: Deep dive into akshara segmentation
- **Basic Tutorial**: 10-step tutorial covering common patterns
- **API Reference**: Complete AksharaTokenizer class documentation

### Ready to Expand (📝 Outlined)

The structure is in place for:
- Additional feature pages (code-switch, normalization, etc.)
- More tutorials (training, hinglish, sanskrit, ML features)
- Additional API pages (normalize, segment, morph, etc.)
- Comparison guide, FAQ, contributing guide

## Building from Scratch

If starting fresh:

```bash
# 1. Install Sphinx and theme
pip install sphinx sphinx-rtd-theme sphinx-autobuild

# 2. Navigate to docs
cd docs

# 3. Build HTML
make html

# 4. View
open build/html/index.html
```

## Documentation Style

The documentation follows these principles:

- **Professional but approachable**: Technical but not stuffy
- **Example-driven**: Every feature has working code examples
- **Progressive**: Starts simple, builds to advanced
- **Practical**: Focus on real-world usage patterns
- **No emojis**: Follows project rules for human-like code
- **Humanized tone**: Avoids AI-perfect language

## Key Features Documented

1. **Grapheme-cluster awareness**: How Akshara preserves Devanagari conjuncts
2. **Code-switch detection**: Finding script boundaries in mixed text
3. **Text normalization**: Cleaning social media Hinglish
4. **Word vs akshara tokenization**: Different granularity levels
5. **Morphological segmentation**: Breaking words into morphemes
6. **Phonetic analysis**: Linguistic properties of characters
7. **Multi-script support**: Handling Roman + Devanagari + more
8. **Batch processing**: Efficient handling of multiple texts
9. **Feature extraction**: Using Akshara for ML pipelines
10. **Model training**: Training custom SentencePiece/BPE models

## Examples in Documentation

Every page includes:

- Working code examples
- Expected output
- Common patterns
- Troubleshooting tips
- Links to related pages

## Extending the Documentation

To add new pages:

1. Create `.rst` file in appropriate directory
2. Add to `toctree` in `index.rst` or parent page
3. Use existing pages as templates
4. Build and verify: `make html`
5. Check for errors: `make linkcheck`

Example:

```rst
New Feature Page
================

Introduction paragraph.

Basic Usage
-----------

.. code-block:: python

   from akshara import new_feature
   
   result = new_feature("input")
   print(result)

See Also
--------

- :doc:`related_page`
- :doc:`../tutorials/tutorial_name`
```

## Hosting Options

The built HTML can be hosted on:

- **Read the Docs**: Automatic builds from GitHub
- **GitHub Pages**: Static hosting
- **Netlify/Vercel**: Automatic deploys
- **Self-hosted**: Any web server

For Read the Docs:

1. Connect GitHub repository
2. Set docs directory to `docs/`
3. Use `requirements.txt`
4. Builds automatically on push

## Maintenance

Keep documentation up-to-date:

- Update `changelog.rst` for each release
- Add examples for new features
- Fix broken links: `make linkcheck`
- Update API docs if signatures change
- Review and update FAQ periodically

## Help

If you encounter issues:

1. Check `docs/README.md` for build instructions
2. Verify Sphinx version: `sphinx-build --version`
3. Check for syntax errors in `.rst` files
4. Look at Sphinx build output for specific errors
5. See Sphinx docs: https://www.sphinx-doc.org/

---

**The documentation is as important as the code. Keep it comprehensive, accurate, and user-friendly!**
