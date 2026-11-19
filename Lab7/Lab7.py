from functools import reduce
from typing import Callable, Iterable, Sequence


def validate_text(text: str) -> str:
    """Проверяет, что входной аргумент является непустой строкой."""
    if not isinstance(text, str):
        raise TypeError("Текст должен быть строкой (str)")
    if not text.strip():
        raise ValueError("Текст не должен быть пустым")
    return text


def tokenize_words(text: str) -> tuple[str, ...]:
    """Разбивает текст на очищенные слова в нижнем регистре, возвращая неизменяемый кортеж."""
    valid_text = validate_text(text)
    cleaned = "".join(ch.lower() if (ch.isalnum() or ch.isspace()) else " " for ch in valid_text)
    return tuple(cleaned.split())


def append_text_segment(segments: Sequence[str], new_segment: str) -> list[str]:
    """Неизменяемое преобразование: возвращает новый список сегментов текста без изменения исходного."""
    if isinstance(segments, str) or not isinstance(segments, Iterable):
        raise TypeError("Сегменты должны передаваться в виде последовательности строк")
    validated_list = [validate_text(seg) for seg in segments]
    return [*validated_list, validate_text(new_segment)]


def word_frequencies(text: str) -> dict[str, int]:
    """Чистая функция: возвращает новый словарь частот слов без изменения исходного текста."""
    tokens = tokenize_words(text)
    freq: dict[str, int] = {}
    for word in tokens:
        freq[word] = freq.get(word, 0) + 1
    return freq


def filter_words(
    tokens: Sequence[str],
    predicate: Callable[[str], bool],
) -> tuple[str, ...]:
    """Функция высшего порядка: отбирает слова по предикату в новый кортеж."""
    if isinstance(tokens, str):
        raise TypeError("Ожидается последовательность слов, а не единая строка")
    return tuple(filter(predicate, tokens))


def most_frequent_word(text: str) -> tuple[str, int]:
    """Возвращает пару (самое частое слово, количество вхождений)."""
    freqs = word_frequencies(text)
    return max(freqs.items(), key=lambda item: item[1])


def average_word_length(text: str) -> float:
    """Вычисляет среднюю длину слова в тексте через reduce."""
    tokens = tokenize_words(text)
    total_chars = reduce(lambda acc, w: acc + len(w), tokens, 0)
    return total_chars / len(tokens)


def recursive_count_word(tokens: Sequence[str], target: str, index: int = 0) -> int:
    """Рекурсивно подсчитывает количество вхождений слова target в последовательности tokens."""
    if index == 0:
        if isinstance(tokens, str):
            raise TypeError("Ожидается последовательность слов, а не строка")
        if not isinstance(target, str) or not target.strip():
            raise ValueError("Искомое слово должно быть непустой строкой")
        target = target.strip().lower()

    # Базовый случай: достигнут конец последовательности
    if index >= len(tokens):
        return 0

    # Рекурсивный случай: вклад текущего элемента + подсчёт в оставшейся части
    match = 1 if tokens[index].lower() == target else 0
    return match + recursive_count_word(tokens, target, index + 1)


def build_text_report(text: str, target_word: str) -> dict[str, object]:
    """Формирует неизменяемый аналитический отчёт по тексту."""
    tokens = tokenize_words(text)
    freqs = word_frequencies(text)
    top_word, top_count = most_frequent_word(text)
    return {
        "total_words": len(tokens),
        "unique_words": len(freqs),
        "frequencies": freqs,
        "most_frequent": (top_word, top_count),
        "average_word_length": round(average_word_length(text), 2),
        "target_word": target_word.strip().lower(),
        "target_count": recursive_count_word(tokens, target_word),
    }


def main() -> None:
    """Императивная оболочка: демонстрация анализа текста без побочных эффектов в ядре."""
    paragraphs = [
        "Функциональный стиль делает код предсказуемым и чистым.",
        "Чистый код легче тестировать, а чистый стиль упрощает поддержку.",
    ]
    extended_paragraphs = append_text_segment(
        paragraphs, "Рекурсия решает задачу через меньшую подзадачу."
    )
    full_text = " ".join(extended_paragraphs)
    report = build_text_report(full_text, "чистый")

    print("Исходный список абзацев:", paragraphs)
    print("Новый список абзацев:", extended_paragraphs)
    print("Отчёт по тексту:", report)


if __name__ == "__main__":
    main()
