import json
import os
from pathlib import Path


CONFIG_FILE = 'config.json'

class ConfigManager:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        """
        Завантажує конфігурацію з файлу. Якщо файл не існує або пошкоджений, повертає значення за замовчуванням.
        """
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
                    return json.load(file)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Помилка завантаження конфігурації: {e}")
        # Значення за замовчуванням
        print("Використовуються значення за замовчуванням.")
        return {
            "auto_shutdown": True,
            "max_earned_time": 60,
            "remove_after_solved": 0
        }

    def save_config(self):
        """
        Зберігає конфігурацію у файл.
        """
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
                json.dump(self.config, file, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Помилка збереження конфігурації: {e}")

    def set_auto_shutdown(self, value):
        self.config["auto_shutdown"] = value
        self.save_config()

    def set_max_earned_time(self, value):
        self.config["max_earned_time"] = value
        self.save_config()

    def set_remove_after_solved(self, value):
        self.config["remove_after_solved"] = value
        self.save_config()

    