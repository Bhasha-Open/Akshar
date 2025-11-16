"""
Phonetic analysis utilities for Indic scripts (focus: Devanagari).

This module loads a compact phonetic property table (from
``resources/all_script_phonetic_data.csv``) and exposes a small analyzer
to answer questions like "is this consonant aspirated?" or "how many
nasals are in this word?".

The analyzer aims to be predictable rather than exhaustive; if a
character is missing in the CSV we simply return falsy/None instead
of guessing.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PhoneticAnalyzer:
    """Light-weight phonetic analyzer for Devanagari.

    The analyzer keeps a map of character → properties (aspirated, voiced,
    nasal, place of articulation, etc.) loaded from a static CSV. Callers
    typically keep a singleton around for repeated queries.

    Examples:
        Basic usage:

        >>> from akshar.phonetic import PhoneticAnalyzer
        >>> pa = PhoneticAnalyzer()
        >>> pa.is_consonant("क")
        True
        >>> pa.is_aspirated("ख")
        True
        >>> pa.get_place_of_articulation("ट")
        'retroflex'
        >>> pa.analyze_word("भारत")
        {'vowels': 2, 'consonants': 3, 'aspirated': 0, 'nasals': 0, 'total_chars': 5}
    """
    
    def __init__(self):
        self.char_props = {}
        self._load_data()
    
    def _load_data(self):
        """Populate the internal property map from CSV.

        The CSV is expected to have boolean columns like ``is_vowel``,
        ``aspirated``, and articulatory columns like ``velar``.
        Missing file is tolerated (the analyzer will just return defaults).
        """
        res_dir = Path(__file__).parent / "resources"
        pfile = res_dir / "all_script_phonetic_data.csv"
        
        if not pfile.exists():
            return
        
        # tried caching this in pickle but csv is fast enough
        with open(pfile, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ch = row['Devanagari']
                self.char_props[ch] = {
                    'itrans': row['ITRANS'],
                    'is_vowel': row['is_vowel'] == '1',
                    'is_consonant': row['is_consonant'] == '1',
                    'independent_vowel': row.get('independent_vowel', '0') == '1',
                    'dependent_vowel': row.get('dependent_vowel', '0') == '1',
                    'nukta': row['nukta'] == '1',
                    'halanta': row['halanta'] == '1',
                    'anusvara': row['anusvara'] == '1',
                    'aspirated': row['aspirated'] == '1',
                    'voiced': row['voiced'] == '1',
                    'nasal': row['nasal'] == '1',
                    'velar': row['velar'] == '1',
                    'palatal': row['palatal'] == '1',
                    'retroflex': row['retroflex'] == '1',
                    'dental': row['dental'] == '1',
                    'labial': row['labial'] == '1',
                }
    
    def get_properties(self, char: str) -> Optional[Dict]:
        """Return the phonetic property dict for a single character.

        Args:
            char: Single Devanagari character.

        Returns:
            Dict with boolean flags like ``is_vowel``, ``is_consonant``,
            ``aspirated``, ``voiced``, plus place flags (``velar`` etc.);
            ``None`` if the character is unknown.

        Examples:
            >>> from akshar.phonetic import PhoneticAnalyzer
            >>> PhoneticAnalyzer().get_properties("क")["is_consonant"]
            True
        """
        return self.char_props.get(char)
    
    def is_vowel(self, char: str) -> bool:
        """Whether the character is a vowel.

        Args:
            char: Single Devanagari character.

        Returns:
            True if marked as vowel in the data; False otherwise.
        """
        props = self.get_properties(char)
        return props['is_vowel'] if props else False
    
    def is_consonant(self, char: str) -> bool:
        """Whether the character is a consonant.

        Args:
            char: Single Devanagari character.

        Returns:
            True if marked as consonant in the data; False otherwise.
        """
        props = self.get_properties(char)
        return props['is_consonant'] if props else False
    
    def is_aspirated(self, char: str) -> bool:
        """Whether the consonant is aspirated.

        Args:
            char: Single Devanagari consonant (others return False).

        Returns:
            True if character is aspirated; False if unknown or not aspirated.
        """
        # We keep a small in-code hint to make intent obvious while reading.
        props = self.get_properties(char)
        return props['aspirated'] if props else False
    
    def is_voiced(self, char: str) -> bool:
        """Whether the character is voiced.

        Args:
            char: Single Devanagari character.

        Returns:
            True if character is voiced; False otherwise.
        """
        props = self.get_properties(char)
        return props['voiced'] if props else False
    
    def is_nasal(self, char: str) -> bool:
        """Whether the character is nasal.

        Args:
            char: Single Devanagari character.

        Returns:
            True if character is nasal; False otherwise.
        """
        props = self.get_properties(char)
        return props['nasal'] if props else False
    
    def get_place_of_articulation(self, char: str) -> Optional[str]:
        """Place of articulation for the character, if known.

        The check is ordered: velar → palatal → retroflex → dental → labial.

        Args:
            char: Single Devanagari character.

        Returns:
            One of ``'velar'``, ``'palatal'``, ``'retroflex'``, ``'dental'``,
            ``'labial'``; ``None`` if not applicable or unknown.
        """
        props = self.get_properties(char)
        if not props:
            return None
        
        # check in order
        if props['velar']:
            return 'velar'
        elif props['palatal']:
            return 'palatal'
        elif props['retroflex']:
            return 'retroflex'
        elif props['dental']:
            return 'dental'
        elif props['labial']:
            return 'labial'
        
        return None
    
    def analyze_word(self, word: str) -> Dict:
        """Summarize phonetic counts for a word (character-wise).

        Args:
            word: Devanagari string to analyze. We iterate characters naïvely;
                  grapheme-level handling is left to the caller if needed.

        Returns:
            Dict with keys:
            - ``vowels``: number of vowel characters
            - ``consonants``: number of consonant characters
            - ``aspirated``: number of aspirated consonants
            - ``nasals``: number of nasal consonants
            - ``total_chars``: length of input string (Python ``len``)

        Examples:
            >>> from akshar.phonetic import PhoneticAnalyzer
            >>> PhoneticAnalyzer().analyze_word("खग")
            {'vowels': 0, 'consonants': 2, 'aspirated': 1, 'nasals': 0, 'total_chars': 2}
        """
        vcnt = 0
        ccnt = 0
        acnt = 0
        ncnt = 0
        
        for ch in word:
            if self.is_vowel(ch):
                vcnt += 1
            elif self.is_consonant(ch):
                ccnt += 1
                if self.is_aspirated(ch):
                    acnt += 1
                if self.is_nasal(ch):
                    ncnt += 1
        
        return {
            'vowels': vcnt,
            'consonants': ccnt,
            'aspirated': acnt,
            'nasals': ncnt,
            'total_chars': len(word)
        }


# global singleton - lazy init
_analyzer = None

def get_phonetic_analyzer() -> PhoneticAnalyzer:
    """Return a process-local singleton analyzer instance.

    Returns:
        A cached ``PhoneticAnalyzer``. The CSV is loaded on first access.

    Examples:
        >>> from akshar.phonetic import get_phonetic_analyzer
        >>> pa = get_phonetic_analyzer()
        >>> pa.is_consonant("क")
        True
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = PhoneticAnalyzer()
    return _analyzer


