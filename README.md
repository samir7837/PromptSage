# PromptSage

**Write smarter prompts. Use fewer tokens.**

PromptSage is a local Streamlit application that reviews prompt text using classical NLP techniques and suggests transparent, rule-based edits. It reports text statistics, highlights frequent keywords and configured filler phrases, and compares token counts using a selected `tiktoken` encoding.

> PromptSage does not call an LLM or guarantee that an edited prompt preserves meaning. Review the suggested text before using it.

## Contents

- [Features](#features)
- [Technology](#technology)
- [How it works](#how-it-works)
- [Installation](#installation)
- [Run the app](#run-the-app)
- [Run the tests](#run-the-tests)
- [Project structure](#project-structure)
- [Limitations](#limitations)
- [Viva questions](#viva-questions)

## Features

- Character, word, sentence, and unique-word statistics.
- Estimated reading time and average words per sentence.
- Exact token counts for `cl100k_base` and `o200k_base` when the selected tokenizer data is available.
- Keyword frequency after stopword filtering, plus filler-phrase and repeated-word detection.
- Conservative rule-based optimization with an editable result.
- Original-versus-optimized comparison for tokens, words, character count, and token reduction.
- Sample prompts, a reset control, and an expandable **NLP Insights** explanation.
- Dark, high-contrast interface designed for a clear project demonstration.

## Technology

| Component | Purpose |
| --- | --- |
| Python 3.10+ | Application logic |
| Streamlit | Interactive web interface |
| NLTK | Resource-free Treebank word tokenizer |
| tiktoken | Encoding-specific token counts |
| `re` | Text cleanup and phrase matching |
| `collections.Counter` | Word-frequency analysis |

## How it works

### Text analysis

NLTK's Treebank tokenizer splits text into word-like units. PromptSage then calculates word statistics, uses punctuation and line breaks as sentence boundaries, and counts keyword frequencies. Common English stopwords are filtered only from keyword results; they are never removed from the user's prompt. The built-in stopword list avoids downloading NLTK data at runtime.

Reading time is estimated at 200 words per minute. Sentence counts and reading time are practical estimates, not linguistic guarantees.

### Token counting

The app uses `tiktoken.get_encoding()` and the selected encoding's `encode()` method. It supports `cl100k_base` and `o200k_base`. Counts are exact for the selected encoding, but other models may use different tokenizers. A first use may require downloading the encoding vocabulary; if initialization fails, the app reports an error instead of showing an approximate count.

Whitespace-separated words and model tokens are different units. Byte-pair encoding (BPE) can split a word into multiple subword tokens, and punctuation or Unicode can affect the result.

### Rule-based optimization

The independent optimizer module applies a configurable list of known verbose phrases, then normalizes repeated whitespace. It does not remove general stopwords or create new instructions. Every change is deterministic and visible in `optimizer.py`. The user can edit the proposed prompt, and the comparison honestly reports when the edited version uses more tokens.

## Installation

In PowerShell, open the project directory and create a virtual environment:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents virtual environment activation, run the following in that terminal, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Run the app

```powershell
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`. Choose a sample prompt or enter your own, select an encoding, and click **Analyze Prompt**. Review and edit the suggested prompt before copying it.

## Run the tests

```powershell
python -m unittest discover -s tests -v
```

The token-counter unit tests use a deterministic mock encoding so they can run offline. Real token counts are provided by tiktoken at runtime when its encoding data is available.

## Project structure

```text
PromptSage/
├── app.py                    # Streamlit interface and session state
├── nlp_analyzer.py           # Word statistics and NLP insights
├── optimizer.py              # Deterministic prompt transformations
├── token_counter.py          # tiktoken loading and comparison metrics
├── requirements.txt          # Runtime dependencies
├── README.md
├── .gitignore
└── tests/
    ├── test_nlp_analyzer.py
    ├── test_optimizer.py
    └── test_token_counter.py
```

## Limitations

- Sentence splitting is heuristic; abbreviations and unusual punctuation can affect its results.
- The built-in stopword list and phrase rules are compact and English-focused.
- Phrase matching identifies configured wording but cannot determine semantic redundancy.
- Rule-based edits can alter meaning. Check the result and retain all necessary instructions and constraints.
- Token counts match the selected encoding, not necessarily every AI model's tokenizer.

## Viva questions

**What is the difference between tokenization and stopword removal?**  
Tokenization splits text into units. Stopword removal filters selected common words from an analysis such as keyword frequency. PromptSage keeps those words in the original prompt.

**Are words and tokens the same?**  
No. Word tokenization creates word-like units; BPE tokenization can split text into encoding-specific subword pieces.

**Is PromptSage a trained machine-learning model?**  
No. It uses classical NLP preprocessing, counters, regular expressions, and fixed rewrite rules. It does not train a model or call a generative AI service.

**How does the optimizer work?**  
It checks a small set of known verbose phrases, applies configured replacements, and normalizes whitespace. Other prompt content is retained as written.

**Why can token counts differ between encodings?**  
Encodings use different vocabularies and merge rules, so identical text can produce different token sequences.

**Does the optimized prompt have guaranteed identical meaning?**  
No. The rules are limited and deterministic, but users must review the suggestion and check its instructions and constraints.

**Why filter stopwords for keyword analysis?**  
Common words often carry less topic-specific information. Filtering them from the frequency list makes more descriptive terms easier to spot.

