"""
Лабораторная работа № 9
Декларативная обработка данных средствами Python, SQL и регулярных выражений.
Базовые задания (1-6) + индивидуальный вариант (Вариант № 3: Допуск к экзамену).
"""

import re
import sqlite3
from typing import Any

GROUP_PATTERN = r"^[A-Z]{2}-\d{2}-\d{2}$"
EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

INITIAL_STUDENTS: list[dict[str, Any]] = [
    {"name": "Aida", "group": "IS-24-01", "score": 82, "attendance": 91, "email": "aida@atu.edu.kz"},
    {"name": "Miras", "group": "IS-24-01", "score": 69, "attendance": 88, "email": "miras@atu.edu.kz"},
    {"name": "Dana", "group": "IS-24-02", "score": 91, "attendance": 96, "email": "dana@atu.edu.kz"},
    {"name": "Timur", "group": "IS-24-02", "score": 74, "attendance": 62, "email": "timur_at_atu.kz"},
    {"name": "Aliya", "group": "IS-24-03", "score": 87, "attendance": 79, "email": "aliya@atu.edu.kz"},
    {"name": "Arman", "group": "IS-24-03", "score": 55, "attendance": 72, "email": "arman@atu.edu.kz"},
]


def run_task_1(students: list[dict[str, Any]]) -> list[str]:
    """Задание 1: Сравнение императивного цикла и декларативного спискового включения."""
    passed_imperative: list[str] = []
    for student in students:
        if student["score"] >= 75:
            passed_imperative.append(student["name"])

    passed_declarative: list[str] = [
        student["name"]
        for student in students
        if student["score"] >= 75
    ]

    print("--- Задание 1: Сравнение двух стилей ---")
    print("Императивный список (score >= 75):", passed_imperative)
    print("Декларативный список (score >= 75):", passed_declarative)
    print("Результаты совпадают (==):", passed_imperative == passed_declarative)
    return passed_declarative


def run_task_2(students: list[dict[str, Any]]) -> dict[str, Any]:
    """Задание 2: Проверка условий через any/all и расчёт среднего с защитой от пустого списка."""
    has_excellent = any(s["score"] >= 90 for s in students)
    all_attended = all(s["attendance"] >= 60 for s in students)
    average = (
        sum(s["score"] for s in students) / len(students)
        if students
        else 0.0
    )

    print("\n--- Задание 2: Условия для коллекции ---")
    print("Есть отличник (score >= 90):", has_excellent)
    print("Посещаемость всех не ниже 60%:", all_attended)
    print("Средний балл:", round(average, 1))

    # Демонстрация изменения показателя attendance так, чтобы all_attended стал False
    modified_students = [
        {**s, "attendance": 55} if s["name"] == "Timur" else dict(s)
        for s in students
    ]
    all_attended_after = all(s["attendance"] >= 60 for s in modified_students)
    print("После снижения attendance у Timur до 55%, all_attended:", all_attended_after)

    return {
        "has_excellent": has_excellent,
        "all_attended": all_attended,
        "average": round(average, 1),
        "all_attended_after": all_attended_after,
    }


