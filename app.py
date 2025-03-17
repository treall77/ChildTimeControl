import json
import os
# import time
import tkinter as tk
from tkinter import messagebox
import threading
from PIL import Image, ImageTk
import random
import keyboard_blocker  # Імпортуємо модуль keyboard_blocker
 
# Константи для імен файлів
MATH_TASKS_FILE = 'math_tasks.json'
ENGLISH_TASKS_FILE = 'english_tasks.json'
CONFIG_FILE = 'config.json'

class TaskManager:
    def __init__(self):
        # Ініціалізація списку завдань, типу завдань та індексів
        self.tasks = []
        self.current_task_type = None
        self.current_task_index = 0
        self.used_tasks = []

    def get_random_task(self):
        """
        Повертає випадкове завдання зі списку.
        """
        if self.tasks:
            return random.choice(self.tasks)
        return None

    def get_random_task_index(self):
        """
        Повертає випадковий індекс завдання зі списку.
        """
        if self.tasks:
            return random.randint(0, len(self.tasks) - 1)
        return -1  # Повертаємо -1, якщо завдань немає

    def check_answer(self, index, user_answer):
        """
        Перевіряє відповідь користувача та оновлює times_solved.
        """
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            if task["answer"].lower() == user_answer.lower():
                if "times_solved" not in task:
                    task["times_solved"] = 1
                else:
                    task["times_solved"] += 1
                self.save_tasks()  # Зберігаємо зміни
                return True
        return False

    def save_tasks(self):
        """
        Зберігає завдання у відповідний файл залежно від типу завдань.
        """
        if self.current_task_type == "math":
            file_path = MATH_TASKS_FILE
        elif self.current_task_type == "english":
            file_path = ENGLISH_TASKS_FILE
        else:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.tasks, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[ERROR] Помилка збереження завдань: {e}")

    def load_tasks(self, task_type):
        """
        Завантажує завдання з файлу залежно від типу завдань.
        """
        self.current_task_type = task_type
        self.tasks = []
        self.current_task_index = 0
        self.used_tasks = []

        if task_type == "math":
            file_path = MATH_TASKS_FILE
        elif task_type == "english":
            file_path = ENGLISH_TASKS_FILE
        elif task_type == "mix":
            math_tasks = self._load_tasks_from_file(MATH_TASKS_FILE)
            english_tasks = self._load_tasks_from_file(ENGLISH_TASKS_FILE)
            self.tasks = self._mix_tasks(math_tasks, english_tasks)
            return

        self.tasks = self._load_tasks_from_file(file_path)

    def _load_tasks_from_file(self, file_path):
        """
        Завантажує завдання з файлу.
        """
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return []

    def _mix_tasks(self, math_tasks, english_tasks):
        """
        Змішує математичні та англійські завдання.
        """
        mixed_tasks = math_tasks + english_tasks
        random.shuffle(mixed_tasks)
        return mixed_tasks

    def get_current_task(self):
        """
        Повертає поточне завдання, яке ще не було використане.
        """
        if len(self.used_tasks) < len(self.tasks):
            while True:
                random_index = self.get_random_task_index()
                if random_index not in self.used_tasks:
                    return self.tasks[random_index]
        return None

    def move_to_next_task(self):
        """
        Переходить до наступного завдання, оновлюючи список використаних завдань.
        """
        if self.current_task_index not in self.used_tasks:
            self.used_tasks.append(self.current_task_index)

        if len(self.used_tasks) >= len(self.tasks):
            self.used_tasks = []

        while True:
            self.current_task_index = (self.current_task_index + 1) % len(self.tasks)
            if self.current_task_index not in self.used_tasks:
                break

class ConfigManager:
    def __init__(self):
        """
        Ініціалізує конфігурацію, завантажуючи її з файлу.
        """
        self.config = self.load_config()

    def load_config(self):
        """
        Завантажує конфігурацію з файлу.
        """
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
                config = json.load(file)
                config.pop("max_skips", None)  # Видаляємо поле max_skips
                return config
        return {"auto_shutdown": True, "max_earned_time": 30}