def analyze_phonetics(text: str) -> Dict:
    """Convenience wrapper over ``PhoneticAnalyzer.analyze_word``.

    Args:
        text: Devanagari string to analyze character-wise.

    Returns:
        Same structure as :meth:`PhoneticAnalyzer.analyze_word`.

    Examples:
        >>> from akshar.phonetic import analyze_phonetics
        >>> analyze_phonetics("भारत")
        {'vowels': 2, 'consonants': 3, 'aspirated': 0, 'nasals': 0, 'total_chars': 5}
    """
    return get_phonetic_analyzer().analyze_word(text)


def _dev_to_itrans(text: str) -> str:
    """Best-effort romanization using the CSV's ITRANS column.
    
    We avoid adding a new dependency; this leans on the analyzer's table.
    Unknown chars are passed through unchanged.
    """
    pa = get_phonetic_analyzer()
    out: List[str] = []
    for ch in text:
        props = pa.get_properties(ch)
        out.append(props['itrans'].lower() if props and props.get('itrans') else ch)
    return ''.join(out)


_ROMAN_CONS_CACHE: Optional[Dict[str, str]] = None
_ROMAN_VOWEL_MATRA_CACHE: Optional[Dict[str, str]] = None
_ROMAN_VOWEL_INDEP_CACHE: Optional[Dict[str, str]] = None


