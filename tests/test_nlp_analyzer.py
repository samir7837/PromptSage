import unittest

from nlp_analyzer import analyze_prompt


class AnalyzerTests(unittest.TestCase):
    def test_empty(self):
        result = analyze_prompt("")
        self.assertEqual((result["words"], result["sentences"], result["characters"]), (0, 0, 0))

    def test_normal_prompt_and_stopwords(self):
        result = analyze_prompt("Explain NLP clearly. Explain tokenization too!")
        self.assertEqual(result["sentences"], 2)
        self.assertEqual(result["frequent_words"][0], ("explain", 2))
        self.assertEqual(result["words"], 6)

    def test_whitespace_and_unicode(self):
        result = analyze_prompt("Café\n\nNLP   works.")
        self.assertEqual(result["words"], 3)
        self.assertEqual(result["characters"], len("Café\n\nNLP   works."))

    def test_fillers_and_repetition(self):
        result = analyze_prompt("In a very simple way, explain NLP. Explain NLP.")
        self.assertIn("in a very simple way", result["filler_phrases"])
        self.assertEqual(result["repeated_words"]["explain"], 2)


if __name__ == "__main__":
    unittest.main()