class UserApp:
    def __init__(self, root):
        """
        Ініціалізує головний інтерфейс користувача.
        """
        
        self.root = root
        self.root.title("Child Time Control - Користувач")
        self.root.geometry("800x600")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)

        # Блокуємо клавіші при запуску
        keyboard_blocker.block_keys()

        self.task_manager = TaskManager()
        self.config_manager = ConfigManager()
        self.earned_time = 3
        self.timer_thread = None

        # Ініціалізація індексу рандомного завдання
        self.current_random_index = -1

        # Завантаження зображень
        try:
            self.checkmark_image = ImageTk.PhotoImage(Image.open("./checkmark.png").resize((30, 30)))
            self.cross_image = ImageTk.PhotoImage(Image.open("./cross.png").resize((30, 30)))
        except FileNotFoundError:
            print("Помилка: файли зображень не знайдено!")
            self.checkmark_image = None
            self.cross_image = None

        self.cross_label = None
        self.checkmark_label = None

        self.show_login_screen()


    def track_window_state(self):
        """
        Відслідковує стан вікна та запускає start_play_time, якщо:
        - Вікно згорнуте
        - Вікно закрите
        - Користувач переключився на інше вікно (Alt + Tab)
        """
        if not self.root.winfo_exists():
            # Якщо вікно було закрите
            start_play_time(self)
            return

        # Відслідковуємо, якщо вікно не є активним або згорнуте
        if not self.root.focus_displayof() or self.root.state() == "iconic":
            start_play_time(self)
            return

        # Перевіряємо стан вікна кожні 500 мс
        self.root.after(500, lambda: track_window_state(self))

    # Виклик функції відслідковування під час запуску додатка
    def run_app(self):
        self.root.protocol("WM_DELETE_WINDOW", lambda: start_play_time(self))  # Закриття вікна
        track_window_state(self)  # Старт відслідковування стану вікна
        self.root.mainloop()

    def show_checkmark(self):
        """Показує галочку."""
        if self.checkmark_image and not self.checkmark_label:
            self.checkmark_label = tk.Label(self.root, image=self.checkmark_image)
        if self.checkmark_label:
            self.checkmark_label.place(x=self.answer_entry.winfo_x() + self.answer_entry.winfo_width() + 10,
                                      y=self.answer_entry.winfo_y())
            self.root.after(1000, self.checkmark_label.place_forget)

    def show_cross(self):
        """Показує хрестик."""
        if self.cross_image and not self.cross_label:
            self.cross_label = tk.Label(self.root, image=self.cross_image)
        if self.cross_label:
            self.cross_label.place(x=self.answer_entry.winfo_x() + self.answer_entry.winfo_width() + 10,
                                  y=self.answer_entry.winfo_y())
            self.root.after(1000, self.cross_label.place_forget)

    def show_auto_close_message(self, title, message, delay=3000):
        """Показує повідомлення, яке закривається автоматично."""
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("300x100")
        popup.attributes("-topmost", True)

        label = tk.Label(popup, text=message, font=("Arial", 14))
        label.pack(pady=20)

        popup.after(delay, popup.destroy)

    def show_login_screen(self):
        """Показує екран входу в систему."""
        self.clear_screen()

        tk.Label(self.root, text="Вхід у систему", font=("Arial", 16)).pack()

        tk.Label(self.root, text="Ім'я:", font=("Arial", 14)).pack()
        self.username_entry = tk.Entry(self.root, font=("Arial", 14))
        self.username_entry.pack()

        tk.Button(self.root, text="Математика", command=lambda: self.start_tasks("math"), font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Англійська", command=lambda: self.start_tasks("english"), font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Мікс", command=lambda: self.start_tasks("mix"), font=("Arial", 14)).pack(pady=10)

    def start_tasks(self, task_type):
        """
        Починає виконання завдань вказаного типу.
        """
        username = self.username_entry.get()
        if username:
            self.current_user = username
            self.task_manager.load_tasks(task_type)
            self.show_user_interface()
        else:
            self.show_auto_close_message("Помилка", "Введіть ім'я")

    def show_user_interface(self):
        """Показує головний інтерфейс користувача."""
        self.clear_screen()

        tk.Label(self.root, text="Головний інтерфейс", font=("Arial", 16)).pack()

        # Віджет для відображення завдання з переносом тексту
        self.task_label = tk.Label(self.root, text="", font=("Arial", 20), wraplength=700)
        self.task_label.pack()

        self.answer_entry = tk.Entry(self.root, font=("Arial", 20))
        self.answer_entry.pack()

        tk.Button(self.root, text="Перевірити", command=self.check_answer, font=("Arial", 14)).pack()
        self.skip_button = tk.Button(self.root, text="Пропуск", command=self.skip_task, font=("Arial", 14))
        self.skip_button.pack()

        self.time_label = tk.Label(self.root, text=f"Зароблено часу: {self.earned_time} хв", font=("Arial", 16))
        self.time_label.pack()

        tk.Button(self.root, text="Грати", command=self.start_play_time, font=("Arial", 14)).pack()

        self.root.bind("<Return>", lambda event: self.check_answer())
        self.show_next_task()

    def skip_task(self):
        """
        Пропускає поточне завдання та зменшує зароблений час.
        """
        if self.earned_time > 0:
            self.earned_time -= 1
            self.time_label.config(text=f"Зароблено часу: {self.earned_time} хв")

        self.task_manager.move_to_next_task()
        self.show_next_task()

    def show_next_task(self):
        """
        Показує наступне завдання. Якщо times_solved більше ніж remove_after_solved, завдання видаляється.
        """
        if len(self.task_manager.used_tasks) >= len(self.task_manager.tasks):
            self.task_manager.used_tasks = []
            messagebox.showinfo("Повідомлення", "Усі завдання виконано! Починаємо спочатку.")

        while True:
            random_index = self.task_manager.get_random_task_index()
            if random_index == -1:
                self.task_label.config(text="Немає завдань для виконання.")
                self.answer_entry.config(state='disabled')
                self.skip_button.config(state='disabled')
                return

            task = self.task_manager.tasks[random_index]

            # Перевіряємо, чи завдання має times_solved і чи воно перевищує remove_after_solved
            if "times_solved" in task and "remove_after_solved" in self.config_manager.config:
                if task["times_solved"] >= self.config_manager.config["remove_after_solved"]:
                    # Видаляємо завдання, якщо воно вирішено занадто багато разів
                    self.task_manager.tasks.pop(random_index)
                    self.task_manager.save_tasks()  # Зберігаємо зміни
                    continue  # Переходимо до наступного завдання

            # Якщо завдання підходить, показуємо його
            self.current_random_index = random_index
            self.task_label.config(text=task['question'])
            break

    def check_answer(self):
        """
        Перевіряє відповідь користувача та оновлює інтерфейс.
        """
        if self.current_random_index != -1:
            user_answer = self.answer_entry.get()
            if self.task_manager.check_answer(self.current_random_index, user_answer):
                self.answer_entry.delete(0, tk.END)
                reward = self.task_manager.tasks[self.current_random_index]['reward_minutes']
                if self.earned_time + reward <= self.config_manager.config["max_earned_time"]:
                    self.earned_time += reward
                    self.time_label.config(text=f"Зароблено часу: {self.earned_time} хв")
                self.task_manager.move_to_next_task()
                self.show_next_task()
                self.show_checkmark()
            else:
                self.show_auto_close_message("Помилка", "Невірна відповідь")
                self.show_cross()



    def start_play_time(self):
        """
        Починає час гри, запускаючи таймер.
        """
        import sys
        if self.earned_time > 0 and not (self.timer_thread and self.timer_thread.is_alive()):
            self.timer_thread = threading.Thread(target=self.run_timer)
            self.timer_thread.start()
            self.root.destroy()  # Закриває головне вікно після запуску таймера
            sys.exit()  # Завершує роботу додатка після закриття вікна

    def run_timer(self):
        """Запускає таймер для автоматичного вимкнення системи."""
        if self.config_manager.config.get("auto_shutdown", False) and self.earned_time > 0:
            os.system(f"shutdown /s /t {self.earned_time * 60}")
                                                            

    def clear_screen(self):
        """
        Очищає екран, видаляючи всі віджети.
        """
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.unbind_all("<Return>")

if __name__ == "__main__":
    root = tk.Tk()
    app = UserApp(root)
    root.mainloop()