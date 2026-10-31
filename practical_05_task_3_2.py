"""
ПР №5: Ініціалізація та конфігурація веб-проєктів з Django та Flask.
Завдання 3.2: Порівняльний аналіз структури Django та Flask проєктів.
"""

import os
import sys

# Налаштовуємо UTF-8 для виводу в консоль
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

IGNORE_DIRS = {'__pycache__', 'venv', 'venv2', '.git', '.idea', '.vscode'}
IGNORE_FILES = {'db.sqlite3', '.DS_Store'}
IGNORE_EXTENSIONS = {'.pyc', '.pyo'}

def should_ignore(name: str, is_dir: bool = False) -> bool:
    """Визначає, чи слід ігнорувати службовий файл/каталог."""
    if is_dir and name in IGNORE_DIRS:
        return True
    if not is_dir:
        if name in IGNORE_FILES:
            return True
        _, ext = os.path.splitext(name)
        if ext in IGNORE_EXTENSIONS:
            return True
    return False

def scan_directory(path: str, prefix: str = '') -> list[str]:
    """Рекурсивно сканує каталог та повертає дерево файлів.
    Args:
        path: шлях до каталогу.
        prefix: відступ для форматування дерева.
    Returns:
        Список рядків зі структурою каталогу.
    """
    tree = []
    try:
        entries = sorted(os.listdir(path))
    except OSError:
        return tree

    # Фільтруємо елементи
    valid_entries = []
    for entry in entries:
        full_p = os.path.join(path, entry)
        is_d = os.path.isdir(full_p)
        if not should_ignore(entry, is_d):
            valid_entries.append(entry)

    total = len(valid_entries)
    for idx, entry in enumerate(valid_entries):
        is_last = (idx == total - 1)
        connector = "└── " if is_last else "├── "
        full_path = os.path.join(path, entry)

        if os.path.isdir(full_path):
            tree.append(f"{prefix}{connector}{entry}/")
            new_prefix = prefix + ("    " if is_last else "│   ")
            subtree = scan_directory(full_path, new_prefix)
            tree.extend(subtree)
        else:
            size_kb = os.path.getsize(full_path) / 1024
            tree.append(f"{prefix}{connector}{entry} ({size_kb:.1f} KB)")

    return tree

def analyze_project(path: str) -> dict:
    """Аналізує проєкт та збирає статистику.
    Args:
        path: кореневий каталог проєкту.
    Returns:
        Словник зі статистикою: кількість файлів .py, .html, .css, загальний розмір, список каталогів.
    """
    stats = {
        'py_files': 0,
        'html_files': 0,
        'css_files': 0,
        'total_size': 0,
        'directories': [],
    }

    for root, dirs, files in os.walk(path):
        # Модифікуємо dirs in-place для пропуску ігнорованих папок
        dirs[:] = [d for d in dirs if not should_ignore(d, is_dir=True)]

        rel_root = os.path.relpath(root, path)
        if rel_root != '.':
            stats['directories'].append(rel_root)

        for f in files:
            if should_ignore(f, is_dir=False):
                continue
            full_path = os.path.join(root, f)
            size = os.path.getsize(full_path)
            stats['total_size'] += size

            _, ext = os.path.splitext(f)
            ext = ext.lower()
            if ext == '.py':
                stats['py_files'] += 1
            elif ext == '.html':
                stats['html_files'] += 1
            elif ext == '.css':
                stats['css_files'] += 1

    return stats

def compare_projects(django_path: str, flask_path: str):
    """Порівнює два проекти та виводить таблицю відмінностей.
    Args:
        django_path: шлях до Django-проекту.
        flask_path: шлях до Flask-проекту.
    """
    print("=" * 70)
    print("=== Завдання 3.2: Порівняльний аналіз структури Django та Flask проєктів ===")
    print("=" * 70)

    # 1. Дерево структури Django
    print(f"\n[1] Деревоподібна структура Django-проєкту ({django_path}/):")
    django_tree = scan_directory(django_path)
    for line in django_tree:
        print(line)
    django_stats = analyze_project(django_path)

    # 2. Дерево структури Flask
    print(f"\n[2] Деревоподібна структура Flask-проєкту ({flask_path}/):")
    flask_tree = scan_directory(flask_path)
    for line in flask_tree:
        print(line)
    flask_stats = analyze_project(flask_path)

    # 3. Порівняльна підсумкова таблиця
    print("\n" + "=" * 70)
    print("ПОРІВНЯЛЬНА ТАБЛИЦЯ МЕТРИК СТРУКТУРИ")
    print("=" * 70)
    header = f"| {'Характеристика':<28} | {'Django (mysite)':<18} | {'Flask (myflaskapp)':<18} |"
    divider = f"|{'-' * 30}|{'-' * 20}|{'-' * 20}|"
    print(header)
    print(divider)

    rows = [
        ("Вихідні файли Python (.py)", django_stats['py_files'], flask_stats['py_files']),
        ("Шаблони розмітки (.html)", django_stats['html_files'], flask_stats['html_files']),
        ("Таблиці стилів (.css)", django_stats['css_files'], flask_stats['css_files']),
        ("Кількість підкаталогів", len(django_stats['directories']), len(flask_stats['directories'])),
        ("Сумарний розмір коду (байт)", f"{django_stats['total_size']} B", f"{flask_stats['total_size']} B"),
    ]

    for label, d_val, f_val in rows:
        print(f"| {label:<28} | {str(d_val):<18} | {str(f_val):<18} |")
    print(divider)

    print("\n[Висновки щодо архітектури]:")
    print("1. Django створює структурований 'batteries-included' каркас з багатьма модулями (settings, urls, wsgi, asgi, apps).")
    print("2. Flask використовує мінімалістичний підхід (Microframework): уся структура створюється розробником під власні потреби.")
    print("=" * 70)

def main():
    django_path = 'mysite'
    flask_path = 'myflaskapp'

    for path in [django_path, flask_path]:
        if not os.path.exists(path):
            print(f"Каталог '{path}' не знайдено. Спершу виконайте попередні завдання.")
            return

    compare_projects(django_path, flask_path)

if __name__ == '__main__':
    main()