def _normalize_itrans_token(tok: str) -> str:
    """Map csv ITRANS tokens to common Hinglish forms."""
    t = tok.lower()
    # map long vowels used in ITRANS to doubled roman
    if t == "a":
        return "a"
    if t == "aa" or t == "a:" or t == "ā":
        return "aa"
    if t in {"i", "ee"}:
        return "i"
    if t in {"ii", "i:", "ī"}:
        return "ii"
    if t == "u":
        return "u"
    if t in {"uu", "u:", "ū"}:
        return "uu"
    if t == "e":
        return "e"
    if t == "o":
        return "o"
    return t


def _build_itrans_maps():
    """Build roman→Devanagari maps using the phonetic CSV."""
    global _ROMAN_CONS_CACHE, _ROMAN_VOWEL_MATRA_CACHE, _ROMAN_VOWEL_INDEP_CACHE
    if _ROMAN_CONS_CACHE is not None:
        return
    pa = get_phonetic_analyzer()
    cons_map: Dict[str, str] = {}
    vowel_matra: Dict[str, str] = {}
    vowel_indep: Dict[str, str] = {}
    for ch, props in pa.char_props.items():
        itr = (props.get("itrans") or "").lower()
        if not itr:
            continue
        if props.get("is_consonant"):
            root = itr.rstrip("a") or itr  # 'ka' -> 'k'
            cons_map.setdefault(root, ch)
        if props.get("dependent_vowel"):
            key = _normalize_itrans_token(itr)
            vowel_matra.setdefault(key, ch)
        if props.get("independent_vowel"):
            key = _normalize_itrans_token(itr)
            vowel_indep.setdefault(key, ch)
    # add common Hinglish forms not present explicitly in ITRANS entries
    alias = {
        "ee": "ii",
        "oo": "uu",
        "ai": "ai",
        "au": "au",
    }
    for k, v in list(vowel_matra.items()):
        if k in alias:
            vowel_matra.setdefault(alias[k], v)
    for k, v in list(vowel_indep.items()):
        if k in alias:
            vowel_indep.setdefault(alias[k], v)
    _ROMAN_CONS_CACHE = cons_map
    _ROMAN_VOWEL_MATRA_CACHE = vowel_matra
    _ROMAN_VOWEL_INDEP_CACHE = vowel_indep


def _levenshtein_phonetic(a: str, b: str) -> float:
    """Levenshtein distance with lower cost for near-phonetic substitutions.
    
    We tweak substitution costs for common Hindi ⇆ Hinglish drifts:
    - t/th/ṭ/ठ/द/ड cluster considered related
    - n/ṇ/ṅ and m/ṃ
    - aspirated vs unaspirated pairs
    Returns normalized similarity in [0, 1] (1 = identical).
    """
    similar_sets = [
        set(list("tṭdḍ")) | {"th", "ṭh"},
        set(list("nmṅṇṃ")),
        set(list("kgh")) | {"kh", "gh"},
        set(list("pb")) | {"ph", "bh"},
        set(list("cjsz")) | {"ch", "jh"},
    ]

    def is_similar(x: str, y: str) -> bool:
        for s in similar_sets:
            if x in s and y in s:
                return True
        return False

    # Tokenize roman digraphs ('th', 'ch', 'jh', 'ph', 'bh', 'kh', 'gh') to keep intent
    def chunks(s: str) -> List[str]:
        i = 0
        out: List[str] = []
        digraphs = {"th", "ch", "jh", "ph", "bh", "kh", "gh", "ṭh"}
        while i < len(s):
            if i + 1 < len(s) and s[i : i + 2] in digraphs:
                out.append(s[i : i + 2])
                i += 2
            else:
                out.append(s[i])
                i += 1
        return out

    A, B = chunks(a.lower()), chunks(b.lower())
    na, nb = len(A), len(B)
    dp = [[0.0] * (nb + 1) for _ in range(na + 1)]
    for i in range(na + 1):
        dp[i][0] = float(i)
    for j in range(nb + 1):
        dp[0][j] = float(j)
    for i in range(1, na + 1):
        for j in range(1, nb + 1):
            ci, cj = A[i - 1], B[j - 1]
            sub_cost = 0.0 if ci == cj else (0.25 if is_similar(ci, cj) else 1.0)
            dp[i][j] = min(
                dp[i - 1][j] + 1.0,         # deletion
                dp[i][j - 1] + 1.0,         # insertion
                dp[i - 1][j - 1] + sub_cost # substitution
            )
    dist = dp[na][nb]
    denom = max(1, na + nb)
    # similarity in [0,1]
    return max(0.0, 1.0 - (2.0 * dist / denom))


