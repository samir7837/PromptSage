"""Classical, explainable text analysis for PromptSage."""

from collections import Counter
import re
from typing import Any

from nltk.tokenize import TreebankWordTokenizer

# A compact built-in list keeps the app usable offline without downloading NLTK data.
STOPWORDS = set("""a about above after again against all am an and any are as at be because been before being below between both but by can could did do does doing down during each few for from further had has have having he her here hers herself him himself his how i if in into is it its itself just me more most my myself no nor not of off on once only or other our ours ourselves out over own same she should so some such than that the their theirs them themselves then there these they this those through to too under until up very was we were what when where which while who whom why will with would you your yours yourself yourselves please""".split())
FILLER_PHRASES = (
    "it is important to note that", "in a very simple way", "that can easily be understood by",
    "as a matter of fact", "for all intents and purposes", "basically", "actually",
    "really", "very", "just", "kind of", "sort of",
)

_TOKENIZER = TreebankWordTokenizer()


def _words(text: str) -> list[str]:
    return [
        w.casefold() for w in _TOKENIZER.tokenize(text) if re.search(r"\w", w, flags=re.UNICODE)
    ]


def analyze_prompt(text: str) -> dict[str, Any]:
    """Return prompt statistics and keyword insights. Does not alter the input."""
    text = text or ""
    words = _words(text)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+|\n+", text.strip()) if s.strip() and re.search(r"\w", s, re.UNICODE)]
    counts = Counter(w for w in words if w not in STOPWORDS and len(w) > 1)
    fillers = [phrase for phrase in FILLER_PHRASES if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, re.I)]
    repeated = {word: count for word, count in Counter(words).items() if count > 1}
    return {
        "characters": len(text), "words": len(words), "sentences": len(sentences),
        "unique_words": len(set(words)), "reading_time_minutes": len(words) / 200,
        "average_words_per_sentence": len(words) / len(sentences) if sentences else 0.0,
        "frequent_words": counts.most_common(8), "filler_phrases": fillers,
        "repeated_words": repeated,
    }

