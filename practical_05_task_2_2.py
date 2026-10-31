"""
ПР №5: Ініціалізація та конфігурація веб-проєктів з Django та Flask.
Завдання 2.2: Аналізатор конфігурації Django-проєкту та перевірка безпеки.
"""

import ast
import os
import sys

# Налаштовуємо UTF-8 для виводу в консоль
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def parse_ast_value(node):
    """Рекурсивно витягує значення з AST-вузла."""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.List):
        return [parse_ast_value(elt) for elt in node.elts]
    elif isinstance(node, ast.Tuple):
        return tuple(parse_ast_value(elt) for elt in node.elts)
    elif isinstance(node, ast.Dict):
        return {parse_ast_value(k): parse_ast_value(v) for k, v in zip(node.keys, node.values)}
    return None

def analyze_settings(settings_path: str) -> dict:
    """Аналізує файл settings.py та повертає ключові параметри.
    Args:
        settings_path: шлях до файлу settings.py.
    Returns:
        Словник з аналізом конфігурації.
    """
    with open(settings_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=settings_path)

    config = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    if var_name in ['DEBUG', 'LANGUAGE_CODE', 'TIME_ZONE']:
                        if isinstance(node.value, ast.Constant):
                            config[var_name] = node.value.value
                    elif var_name == 'INSTALLED_APPS':
                        config['INSTALLED_APPS'] = [
                            elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)
                        ]
                    elif var_name == 'DATABASES':
                        # Визначаємо тип/рушій БД
                        db_engine = 'невідомо'
                        if isinstance(node.value, ast.Dict):
                            for k, v in zip(node.value.keys, node.value.values):
                                if isinstance(k, ast.Constant) and k.value == 'default':
                                    if isinstance(v, ast.Dict):
                                        for sub_k, sub_v in zip(v.keys, v.values):
                                            if isinstance(sub_k, ast.Constant) and sub_k.value == 'ENGINE':
                                                if isinstance(sub_v, ast.Constant):
                                                    db_engine = sub_v.value.split('.')[-1]
                        config['DATABASES'] = f"default ({db_engine})"

    return config

def check_security(settings_path: str) -> list[str]:
    """Перевіряє базову безпеку конфігурації.
    Args:
        settings_path: шлях до файлу settings.py.
    Returns:
        Список попереджень безпеки.
    """
    warnings = []
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
        tree = ast.parse(content, filename=settings_path)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # 1. Перевірка DEBUG
                    if target.id == 'DEBUG':
                        if isinstance(node.value, ast.Constant) and node.value.value is True:
                            warnings.append(
                                "КРИТИЧНО: DEBUG = True увімкнено! У production-середовищі це розкриває конфіденційні трейсбеки, змінні оточення та код."
                            )

                    # 2. Перевірка SECRET_KEY
                    elif target.id == 'SECRET_KEY':
                        # Якщо це константа-рядок, а не виклик os.environ.get
                        if isinstance(node.value, ast.Constant):
                            warnings.append(
                                "УВАГА: SECRET_KEY захардкоджений у вихідному коді! Рекомендовано завантажувати його з змінних оточення (os.environ)."
                            )
                        elif isinstance(node.value, ast.Call):
                            pass  # Завантажується через функцію/метод

                    # 3. Перевірка ALLOWED_HOSTS
                    elif target.id == 'ALLOWED_HOSTS':
                        if isinstance(node.value, (ast.List, ast.Tuple)):
                            if len(node.value.elts) == 0:
                                warnings.append(
                                    "ПОПЕРЕДЖЕННЯ: ALLOWED_HOSTS порожній! Для production необхідно явно вказати дозволені доменні імена та IP."
                                )

    return warnings

def main():
    settings_path = os.path.join('mysite', 'mysite', 'settings.py')
    if not os.path.exists(settings_path):
        # Перевірка з поточної папки або підкаталогу
        alt_path = os.path.join('mysite', 'settings.py')
        if os.path.exists(alt_path):
            settings_path = alt_path
        else:
            print(f"Файл {settings_path} не знайдено!")
            sys.exit(1)

    print("=" * 60)
    print("=== Завдання 2.2: Аналіз конфігурації Django та аудит безпеки ===")
    print("=" * 60)

    config = analyze_settings(settings_path)
    print("\n=== Аналіз конфігурації Django (settings.py) ===")
    for key, value in config.items():
        if isinstance(value, list):
            print(f"  {key}:")
            for item in value:
                print(f"    - {item}")
        else:
            print(f"  {key}: {value}")

    print("\n=== Перевірка безпеки конфігурації ===")
    warnings = check_security(settings_path)
    if warnings:
        for idx, w in enumerate(warnings, 1):
            print(f"  ! [{idx}] {w}")
    else:
        print("  ✓ Попереджень не знайдено, базова безпека дотримана.")
    print("=" * 60)

if __name__ == '__main__':
    main()
