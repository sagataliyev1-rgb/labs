"""
Лабораторная работа № 11
Событийная парадигма: события, обработчики и цикл графического интерфейса (Tkinter).
Базовая функциональность + дополнительная функция (удаление выбранной записи по клавише Delete).
"""

import tkinter as tk
from tkinter import messagebox, ttk


def main() -> None:
    # Этап 1: Создание окна и переменных состояния интерфейса
    root = tk.Tk()
    root.title("Регистрация студента")
    root.geometry("620x440")
    root.minsize(520, 380)

    student_var = tk.StringVar()
    course_var = tk.StringVar(value="Парадигмы программирования")
    status_var = tk.StringVar(value="Готово")
    count_var = tk.StringVar(value="Регистраций: 0")

    # Модель предметной области хранится отдельно от виджетов
    registrations: list[tuple[str, str]] = []
    status_timer_id: str | None = None

    # Этап 2: Создание интерфейса с единым менеджером геометрии grid внутри frame
    frame = ttk.Frame(root, padding=16)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(3, weight=1)

    ttk.Label(frame, text="Имя студента:").grid(row=0, column=0, sticky="w", pady=5)
    student_entry = ttk.Entry(frame, textvariable=student_var)
    student_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=5)

    ttk.Label(frame, text="Дисциплина:").grid(row=1, column=0, sticky="w", pady=5)
    course_box = ttk.Combobox(
        frame,
        textvariable=course_var,
        state="readonly",
        values=[
            "Парадигмы программирования",
            "Базы данных",
            "Искусственный интеллект",
        ],
    )
    course_box.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=5)

    register_button = ttk.Button(frame, text="Зарегистрировать")
    register_button.grid(row=2, column=1, sticky="ew", padx=8, pady=8)

    clear_button = ttk.Button(frame, text="Очистить список")
    clear_button.grid(row=2, column=2, sticky="ew", pady=8)

    result_list = tk.Listbox(frame, height=10)
    result_list.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=8)

    ttk.Label(frame, textvariable=count_var).grid(row=4, column=0, sticky="w")
    ttk.Label(frame, textvariable=status_var).grid(row=4, column=1, columnspan=2, sticky="e")

    # Этап 3: Обработчики событий и управление состоянием
    def update_counter() -> None:
        count_var.set(f"Регистраций: {len(registrations)}")

    def reset_status() -> None:
        nonlocal status_timer_id
        status_timer_id = None
        status_var.set("Готово")

    def set_status(text: str) -> None:
        """Обновляет строку состояния и планирует сброс на 'Готово' через 2.5 сек без блокировки GUI."""
        nonlocal status_timer_id
        if status_timer_id is not None:
            root.after_cancel(status_timer_id)
        status_var.set(text)
        status_timer_id = root.after(2500, reset_status)

    def register() -> None:
        student = student_var.get().strip()
        course = course_var.get()

        if len(student) < 2:
            messagebox.showwarning("Проверка", "Введите имя студента (минимум 2 символа)")
            student_entry.focus_set()
            return

        item = (student, course)
        if item in registrations:
            set_status("Такая регистрация уже существует")
            student_entry.focus_set()
            return

        registrations.append(item)
        result_list.insert(tk.END, f"{student} - {course}")
        update_counter()
        set_status("Регистрация добавлена")
        student_var.set("")
        student_entry.focus_set()

    def register_from_event(event: tk.Event) -> None:
        """Адаптер клавиатурного события Enter для вызова общей логики регистрации."""
        register()

    def delete_selected(event: tk.Event | None = None) -> None:
        """Дополнительная функция (Вариант 1): удаление выбранной записи клавишей Delete."""
        selection = result_list.curselection()
        if not selection:
            set_status("Выберите запись для удаления")
            return
        index = int(selection[0])
        removed_student, removed_course = registrations.pop(index)
        result_list.delete(index)
        update_counter()
        set_status(f"Удалено: {removed_student} - {removed_course}")

    def clear_all() -> None:
        if not registrations:
            set_status("Список уже пуст")
            return
        if not messagebox.askyesno("Подтверждение", "Удалить все регистрации?"):
            set_status("Очистка отменена")
            return
        registrations.clear()
        result_list.delete(0, tk.END)
        update_counter()
        set_status("Список очищен")
        student_entry.focus_set()

    # Этап 4: Привязка обработчиков и запуск главного цикла событий
    register_button.config(command=register)
    clear_button.config(command=clear_all)
    root.bind("<Return>", register_from_event)
    result_list.bind("<Delete>", delete_selected)

    student_entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
