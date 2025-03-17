import json
import os

TASKS_FILE = 'tasks.json'

class TaskManager:
    def __init__(self):
        self.tasks = self.load_tasks()

    def load_tasks(self):
        """
        Завантажує завдання з файлу. Якщо файл не існує, повертає порожній список.
        """
        try:
            if os.path.exists(TASKS_FILE):
                with open(TASKS_FILE, 'r', encoding='utf-8') as file:
                    tasks = json.load(file)
                    # Перевіряємо кожне завдання на наявність параметра times_solved
                    for task in tasks:
                        if "times_solved" not in task:
                            task["times_solved"] = 0  # Додаємо параметр зі значенням за замовчуванням
                    return tasks
        except (json.JSONDecodeError, IOError) as e:
            print(f"Помилка завантаження завдань: {e}")
        return []

    def save_tasks(self):
        """
        Зберігає завдання у файл.
        """
        try:
            with open(TASKS_FILE, 'w', encoding='utf-8') as file:
                json.dump(self.tasks, file, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Помилка збереження завдань: {e}")

    def add_task(self, question, answer, reward_minutes=1):
        """
        Додає нове завдання до списку.

        :param question: Питання завдання
        :param answer: Відповідь на завдання
        :param reward_minutes: Кількість хвилин нагороди (за замовчуванням 1)
        """
        self.tasks.append({
            'question': question,
            'answer': answer,
            'reward_minutes': reward_minutes,
            'times_solved': 0  # Новий параметр
        })
        self.save_tasks()

    def remove_task(self, index):
        """
        Видаляє завдання за індексом.

        :param index: Індекс завдання для видалення
        """
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            self.save_tasks()

    def load_tasks_from_json(self, file_path):
        """
        Завантажує завдання з JSON-файлу.

        :param file_path: Шлях до JSON-файлу
        :return: True, якщо завдання успішно завантажено, інакше False
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    new_tasks = json.load(file)
                    self.tasks.extend(new_tasks)
                    self.save_tasks()
                    return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Помилка завантаження завдань з файлу: {e}")
        return False

    def increment_times_solved(self, index):
        """
        Збільшує лічильник times_solved для завдання за індексом.

        :param index: Індекс завдання
        """
        if 0 <= index < len(self.tasks):
            self.tasks[index]["times_solved"] += 1
            self.save_tasks()