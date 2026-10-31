"""
ПР №5: Ініціалізація та конфігурація веб-проєктів з Django та Flask.
Завдання 1.2: Генератор requirements.txt з перевіркою залежностей.
"""

import json
import os
import subprocess
import sys

# Налаштовуємо UTF-8 для виводу в консоль
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_installed_packages() -> list[dict]:
    """Повертає список встановлених пакетів з версіями.
    Returns:
        Список словників [{'name': ..., 'version': ...}].
    """
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'list', '--format=json'],
        capture_output=True, text=True, check=True
    )
    packages = json.loads(result.stdout)
    return packages

def generate_requirements(packages: list[dict], filename: str = 'requirements.txt'):
    """Записує пакети у файл requirements.txt.
    Args:
        packages: список словників з ключами 'name' та 'version'.
        filename: ім'я файлу для запису.
    """
    # Відфільтровуємо службові/системні пакети менеджера
    system_packages = {'pip', 'setuptools', 'wheel'}
    filtered_packages = [
        pkg for pkg in packages
        if pkg['name'].lower() not in system_packages
    ]

    with open(filename, 'w', encoding='utf-8') as f:
        for pkg in sorted(filtered_packages, key=lambda x: x['name'].lower()):
            f.write(f"{pkg['name']}=={pkg['version']}\n")

def verify_requirements(filename: str = 'requirements.txt') -> bool:
    """Перевіряє, чи всі пакети з requirements.txt встановлені.
    Args:
        filename: шлях до файлу requirements.txt.
    Returns:
        True, якщо всі залежності задоволені.
    """
    if not os.path.exists(filename):
        print(f"  [ПОМИЛКА] Файл '{filename}' не знайдено!")
        return False

    installed = {pkg['name'].lower(): pkg['version'] for pkg in get_installed_packages()}
    all_ok = True

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '==' in line:
                req_name, req_ver = line.split('==', 1)
                req_name_clean = req_name.strip()
                req_name_lower = req_name_clean.lower()
                req_ver = req_ver.strip()

                if req_name_lower not in installed:
                    print(f"  [MISSING] Пакет {req_name_clean} не встановлено!")
                    all_ok = False
                elif installed[req_name_lower] != req_ver:
                    print(f"  [DIFF] Пакет {req_name_clean}: очікується {req_ver}, встановлено {installed[req_name_lower]}")
                    all_ok = False
                else:
                    print(f"  [OK] {req_name_clean}=={req_ver}")
            else:
                # Пакет без суворої версії
                pkg_name = line.strip()
                if pkg_name.lower() not in installed:
                    print(f"  [MISSING] Пакет {pkg_name} не встановлено!")
                    all_ok = False
                else:
                    print(f"  [OK] {pkg_name} ({installed[pkg_name.lower()]})")

    return all_ok

def main():
    print("=" * 60)
    print("=== Завдання 1.2: Відтворення та перевірка requirements.txt ===")
    print("=" * 60)

    packages = get_installed_packages()
    print(f"Знайдено {len(packages)} встановлених пакетів у поточному середовищі:")
    for pkg in packages[:10]:
        print(f"  {pkg['name']}=={pkg['version']}")
    if len(packages) > 10:
        print(f"  ... та ще {len(packages) - 10} пакетів")

    generate_requirements(packages)
    print(f"\nФайл requirements.txt успішно створено/оновлено.")

    print("\nПеревірка відповідності встановлених пакетів вимогам:")
    ok = verify_requirements()
    print(f"\nРезультат перевірки залежностей: {'✓ Усе OK (середовище ідентичне)' if ok else '✗ Є розбіжності'}")
    print("=" * 60)

if __name__ == '__main__':
    main()
