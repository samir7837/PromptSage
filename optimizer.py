"""Conservative, deterministic prompt cleanup rules."""

import re

# Phrases are trimmed only when they are introductory politeness or verbose connective text.
REPLACEMENTS = (
    (r"\bcan you please\s+", ""), (r"\bcould you please\s+", ""),
    (r"\bi would like you to\s+", ""), (r"\bi want you to\s+", ""),
    (r"\bplease note that\s+", ""), (r"\bin order to\s+", "to "),
    (r"\bfor the purpose of\s+", "for "),
    (r"\bit is important to note that\s+", ""),
    (r"\bin a very simple way\b", "simply"),
    (r"\bthat can easily be understood by\b", "understandable to"),
)


def optimize_prompt(text: str) -> str:
    """Apply a small set of transparent edits; preserve constraints and other content."""
    result = text or ""
    for pattern, replacement in REPLACEMENTS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    result = re.sub(r"[ \t]+", " ", result)
    result = re.sub(r" *\n+ *", "\n", result)
    return result.strip()

