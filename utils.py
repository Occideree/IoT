import sys
import os


def resource_path(relative_path):
    """Получение абсолютного пути к ресурсу в упакованном приложении"""
    try:
        # Если мы запустили .exe файл
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS  # Местоположение временного каталога PyInstaller
        else:
            base_path = os.path.abspath(".")  # Местоположение текущего каталога для исходных файлов
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"Error getting resource path: {e}")
        return relative_path