def _roman_to_deva_coarse(text: str) -> str:
    """Roman→Devanagari using a compact, rule-based mapper (stable output).
    
    We intentionally keep this deterministic and opinionated for common Hinglish:
      - Consonant digraphs first (kh, gh, ch, jh, th, dh, ph, bh, sh)
      - Vowel tokens with matras when following a consonant, else independent
      - 'an' before a consonant → anusvara (ं) + next consonant
      - 'd'/'t' default to dental (द/त); retroflex forms are added later as variants
    """
    t = text.lower()
    i = 0
    out: List[str] = []
    prev_was_consonant = False

    cons_digraphs = {
        # aspirated stops
        "kh": "ख", "gh": "घ",

        # palatals
        "ch": "च", 
        "chh": "छ",   # sometimes used by Hinglish users
        "jh": "झ",

        # Hinglish default: th → ठ  (retroflex bias)
        "th": "ठ",

        # Hinglish default: dh → ढ (retroflex bias)
        "dh": "ढ",

        # labials
        "ph": "फ", "bh": "भ",

        # sibilants
        "sh": "ष",

        # Hinglish x → एक्स (not क्ष)
        "x": "एक्स",

        # optional cultural forms
        "ksh": "क्ष",
        "gy": "ज्ञ",   # gyani → ज्ञानी (very common Hinglish pattern)
    }

    cons_single = {
        # velars
        "k": "क",
        "g": "ग",

        # Hinglish: 'c' usually typed as 'k'
        "c": "क",

        # palatal
        "j": "ज",

        # dentals
        "t": "त",
        "d": "द",
        "n": "न",

        # labials
        "p": "प",
        "b": "ब",
        "m": "म",

        # semivowels
        "y": "य",
        "r": "र",
        "l": "ल",

        "v": "व",
        "w": "व",

        # sibilant
        "s": "स",

        # aspirate
        "h": "ह",

        # fallback English usage
        "x": "एक्स",
    }

    vowel_tokens = {
        # long vowels
        "aa": ("ा", "आ"),
        "ii": ("ी", "ई"),
        "ee": ("ी", "ई"),
        "uu": ("ू", "ऊ"),
        "oo": ("ू", "ऊ"),

        # diphthongs
        "ai": ("ै", "ऐ"),
        "au": ("ौ", "औ"),

        # Hinglish single vowels (correct)
        "a": ("", "अ"),     # NEVER "ा"
        "i": ("ि", "इ"),
        "u": ("ु", "उ"),

        "e": ("े", "ए"),
        "o": ("ो", "ओ"),
    }




    def next_is_single_consonant_then_end(idx: int) -> bool:
        dig = t[idx : idx + 2]
        if dig in cons_digraphs and idx + 2 == len(t):
            return True
        if t[idx:idx+1] in cons_single and idx + 1 == len(t):
            return True
        return False

    while i < len(t):
        # special English pattern: 'igh' ≈ 'ai' (light → lait)
        if t.startswith("igh", i):
            # treat like the 'ai' diphthong
            matra, indep = ("ै", "ऐ")
            if prev_was_consonant:
                out.append(matra)
            else:
                out.append(indep)
            i += 3
            prev_was_consonant = False
            continue
        # nasalization: 'an' before consonant -> anusvara
        if i + 1 < len(t) and t[i] == "a" and t[i + 1] == "n":
            # only nasalize if followed by a consonant after 'n'
            nxt2 = t[i + 2] if i + 2 < len(t) else ""
            if any(t.startswith(d, i + 2) for d in cons_digraphs) or nxt2 in cons_single:
                out.append("ं")
                prev_was_consonant = False
                i += 2
                continue

        # vowels (longest token)
        matched = False
        for tok in ("aa","ii","ee","uu","oo","ai","au","a","i","u","e","o"):
            if t.startswith(tok, i):
                matra, indep = vowel_tokens[tok]
                # Only lengthen final standalone 'i' at absolute end (e.g., "ji" → "जी")
                if tok == "i" and (i + 1 == len(t)) and prev_was_consonant:
                    matra = "ी"
                    indep = "ई"
                if prev_was_consonant:
                    out.append(matra)
                else:
                    out.append(indep)
                i += len(tok)
                prev_was_consonant = False
                matched = True
                break
        if matched:
            continue

        # consonant digraphs
        dig = t[i : i + 2]
        if dig in cons_digraphs:
            out.append(cons_digraphs[dig])
            i += 2
            prev_was_consonant = True
            continue
        # single consonant
        ch = t[i]
        if ch in cons_single:
            out.append(cons_single[ch])
            i += 1
            prev_was_consonant = True
            continue

        # fallback (punctuation etc.)
        out.append(ch)
        i += 1
        prev_was_consonant = False

    # nasal assimilation: 'न' before {द, ड} → 'ं' + stop
    out2: List[str] = []
    j = 0
    while j < len(out):
        cur = out[j]
        nxt = out[j + 1] if j + 1 < len(out) else ""
        if cur == "न" and nxt in {"द", "ड"}:
            out2.append("ं")
            out2.append(nxt)
            j += 2
            continue
        out2.append(cur)
        j += 1
    return "".join(out2)


