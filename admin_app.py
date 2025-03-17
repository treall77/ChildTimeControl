import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import shutil
import json
import subprocess
from tkinter import Tk, Button


# Константи для стилів
FONT = ("Arial", 14)
TITLE_FONT = ("Arial", 16)

class TaskManager:
    def __init__(self):
        self.english_tasks_file = "english_tasks.json"
        self.math_tasks_file = "math_tasks.json"
        self.english_tasks = self.load_tasks(self.english_tasks_file)
        self.math_tasks = self.load_tasks(self.math_tasks_file)

    def load_tasks(self, filename):
        """Завантажує завдання з JSON-файлу."""
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def save_tasks(self, tasks, filename):
        """Зберігає завдання у JSON-файл."""
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(tasks, file, ensure_ascii=False, indent=4)

    def add_task(self, category, question, answer, reward_minutes):
        """Додає нове завдання до відповідної категорії."""
        task = {
            "question": question,
            "answer": answer,
            "reward_minutes": reward_minutes,
            "times_solved": 0
        }
        if category == "english":
            self.english_tasks.append(task)
            self.save_tasks(self.english_tasks, self.english_tasks_file)
        elif category == "math":
            self.math_tasks.append(task)
            self.save_tasks(self.math_tasks, self.math_tasks_file)

    def remove_task(self, category, task_index):
        """Видаляє завдання з відповідної категорії."""
        if category == "english":
            self.english_tasks.pop(task_index)
            self.save_tasks(self.english_tasks, self.english_tasks_file)
        elif category == "math":
            self.math_tasks.pop(task_index)
            self.save_tasks(self.math_tasks, self.math_tasks_file)

    def get_tasks(self, category):
        """Повертає завдання з відповідної категорії."""
        if category == "english":
            return self.english_tasks
        elif category == "math":
            return self.math_tasks
        return []

