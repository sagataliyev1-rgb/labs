import unittest
from lab7 import (
    append_text_segment,
    average_word_length,
    build_text_report,
    filter_words,
    most_frequent_word,
    recursive_count_word,
    tokenize_words,
    word_frequencies,
)


class TestTextAnalysisFunctionalCore(unittest.TestCase):
    def test_immutability_of_input_list_and_text(self) -> None:
        source_segments = ["Первый абзац текста.", "Второй абзац текста."]
        snapshot = source_segments.copy()
        original_text = "Код без побочных эффектов."

        new_segments = append_text_segment(source_segments, "Третий абзац.")
        _ = word_frequencies(original_text)
        _ = build_text_report(original_text, "код")

        self.assertEqual(source_segments, snapshot)
        self.assertIsNot(new_segments, source_segments)
        self.assertEqual(original_text, "Код без побочных эффектов.")

    def test_tokenize_and_word_frequencies(self) -> None:
        sample = "Python — это просто! Python, это гибко."
        tokens = tokenize_words(sample)
        self.assertEqual(tokens, ("python", "это", "просто", "python", "это", "гибко"))
        self.assertEqual(
            word_frequencies(sample),
            {"python": 2, "это": 2, "просто": 1, "гибко": 1},
        )

    def test_determinism_same_arguments_same_result(self) -> None:
        text = "рекурсия и чистые функции"
        self.assertEqual(build_text_report(text, "рекурсия"), build_text_report(text, "рекурсия"))

    def test_filter_words_higher_order(self) -> None:
        tokens = tokenize_words("код рекурсия функция стек")
        long_words = filter_words(tokens, lambda w: len(w) > 5)
        self.assertEqual(long_words, ("рекурсия", "функция"))

    def test_most_frequent_and_average_length(self) -> None:
        text = "дом сад дом лес"
        self.assertEqual(most_frequent_word(text), ("дом", 2))
        self.assertEqual(average_word_length(text), 3.0)

    def test_recursive_count_word_normal_and_absent(self) -> None:
        tokens = ("данные", "код", "данные", "тест", "данные")
        self.assertEqual(recursive_count_word(tokens, "данные"), 3)
        self.assertEqual(recursive_count_word(tokens, "отсутствует"), 0)
        self.assertEqual(recursive_count_word((), "данные"), 0)

    def test_error_on_empty_or_whitespace_text(self) -> None:
        with self.assertRaises(ValueError):
            word_frequencies("   ")

    def test_error_on_invalid_input_types(self) -> None:
        with self.assertRaises(TypeError):
            tokenize_words(12345)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            recursive_count_word(("один", "два"), "")


if __name__ == "__main__":
    unittest.main()
