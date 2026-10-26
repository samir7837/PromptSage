import unittest

from optimizer import optimize_prompt


class OptimizerTests(unittest.TestCase):
    def test_removes_politeness_and_normalizes_space(self):
        self.assertEqual(optimize_prompt("Can you please   explain NLP?"), "explain NLP?")

    def test_preserves_constraints_and_numbers(self):
        text = "Could you please summarize in 150 words and include 1789 and 1799."
        result = optimize_prompt(text)
        for term in ("150", "1789", "1799", "summarize"):
            self.assertIn(term, result)

    def test_no_change(self):
        text = "Summarize this report in five bullet points."
        self.assertEqual(optimize_prompt(text), text)

    def test_unicode_and_newlines(self):
        self.assertEqual(optimize_prompt("Please note that café is open.\n\nThanks!"), "café is open.\nThanks!")


if __name__ == "__main__":
    unittest.main()

