"""
Лабораторная работа № 12
Реактивное и асинхронное программирование. Потоки данных (asyncio).
Базовый конвейер (Этапы 1-5 + улучшения), Индивидуальный вариант № 14 и 7 тестовых сценариев.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

SENTINEL = object()

RECORDS: list[dict[str, Any]] = [
    {"student": "Алия", "grade": 85},
    {"student": "Дамир", "grade": 54},
    {"student": "Руслан", "grade": 78},
    {"student": "", "grade": 91},
    {"student": "Мадина", "grade": 105},
]


# =========================================================
# Часть 1. Базовый конвейер оценок + тайм-аут и рейтинг
# =========================================================

def validate_grade_record(record: dict[str, Any]) -> None:
    """Проверяет корректность имени студента и оценки (0..100, не bool)."""
    student = str(record.get("student", "")).strip()
    grade = record.get("grade")
    if not student:
        raise ValueError("Не указано имя студента")
    if isinstance(grade, bool) or not isinstance(grade, (int, float)) or not 0 <= grade <= 100:
        raise ValueError("Оценка должна быть числом от 0 до 100")


async def process_grade_record(record: dict[str, Any], delay: float = 0.25) -> dict[str, Any]:
    """Асинхронная обработка и проверка одной записи об оценке."""
    await asyncio.sleep(delay)
    validate_grade_record(record)
    grade = record["grade"]
    return {
        "student": str(record["student"]).strip(),
        "grade": grade,
        "status": "зачет" if grade >= 60 else "незачет",
    }


async def grade_producer(
    queue: asyncio.Queue[Any],
    data: list[dict[str, Any]],
    workers_count: int,
    produce_delay: float = 0.15,
    verbose: bool = True,
) -> None:
    """Помещает исходные записи в ограниченную очередь и отправляет SENTINEL для каждого worker."""
    for record in data:
        await asyncio.sleep(produce_delay)
        await queue.put(record)
        if verbose:
            print("Получено:", record)

    for _ in range(workers_count):
        await queue.put(SENTINEL)


async def grade_consumer(
    name: str,
    queue: asyncio.Queue[Any],
    results: list[dict[str, Any]],
    errors: list[str],
    process_delay: float = 0.25,
    timeout_sec: float = 1.0,
    verbose: bool = True,
) -> None:
    """Извлекает записи из очереди, обрабатывает с тайм-аутом и гарантирует вызов task_done."""
    while True:
        item = await queue.get()
        try:
            if item is SENTINEL:
                if verbose:
                    print(f"{name} завершен")
                return

            try:
                async with asyncio.timeout(timeout_sec):
                    result = await process_grade_record(item, delay=process_delay)
                results.append(result)
                if verbose:
                    print(f"{name} обработал:", result)
            except TimeoutError:
                errors.append(f"{item}: превышен тайм-аут ({timeout_sec} с)")
            except ValueError as error:
                errors.append(f"{item}: {error}")
        finally:
            queue.task_done()


async def run_grade_pipeline(
    data: list[dict[str, Any]],
    maxsize: int = 3,
    workers_count: int = 2,
    produce_delay: float = 0.15,
    process_delay: float = 0.25,
    timeout_sec: float = 1.0,
    verbose: bool = True,
) -> dict[str, Any]:
    """Запускает полный цикл producer -> Queue -> consumers и возвращает сводную статистику."""
    queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=maxsize)
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    started = time.perf_counter()

    workers = [
        asyncio.create_task(
            grade_consumer(
                name=f"worker-{i}",
                queue=queue,
                results=results,
                errors=errors,
                process_delay=process_delay,
                timeout_sec=timeout_sec,
                verbose=verbose,
            )
        )
        for i in range(1, workers_count + 1)
    ]

    await grade_producer(
        queue=queue,
        data=data,
        workers_count=workers_count,
        produce_delay=produce_delay,
        verbose=verbose,
    )
    await queue.join()
    await asyncio.gather(*workers)

    elapsed = time.perf_counter() - started
    average = sum(item["grade"] for item in results) / len(results) if results else 0.0
    ranking = sorted(results, key=lambda item: item["grade"], reverse=True)

    return {
        "processed": len(results),
        "errors_count": len(errors),
        "average": average,
        "elapsed": elapsed,
        "results": results,
        "ranking": ranking,
        "errors": errors,
    }


# =========================================================
# Часть 2. Индивидуальный вариант № 14: Заявки техподдержки
# (PriorityQueue, 2 worker, очередь решённых заявок, среднее время)
# =========================================================

@dataclass(order=True)
class PrioritizedTicket:
    priority: int
    sequence: int
    ticket: dict[str, Any] = field(compare=False)
    enqueued_at: float = field(compare=False)


def validate_ticket(ticket: dict[str, Any]) -> None:
    """Проверяет поля заявки техподдержки: ID, приоритет (1..5) и описание."""
    ticket_id = ticket.get("id")
    priority = ticket.get("priority")
    description = str(ticket.get("description", "")).strip()

    if not isinstance(ticket_id, int) or ticket_id <= 0:
        raise ValueError("ID заявки должен быть положительным целым числом")
    if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 5:
        raise ValueError("Приоритет должен быть целым числом от 1 (высший) до 5 (низший)")
    if len(description) < 3:
        raise ValueError("Описание заявки слишком короткое")


async def support_producer(
    priority_queue: asyncio.PriorityQueue[PrioritizedTicket],
    tickets: list[dict[str, Any]],
    workers_count: int,
) -> None:
    """Загружает заявки в приоритетную очередь с ограничением maxsize."""
    for seq, ticket in enumerate(tickets):
        await asyncio.sleep(0.08)
        raw_priority = ticket.get("priority")
        sort_priority = raw_priority if isinstance(raw_priority, int) and not isinstance(raw_priority, bool) else 99
        item = PrioritizedTicket(
            priority=sort_priority,
            sequence=seq,
            ticket=ticket,
            enqueued_at=time.perf_counter(),
        )
        await priority_queue.put(item)

    for offset in range(workers_count):
        await priority_queue.put(
            PrioritizedTicket(
                priority=999,
                sequence=len(tickets) + offset,
                ticket={"_sentinel": True},
                enqueued_at=time.perf_counter(),
            )
        )


async def support_worker(
    name: str,
    priority_queue: asyncio.PriorityQueue[PrioritizedTicket],
    resolved_queue: asyncio.Queue[dict[str, Any]],
    errors: list[str],
    handling_times: list[float],
) -> None:
    """Обрабатывает заявки в порядке приоритета и помещает решённые в выходную очередь."""
    while True:
        item = await priority_queue.get()
        try:
            if item.ticket.get("_sentinel"):
                return

            try:
                validate_ticket(item.ticket)
                # Имитация времени решения заявки (срочные решаются быстрее)
                await asyncio.sleep(0.12 + 0.03 * item.priority)
                duration = time.perf_counter() - item.enqueued_at
                handling_times.append(duration)

                resolved_record = {
                    "id": item.ticket["id"],
                    "priority": item.ticket["priority"],
                    "description": item.ticket["description"].strip(),
                    "handled_by": name,
                    "handling_time_sec": round(duration, 3),
                }
                await resolved_queue.put(resolved_record)
            except ValueError as err:
                errors.append(f"Заявка {item.ticket}: {err}")
        finally:
            priority_queue.task_done()


async def run_variant_14_support_tickets() -> None:
    """Демонстрация индивидуального варианта № 14."""
    tickets_input: list[dict[str, Any]] = [
        {"id": 101, "priority": 4, "description": "Замена картриджа в принтере"},
        {"id": 102, "priority": 1, "description": "Не работает сервер авторизации"},
        {"id": 103, "priority": 2, "description": "Сбой доступа к базе данных"},
        {"id": 104, "priority": 3, "description": "Настройка Wi-Fi в аудитории 305"},
        {"id": 105, "priority": 0, "description": "Некорректный приоритет"},
        {"id": 106, "priority": 2, "description": ""},
    ]

    priority_queue: asyncio.PriorityQueue[PrioritizedTicket] = asyncio.PriorityQueue(maxsize=4)
    resolved_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    errors: list[str] = []
    handling_times: list[float] = []

    workers = [
        asyncio.create_task(
            support_worker(f"support-{i}", priority_queue, resolved_queue, errors, handling_times)
        )
        for i in range(1, 3)
    ]

    await support_producer(priority_queue, tickets_input, workers_count=2)
    await priority_queue.join()
    await asyncio.gather(*workers)

    resolved_list: list[dict[str, Any]] = []
    while not resolved_queue.empty():
        resolved_list.append(await resolved_queue.get())
        resolved_queue.task_done()

    avg_time = sum(handling_times) / len(handling_times) if handling_times else 0.0

    print("\n=== Индивидуальный вариант № 14: Заявки технической поддержки ===")
    print(f"Решено заявок: {len(resolved_list)} | Отклонено с ошибкой: {len(errors)}")
    print(f"Среднее время обработки заявки: {avg_time:.3f} с")
    print("Очередь решённых заявок (в порядке завершения):")
    for rec in resolved_list:
        print(
            f"  #{rec['id']} [приоритет {rec['priority']}] — {rec['description']} "
            f"({rec['handled_by']}, {rec['handling_time_sec']} с)"
        )
    for err in errors:
        print("  Ошибка:", err)


# =========================================================
# Часть 3. 7 тестовых сценариев из плана тестирования
# =========================================================

async def run_test_scenarios() -> None:
    """Проверяет все 7 обязательных тестовых сценариев из методички."""
    print("\n=== Проверка 7 тестовых сценариев ===")

    # Сценарий 1: Все записи корректны
    s1 = await run_grade_pipeline(
        [{"student": "Алия", "grade": 85}, {"student": "Дамир", "grade": 90}],
        produce_delay=0.01,
        process_delay=0.02,
        verbose=False,
    )
    assert s1["processed"] == 2 and s1["errors_count"] == 0

    # Сценарий 2: Пустое имя
    s2 = await run_grade_pipeline(
        [{"student": "   ", "grade": 80}, {"student": "Руслан", "grade": 75}],
        produce_delay=0.01,
        process_delay=0.02,
        verbose=False,
    )
    assert s2["processed"] == 1 and s2["errors_count"] == 1

    # Сценарий 3: Оценка < 0 или > 100
    s3 = await run_grade_pipeline(
        [{"student": "Алия", "grade": -5}, {"student": "Дамир", "grade": 101}],
        produce_delay=0.01,
        process_delay=0.02,
        verbose=False,
    )
    assert s3["processed"] == 0 and s3["errors_count"] == 2

    # Сценарий 4: Очередь maxsize=1 (обратное давление, данные не теряются)
    s4 = await run_grade_pipeline(
        [{"student": f"Студент-{i}", "grade": 70 + i} for i in range(4)],
        maxsize=1,
        workers_count=2,
        produce_delay=0.01,
        process_delay=0.02,
        verbose=False,
    )
    assert s4["processed"] == 4 and s4["errors_count"] == 0

    # Сценарий 5: Один и два потребителя (два потребителя быстрее)
    sample_batch = [{"student": f"Студент-{i}", "grade": 80} for i in range(6)]
    one_worker = await run_grade_pipeline(
        sample_batch, maxsize=3, workers_count=1, produce_delay=0.01, process_delay=0.05, verbose=False
    )
    two_workers = await run_grade_pipeline(
        sample_batch, maxsize=3, workers_count=2, produce_delay=0.01, process_delay=0.05, verbose=False
    )
    assert two_workers["elapsed"] < one_worker["elapsed"]

    # Сценарий 6: Тайм-аут / исключение в process (task_done вызывается, join завершается)
    s6 = await run_grade_pipeline(
        [{"student": "Алия", "grade": 85}],
        produce_delay=0.01,
        process_delay=0.2,
        timeout_sec=0.05,
        verbose=False,
    )
    assert s6["processed"] == 0 and s6["errors_count"] == 1

    # Сценарий 7: Пустой входной список (средний балл 0.0, без ZeroDivisionError)
    s7 = await run_grade_pipeline([], produce_delay=0.01, process_delay=0.02, verbose=False)
    assert s7["processed"] == 0 and s7["average"] == 0.0

    print(
        f"Все 7 сценариев пройдены успешно! "
        f"(1 worker: {one_worker['elapsed']:.3f} с vs 2 workers: {two_workers['elapsed']:.3f} с)"
    )


async def main() -> None:
    print("=== Базовый конвейер обработки оценок ===")
    summary = await run_grade_pipeline(RECORDS, maxsize=3, workers_count=2)
    print(f"Обработано: {summary['processed']}")
    print(f"Ошибок: {summary['errors_count']}")
    print(f"Средний балл: {summary['average']:.2f}")
    print(f"Время: {summary['elapsed']:.2f} с")
    print("Рейтинг студентов:", [(r["student"], r["grade"], r["status"]) for r in summary["ranking"]])
    for error in summary["errors"]:
        print("Ошибка:", error)

    await run_variant_14_support_tickets()
    await run_test_scenarios()


if __name__ == "__main__":
    asyncio.run(main())
