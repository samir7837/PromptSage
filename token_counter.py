"""Exact token counts for explicitly selected tiktoken encodings."""

from functools import lru_cache
import tiktoken

SUPPORTED_ENCODINGS = ("cl100k_base", "o200k_base")


@lru_cache(maxsize=2)
def get_encoding(name: str):
    if name not in SUPPORTED_ENCODINGS:
        raise ValueError(f"Unsupported encoding: {name}")
    return tiktoken.get_encoding(name)


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    return len(get_encoding(encoding_name).encode(text or ""))


def compare_prompts(original: str, optimized: str, encoding_name: str = "cl100k_base") -> dict[str, float | int]:
    original_tokens = count_tokens(original, encoding_name)
    optimized_tokens = count_tokens(optimized, encoding_name)
    saved = original_tokens - optimized_tokens
    return {
        "original_tokens": original_tokens, "optimized_tokens": optimized_tokens,
        "tokens_saved": saved,
        "reduction_percentage": (saved / original_tokens * 100) if original_tokens else 0.0,
        "original_words": len((original or "").split()), "optimized_words": len((optimized or "").split()),
        "character_reduction": len(original or "") - len(optimized or ""),
    }

