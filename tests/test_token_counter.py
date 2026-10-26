import unittest
from unittest.mock import patch
import re

import token_counter


class FakeEncoding:
    """Deterministic stand-in so unit tests do not need network-fetched vocab files."""
    def encode(self, text):
        return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)


class TokenCounterTests(unittest.TestCase):
    def setUp(self):
        self.encoding_patch = patch.object(token_counter, "get_encoding", return_value=FakeEncoding())
        self.encoding_patch.start()

    def tearDown(self):
        self.encoding_patch.stop()

    def test_original_and_optimized_counts(self):
        result = token_counter.compare_prompts("Can you please explain this?", "Explain this?")
        self.assertGreater(result["original_tokens"], 0)
        self.assertEqual(result["optimized_tokens"], token_counter.count_tokens("Explain this?"))
        self.assertEqual(result["tokens_saved"], result["original_tokens"] - result["optimized_tokens"])

    def test_zero_and_negative_savings(self):
        empty = token_counter.compare_prompts("", "")
        self.assertEqual(empty["reduction_percentage"], 0)
        expanded = token_counter.compare_prompts("Hi", "Hi there, how are you today?")
        self.assertLess(expanded["tokens_saved"], 0)
        self.assertLess(expanded["reduction_percentage"], 0)

    def test_unicode(self):
        self.assertGreater(token_counter.count_tokens("नमस्ते café 🌱"), 0)


if __name__ == "__main__":
    unittest.main()

