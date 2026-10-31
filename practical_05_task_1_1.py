"""
ПР №5: Ініціалізація та конфігурація веб-проєктів з Django та Flask.
Завдання 1.1: Скрипт перевірки середовища розробки.
"""

import sys
import importlib
import importlib.metadata
import warnings

# Налаштовуємо UTF-8 кодування для консолі
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

warnings.filterwarnings("ignore", category=DeprecationWarning)

def check_python_version():
    """Перевіряє версію Python (потрібно >= 3.10)."""
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version < (3, 10):
        print("  [ПОПЕРЕДЖЕННЯ] Версія Python застаріла! Рекомендовано >= 3.10")
    else:
        print("  [OK] Версія Python відповідає вимогам (>= 3.10)")

def check_package(package_name: str) -> bool:
    """Перевіряє, чи встановлено пакет, і виводить його версію.
    Args:
        package_name: назва пакета для перевірки.
    Returns:
        True, якщо пакет встановлено.
    """
    try:
        module = importlib.import_module(package_name)
        try:
            version = importlib.metadata.version(package_name)
        except Exception:
            version = getattr(module, '__version__', 'невідома')
        print(f"  [OK] {package_name} ({version})")
        return True
    except ImportError:
        print(f"  [MISSING] {package_name}: НЕ ВСТАНОВЛЕНО :(")
        return False

def main():
    print("=" * 60)
    print("=== Завдання 1.1: Перевірка середовища розробки ===")
    print("=" * 60)
    print("\nВерсія інтерпретатора Python:")
    check_python_version()

    print("\nВстановлені пакети:")
    packages = ['django', 'flask']
    results = {pkg: check_package(pkg) for pkg in packages}

    installed_count = sum(1 for v in results.values() if v)
    missing_count = sum(1 for v in results.values() if not v)

    print("\n--- Підсумок перевірки ---")
    print(f"Встановлено пакетів: {installed_count}/{len(packages)}")
    print(f"Відсутніх пакетів:   {missing_count}/{len(packages)}")

    if missing_count > 0:
        missing_pkgs = [pkg for pkg, ok in results.items() if not ok]
        print(f"\nДля встановлення відсутніх пакетів виконайте:\npip install {' '.join(missing_pkgs)}")
    else:
        print("\nВсі необхідні веб-фреймворки успішно встановлені та готові до роботи!")
    print("=" * 60)

if __name__ == '__main__':
    main()