class ConfigManager:
    def __init__(self):
        self.config_file = "config.json"
        self.config = self.load_config()

    def load_config(self):
        """Завантажує конфігурацію з JSON-файлу."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as file:
                return json.load(file)
        return {
            "auto_shutdown": False,
            "max_earned_time": 60,
            "remove_after_solved": 3
        }

    def save_config(self):
        """Зберігає конфігурацію у JSON-файл."""
        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(self.config, file, ensure_ascii=False, indent=4)

    def set_auto_shutdown(self, value):
        """Встановлює налаштування автоматичного вимкнення ПК."""
        self.config["auto_shutdown"] = value
        self.save_config()

    def set_max_earned_time(self, value):
        """Встановлює максимальний ігровий час."""
        self.config["max_earned_time"] = value
        self.save_config()

    def set_remove_after_solved(self, value):
        """Встановлює параметр 'Завдання видаляється після проходження раз'."""
        self.config["remove_after_solved"] = value
        self.save_config()

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Child Time Control - Адмін")
        self.root.geometry("800x600")

         

        self.task_manager = TaskManager()
        self.config_manager = ConfigManager()

        self.show_admin_interface()

    def add_to_startup(self):
        """
        Викликає startup_manager.py для додавання до автозапуску.
        """
        try:
            subprocess.run(['python', 'startup_manager.py', 'add'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Помилка: {e}")

    def remove_from_startup(self):
        """
        Викликає startup_manager.py для видалення з автозапуску.
        """
        try:
            subprocess.run(['python', 'startup_manager.py', 'remove'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Помилка: {e}")
    

    def clear_screen(self):
        """
        Очищає екран від усіх віджетів.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.unbind_all("<Return>")  # Видаляємо всі прив'язки до Enter

    def show_auto_close_message(self, title, message, delay=3000):
        """
        Показує повідомлення, яке закривається автоматично через delay мілісекунд.
        """
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("300x100")
        popup.attributes("-topmost", True)

        label = tk.Label(popup, text=message, font=FONT)
        label.pack(pady=20)

        popup.after(delay, popup.destroy)

    def show_admin_interface(self):
        """
        Відображає головний інтерфейс адміна з прокруткою всього вікна.
        """
        self.clear_screen()

        # Створення основного контейнера з прокруткою
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)

        # Створення Canvas (полотно) для прокрутки
        canvas = tk.Canvas(container)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Додавання вертикальної прокрутки
        scrollbar = tk.Scrollbar(container, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Налаштування Canvas для роботи з прокруткою
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Створення Frame всередині Canvas для розміщення елементів
        inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # Додавання елементів інтерфейсу до inner_frame
        tk.Label(inner_frame, text="Адмін інтерфейс", font=TITLE_FONT).pack()

        # Вибір категорії завдання
        tk.Label(inner_frame, text="Категорія:", font=FONT).pack()
        self.category_var = tk.StringVar(value="english")
        tk.Radiobutton(inner_frame, text="Англійська", variable=self.category_var, value="english", font=FONT).pack()
        tk.Radiobutton(inner_frame, text="Математика", variable=self.category_var, value="math", font=FONT).pack()

        tk.Button(inner_frame, text="Видалити всі завдання", command=self.remove_all_tasks, font=FONT).pack()
        tk.Button(inner_frame, text="Завантажити завдання", command=self.load_tasks_from_file, font=FONT).pack()
        tk.Button(inner_frame, text="Переглянути завдання", command=self.view_tasks, font=FONT).pack()
        tk.Button(inner_frame, text="Налаштування", command=self.show_settings, font=FONT).pack()
        tk.Button(inner_frame, text="Вийти", command=self.root.destroy, font=FONT).pack()

        # Прив'язка події Enter до кнопки "Додати завдання"
        self.root.bind("<Return>", lambda event: self.add_task())

        # Поле для масового додавання завдань
        tk.Label(inner_frame, text="Масове додавання завдань (формат: Питання; Відповідь; Хвилини):", font=FONT).pack()

        # Текстове поле з вертикальною прокруткою
        text_frame = tk.Frame(inner_frame)
        text_frame.pack()

        self.bulk_tasks_entry = tk.Text(text_frame, height=10, width=80, font=FONT, wrap=tk.WORD)
        self.bulk_tasks_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Вертикальна прокрутка для текстового поля
        text_scrollbar = tk.Scrollbar(text_frame, command=self.bulk_tasks_entry.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.bulk_tasks_entry.config(yscrollcommand=text_scrollbar.set)

        # Кнопка для вставки з буферу обміну
        tk.Button(inner_frame, text="Вставити з буферу обміну", command=self.paste_from_clipboard, font=FONT).pack()

        # Кнопка для додавання кількох завдань
        tk.Button(inner_frame, text="Додати кілька завдань", command=self.add_bulk_tasks, font=FONT).pack()

        # Підтримка прокрутки колесом миші
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Видалення прив'язки події при закритті вікна
        def on_close():
            canvas.unbind("<MouseWheel>")
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_close)

    def paste_from_clipboard(self):
        """
        Вставляє текст з буферу обміну у поле для масового додавання завдань.
        """
        try:
            clipboard_text = self.root.clipboard_get()  # Отримуємо текст з буферу обміну
            self.bulk_tasks_entry.insert(tk.END, clipboard_text)  # Вставляємо текст у поле
        except tk.TclError:
            self.show_auto_close_message("Помилка", "Буфер обміну порожній або містить не текст")

    def add_bulk_tasks(self):
        """
        Додає кілька завдань з текстового поля.
        """
        bulk_text = self.bulk_tasks_entry.get("1.0", tk.END).strip()
        if not bulk_text:
            self.show_auto_close_message("Помилка", "Введіть завдання")
            return

        tasks_added = 0
        for line in bulk_text.split("\n"):
            try:
                question, answer, reward_minutes = map(str.strip, line.split(";"))
                reward_minutes = int(reward_minutes)
                self.task_manager.add_task(self.category_var.get(), question, answer, reward_minutes)
                tasks_added += 1
            except (ValueError, IndexError):
                continue

        self.show_auto_close_message("Успіх", f"Додано {tasks_added} завдань")
        self.bulk_tasks_entry.delete("1.0", tk.END)

    def add_task(self):
        """
        Додає нове завдання на основі введених даних.
        """
        category = self.category_var.get()
        question = self.question_entry.get()
        answer = self.answer_entry.get()
        try:
            reward_minutes = int(self.reward_entry.get() or 1)
        except ValueError:
            self.show_auto_close_message("Помилка", "Хвилини нагороди мають бути числом")
            return

        self.task_manager.add_task(category, question, answer, reward_minutes)
        self.show_auto_close_message("Успіх", "Завдання додано")
        self.question_entry.delete(0, tk.END)
        self.answer_entry.delete(0, tk.END)
        self.reward_entry.delete(0, tk.END)

    def remove_all_tasks(self):
        """
        Видаляє всі завдання.
        """
        category = self.category_var.get()
        if category == "english":
            self.task_manager.english_tasks = []
            self.task_manager.save_tasks(self.task_manager.english_tasks, self.task_manager.english_tasks_file)
        elif category == "math":
            self.task_manager.math_tasks = []
            self.task_manager.save_tasks(self.task_manager.math_tasks, self.task_manager.math_tasks_file)
        self.show_auto_close_message("Успіх", "Всі завдання видалено")

    def load_tasks_from_file(self):
        """
        Завантажує завдання з JSON-файлу.
        """
        file_path = filedialog.askopenfilename(
            title="Виберіть файл завдань",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")))
        
        if file_path:
            category = self.category_var.get()
            if category == "english":
                self.task_manager.english_tasks = self.task_manager.load_tasks(file_path)
                self.task_manager.save_tasks(self.task_manager.english_tasks, self.task_manager.english_tasks_file)
            elif category == "math":
                self.task_manager.math_tasks = self.task_manager.load_tasks(file_path)
                self.task_manager.save_tasks(self.task_manager.math_tasks, self.task_manager.math_tasks_file)
            self.show_auto_close_message("Успіх", "Завдання завантажено")
        else:
            self.show_auto_close_message("Помилка", "Не вдалося завантажити завдання")

    def view_tasks(self):
        """
        Відображає завдання у вигляді таблиці з можливістю редагування.
        """
        tasks_window = tk.Toplevel(self.root)
        tasks_window.title("Список завдань")
        tasks_window.geometry("800x400")

        # Створення таблиці
        columns = ("#1", "#2", "#3", "#4", "#5")
        self.tasks_table = ttk.Treeview(tasks_window, columns=columns, show="headings")
        self.tasks_table.heading("#1", text="№")
        self.tasks_table.heading("#2", text="Запитання")
        self.tasks_table.heading("#3", text="Відповідь")
        self.tasks_table.heading("#4", text="Хвилини")
        self.tasks_table.heading("#5", text="Виконано разів")
        self.tasks_table.pack(fill=tk.BOTH, expand=True)

        # Очищення таблиці перед оновленням
        for row in self.tasks_table.get_children():
            self.tasks_table.delete(row)

        # Додавання завдань до таблиці
        category = self.category_var.get()
        tasks = self.task_manager.get_tasks(category)
        for i, task in enumerate(tasks):
            self.tasks_table.insert("", tk.END, values=(
                i + 1,
                task["question"],
                task["answer"],
                task["reward_minutes"],
                task["times_solved"]  # Виконано разів
            ))

        # Кнопки для редагування та видалення
        button_frame = tk.Frame(tasks_window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Редагувати", command=lambda: self.edit_task(self.tasks_table.selection()), font=FONT).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Видалити", command=lambda: self.delete_task(self.tasks_table.selection()), font=FONT).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Закрити", command=tasks_window.destroy, font=FONT).pack(side=tk.RIGHT, padx=10)

    def edit_task(self, selected_item):
        """
        Редагує обране завдання.
        """
        if not selected_item:
            self.show_auto_close_message("Помилка", "Виберіть завдання для редагування")
            return

        # Отримуємо індекс обраного завдання
        task_index = int(self.tasks_table.item(selected_item, "values")[0]) - 1
        category = self.category_var.get()
        tasks = self.task_manager.get_tasks(category)
        task = tasks[task_index]

        # Створення вікна для редагування
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редагування завдання")
        edit_window.geometry("400x300")

        # Поле для редагування питання
        tk.Label(edit_window, text="Запитання:", font=FONT).pack()
        question_entry = tk.Entry(edit_window, width=50, font=FONT)
        question_entry.insert(0, task["question"])
        question_entry.pack()

        # Поле для редагування відповіді
        tk.Label(edit_window, text="Відповідь:", font=FONT).pack()
        answer_entry = tk.Entry(edit_window, width=50, font=FONT)
        answer_entry.insert(0, task["answer"])
        answer_entry.pack()

        # Поле для редагування хвилин нагороди
        tk.Label(edit_window, text="Хвилини нагороди:", font=FONT).pack()
        reward_entry = tk.Entry(edit_window, width=50, font=FONT)
        reward_entry.insert(0, str(task["reward_minutes"]))
        reward_entry.pack()

        # Кнопка для збереження змін
        def save_changes():
            task["question"] = question_entry.get()
            task["answer"] = answer_entry.get()
            task["reward_minutes"] = int(reward_entry.get())
            if category == "english":
                self.task_manager.save_tasks(self.task_manager.english_tasks, self.task_manager.english_tasks_file)
            elif category == "math":
                self.task_manager.save_tasks(self.task_manager.math_tasks, self.task_manager.math_tasks_file)
            self.show_auto_close_message("Успіх", "Завдання оновлено")
            edit_window.destroy()
            self.view_tasks()  # Оновлюємо таблицю

        tk.Button(edit_window, text="Зберегти", command=save_changes, font=FONT).pack(pady=10)

    def delete_task(self, selected_item):
        """
        Видаляє обране завдання.
        """
        if not selected_item:
            self.show_auto_close_message("Помилка", "Виберіть завдання для видалення")
            return

        # Отримуємо індекс обраного завдання
        task_index = int(self.tasks_table.item(selected_item, "values")[0]) - 1
        category = self.category_var.get()
        self.task_manager.remove_task(category, task_index)
        self.show_auto_close_message("Успіх", "Завдання видалено")
        self.view_tasks()  # Оновлюємо таблицю

    def show_settings(self):
        """
        Відображає вікно налаштувань з прокруткою.
        """
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Налаштування")
        settings_window.geometry("400x400")  # Збільшимо розмір вікна

        # Створення контейнера для прокрутки
        container = tk.Frame(settings_window)
        container.pack(fill=tk.BOTH, expand=True)

        # Створення Canvas (полотно) для прокрутки
        canvas = tk.Canvas(container)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Додавання вертикальної прокрутки
        scrollbar = tk.Scrollbar(container, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Налаштування Canvas для роботи з прокруткою
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Створення Frame всередині Canvas для розміщення елементів
        inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # Вимикач для автоматичного вимкнення ПК
        self.auto_shutdown_var = tk.BooleanVar(value=self.config_manager.config["auto_shutdown"])
        auto_shutdown_check = tk.Checkbutton(
            inner_frame,
            text="Автоматичне вимкнення ПК",
            variable=self.auto_shutdown_var,
            command=self.update_auto_shutdown,
            font=FONT
        )
        auto_shutdown_check.pack(pady=10)

        # Поле для введення максимального ігрового часу
        tk.Label(inner_frame, text="Максимальний ігровий час (хв):", font=FONT).pack(pady=10)
        self.max_earned_time_entry = tk.Entry(inner_frame, font=FONT)
        self.max_earned_time_entry.insert(0, str(self.config_manager.config["max_earned_time"]))
        self.max_earned_time_entry.pack(pady=10)

        # Поле для введення параметра "Завдання видаляється після проходження раз:"
        tk.Label(inner_frame, text="Завдання видаляється після проходження раз:", font=FONT).pack(pady=10)
        self.remove_after_solved_entry = tk.Entry(inner_frame, font=FONT)
        self.remove_after_solved_entry.insert(0, str(self.config_manager.config["remove_after_solved"]))
        self.remove_after_solved_entry.pack(pady=10)

        # Додаємо кнопку для додавання до автозапуску
        tk.Button(
            inner_frame,
            text="Додати до автозапуску",
            command=self.add_to_startup,
            font=FONT
        ).pack(pady=10)

        # Додаємо кнопку для видалення з автозапуску
        tk.Button(
            inner_frame,
            text="Видалити з автозапуску",
            command=self.remove_from_startup,
            font=FONT
        ).pack(pady=10)

        # Кнопка для збереження налаштувань
        tk.Button(
            inner_frame,
            text="Зберегти",
            command=self.update_settings,
            font=FONT
        ).pack(pady=10)

        # Кнопка для закриття вікна
        tk.Button(
            inner_frame,
            text="Закрити",
            command=settings_window.destroy,
            font=FONT
        ).pack(pady=10)

        # Підтримка прокрутки колесом миші
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def update_auto_shutdown(self):
        """
        Оновлює налаштування автоматичного вимкнення ПК.
        """
        self.config_manager.set_auto_shutdown(self.auto_shutdown_var.get())
        self.show_auto_close_message("Успіх", "Налаштування збережено")

    def update_settings(self):
        """
        Оновлює всі налаштування.
        """
        try:
            max_earned_time = int(self.max_earned_time_entry.get())
            remove_after_solved = int(self.remove_after_solved_entry.get())
            if max_earned_time <= 0 or remove_after_solved < 0:
                raise ValueError
            self.config_manager.set_max_earned_time(max_earned_time)
            self.config_manager.set_remove_after_solved(remove_after_solved)
            self.config_manager.set_auto_shutdown(self.auto_shutdown_var.get())
            self.show_auto_close_message("Успіх", "Налаштування збережено")
        except ValueError:
            self.show_auto_close_message("Помилка", "Некоректні дані")

    
if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop() 

   