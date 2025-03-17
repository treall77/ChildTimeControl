import keyboard  # Для блокування клавіш

def block_keys():
    """Блокує комбінації клавіш, що дозволяють закрити або згорнути вікно."""
    keyboard.add_hotkey("alt+f4", lambda: None, suppress=True)
    keyboard.add_hotkey("alt+tab", lambda: None, suppress=True)
    keyboard.add_hotkey("win+tab", lambda: None, suppress=True)
 #   keyboard.add_hotkey("win+d", lambda: None, suppress=True)
 #   keyboard.add_hotkey("ctrl+esc", lambda: None, suppress=True)
 #   keyboard.add_hotkey("win+l", lambda: None, suppress=True)
 #   keyboard.add_hotkey("alt+esc", lambda: None, suppress=True)
 #   keyboard.add_hotkey("win+m", lambda: None, suppress=True)
 #   keyboard.add_hotkey("win+shift+m", lambda: None, suppress=True)

# Якщо запускаємо як окремий скрипт — працює у режимі тестування
if __name__ == "__main__":
    print("Блокування клавіш увімкнено. Натисніть Ctrl+C, щоб зупинити.")
    block_keys()
    while True:
        pass