def _hinglish_variants(token: str) -> List[str]:
    """Generate Devanagari candidates via roman→Deva + small alternations."""
    base = _roman_to_deva_coarse(token)
    variants = {base}
    # dental/retroflex alternations for t/d
    variants.add(base.replace("त", "ट"))
    variants.add(base.replace("द", "ड"))
    # 'ंद' → 'ंड'
    variants.add(base.replace("ंद", "ंड"))
    # common tail: 'िक' -> 'ीक' (thik → ठीक)
    variants.add(base.replace("िक", "ीक"))
    # final dental 'त' → retroflex 'ट' (light → लैक/लाइट variants)
    if base.endswith("त"):
        variants.add(base[:-1] + "ट")
    return [v for v in variants if v]


def phonetic_radar_hinglish_to_hindi(query: str, top_k: int = 5) -> List[Tuple[str, float]]:
    """Suggest Devanagari spellings for a Hinglish token with similarity scores.
    
    Parameters
    ----------
    query : str
        Hinglish input, e.g., ``"thand"``.
    top_k : int
        Number of suggestions to return.
    
    Returns
    -------
    List[Tuple[str, float]]
        List of (candidate, score) sorted by score desc. Score in [0, 1].
    
    Notes
    -----
    - We compare the input with an ITRANS romanization of generated candidates.
    - Substitutions across near-phonetic sets are penalized less.
    - This is deliberately compact and dependency-free; intended as an
      interactive helper rather than a dictionary-backed spellchecker.
    """
    cands = _hinglish_variants(query)
    scored: List[Tuple[str, float]] = []
    q = query.lower()
    for c in cands:
        roman = _dev_to_itrans(c)
        base = _levenshtein_phonetic(q, roman)
        bonus = 0.0
        # Prefer anusvara + retroflex for "...and" patterns
        if "and" in q or q.endswith("nd"):
            if "ंड" in c:
                bonus += 0.12
            elif "ंद" in c:
                bonus += 0.06
        # If input uses 'th', prefer ठ over थ
        if "th" in q:
            if "ठ" in c:
                bonus += 0.15
            elif "थ" in c:
                bonus += 0.02
        # English 'ight' pattern: prefer retroflex ट at the end (लाइट)
        if q.endswith("ight"):
            if c.endswith("ट"):
                bonus += 0.12
            elif c.endswith("त"):
                bonus -= 0.05
        # Prefer dental 'द' when 'd' present (retroflex 'ड' gets slight penalty)
        if "d" in q:
            if "द" in c:
                bonus += 0.05
            if "ड" in c:
                bonus -= 0.03
        # If 'i' occurs before a consonant in query, penalize long 'ी' outcomes
        for i_pos in range(len(q) - 1):
            if q[i_pos] == "i" and q[i_pos + 1].isalpha() and q[i_pos + 1] not in "aeiou":
                if "ी" in c:
                    bonus -= 0.08
                    break
        # If query uses plain 't' (not 'th'), prefer dental 'त' over retroflex 'ट'
        if "t" in q and "th" not in q:
            if "त" in c:
                bonus += 0.07
            if "ट" in c:
                bonus -= 0.05
        score = min(1.0, max(0.0, base + bonus))
        scored.append((c, round(score, 2)))
    scored.sort(key=lambda x: (x[1], x[0]), reverse=True)
    return scored[:top_k]