def run_task_3(students: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Задание 3: Проверка кодов групп и email регулярными выражениями + исправление ошибки."""
    invalid_groups = [
        s["group"]
        for s in students
        if not re.fullmatch(GROUP_PATTERN, s["group"])
    ]
    invalid_emails = [
        s["email"]
        for s in students
        if not re.fullmatch(EMAIL_PATTERN, s["email"])
    ]

    print("\n--- Задание 3: Проверка данных регулярными выражениями ---")
    print("Ошибочные группы:", invalid_groups)
    print("Ошибочные email:", invalid_emails)

    # Исправляем некорректный адрес timur_at_atu.kz -> timur@atu.edu.kz в новом списке
    corrected_students = [
        {**s, "email": "timur@atu.edu.kz"} if s["email"] == "timur_at_atu.kz" else dict(s)
        for s in students
    ]
    rechecked_invalid_emails = [
        s["email"]
        for s in corrected_students
        if not re.fullmatch(EMAIL_PATTERN, s["email"])
    ]
    print("Повторная проверка email после исправления:", rechecked_invalid_emails)
    return corrected_students


def create_sqlite_db(students: list[dict[str, Any]]) -> sqlite3.Connection:
    """Задание 4: Создание таблицы в оперативной памяти и безопасная вставка данных."""
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE students (
            name TEXT NOT NULL,
            group_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            attendance INTEGER NOT NULL,
            email TEXT NOT NULL
        )
        """
    )
    rows = [
        (s["name"], s["group"], s["score"], s["attendance"], s["email"])
        for s in students
    ]
    cursor.executemany(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    connection.commit()
    return connection


def run_task_5(connection: sqlite3.Connection) -> None:
    """Задание 5: Выборка, сортировка, группировка и агрегирование в SQL."""
    cursor = connection.cursor()

    print("\n--- Задание 5а: Выборка и сортировка (score >= 75 AND attendance >= 70) ---")
    select_query = """
    SELECT name, score, attendance
    FROM students
    WHERE score >= 75 AND attendance >= 70
    ORDER BY score DESC
    """
    rows = cursor.execute(select_query).fetchall()
    if not rows:
        print("Подходящих студентов не найдено.")
    else:
        for name, score, attendance in rows:
            print(f"Студент: {name} | балл: {score} | посещаемость: {attendance}%")

    print("\n--- Задание 5б: Группировка и агрегирование (HAVING AVG(score) >= 70) ---")
    group_query = """
    SELECT group_name,
           COUNT(*) AS student_count,
           ROUND(AVG(score), 1) AS average_score
    FROM students
    GROUP BY group_name
    HAVING AVG(score) >= 70
    ORDER BY average_score DESC
    """
    group_rows = cursor.execute(group_query).fetchall()
    if not group_rows:
        print("Группы со средним баллом >= 70 отсутствуют.")
    else:
        for group_name, student_count, avg_score in group_rows:
            print(f"Группа: {group_name} | студентов: {student_count} | средний балл: {avg_score}")


def run_task_6(connection: sqlite3.Connection) -> None:
    """Задание 6: Интеграция SQL-запроса, проверки email через regex и вывода в Python."""
    cursor = connection.cursor()
    query = """
    SELECT name, group_name, score, email
    FROM students
    WHERE score >= 70 AND attendance >= 70
    ORDER BY score DESC
    """
    result = cursor.execute(query).fetchall()
    valid_result = [
        row for row in result
        if re.fullmatch(EMAIL_PATTERN, row[3])
    ]

    print("\n--- Задание 6: Интегрированный рейтинг допущенных студентов ---")
    if not valid_result:
        print("Список допущенных студентов с корректным email пуст.")
        return

    for place, (name, group_name, score, email) in enumerate(valid_result, start=1):
        print(f"{place}. {name} | {group_name} | {score} | {email}")


def run_variant_3_exam_admission(
    connection: sqlite3.Connection,
    min_score: int = 70,
    min_attendance: int = 70,
) -> None:
    """
    Индивидуальный вариант № 3: Допуск к экзамену.
    Условие 1: score >= min_score
    Условие 2: attendance >= min_attendance
    Дополнительное требование: показать количество допущенных по группам + проверка email и групп.
    """
    cursor = connection.cursor()
    admitted_query = """
    SELECT name, group_name, score, attendance, email
    FROM students
    WHERE score >= ? AND attendance >= ?
    ORDER BY group_name ASC, score DESC
    """
    admitted_rows = cursor.execute(admitted_query, (min_score, min_attendance)).fetchall()

    # Декларативная фильтрация записей с корректными кодом группы и email
    verified_admitted = [
        {
            "name": name,
            "group_name": group_name,
            "score": score,
            "attendance": attendance,
            "email": email,
        }
        for name, group_name, score, attendance, email in admitted_rows
        if re.fullmatch(GROUP_PATTERN, group_name) and re.fullmatch(EMAIL_PATTERN, email)
    ]

    # Агрегирование количества допущенных по группам через SQL с параметрами
    counts_query = """
    SELECT group_name, COUNT(*) AS admitted_count
    FROM students
    WHERE score >= ? AND attendance >= ?
    GROUP BY group_name
    ORDER BY admitted_count DESC, group_name ASC
    """
    group_counts = cursor.execute(counts_query, (min_score, min_attendance)).fetchall()

    print("\n=== Индивидуальный вариант № 3: Допуск к экзамену ===")
    if not verified_admitted:
        print("Нет студентов, допущенных к экзамену по заданным критериям.")
    else:
        print("Допущенные студенты (с валидными группой и email):")
        for item in verified_admitted:
            print(
                f"  - {item['name']} ({item['group_name']}): "
                f"балл={item['score']}, посещаемость={item['attendance']}%, email={item['email']}"
            )

    print("\nКоличество допущенных по группам:")
    if not group_counts:
        print("  Данных по группам нет.")
    else:
        for group_name, cnt in group_counts:
            print(f"  Группа {group_name}: {cnt} чел.")


def main() -> None:
    # Расширим исходный набор 2 записями для наглядной демонстрации разных случаев
    students_data: list[dict[str, Any]] = [
        *INITIAL_STUDENTS,
        {"name": "Dias", "group": "IS-24-01", "score": 94, "attendance": 85, "email": "dias@atu.edu.kz"},
        {"name": "Madina", "group": "IS-24-03", "score": 72, "attendance": 78, "email": "madina@atu.edu.kz"},
    ]

    run_task_1(students_data)
    run_task_2(students_data)
    corrected_students = run_task_3(students_data)

    connection = create_sqlite_db(corrected_students)
    try:
        run_task_5(connection)
        run_task_6(connection)
        run_variant_3_exam_admission(connection, min_score=70, min_attendance=70)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
