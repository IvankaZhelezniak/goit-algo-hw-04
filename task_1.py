#!/usr/bin/env python3
"""
Програма, яка рекурсивно копіює всі файли із вихідної директорії у директорію призначення,
з розкладанням за піддиректоріями, назви яких базуються на розширенні файлів.

Використання:
    python task.py <SRC_DIR> [DST_DIR]

    - SRC_DIR — шлях до вихідної теки (обов'язково)
    - DST_DIR — шлях до теки призначення (необов'язково; за замовчуванням 'dist')

Приклад:
    python task_1.py ./input ./dist
    python task_1.py "C:/Users/Ivanna/Downloads"          # покладе у ./dist
"""

from __future__ import annotations

import argparse
import shutil
from itertools import count
from pathlib import Path
from typing import Iterable


def parse_args() -> argparse.Namespace:
    """Парсинг аргументів командного рядка."""
    p = argparse.ArgumentParser(
        description="Рекурсивно копіює файли та сортує їх у підтеки за розширеннями."
    )
    p.add_argument("src", type=Path, help="Шлях до вихідної директорії")
    p.add_argument(
        "dst",
        nargs="?",
        default=Path("dist"),
        type=Path,
        help="Шлях до директорії призначення (за замовчуванням: ./dist)",
    )
    return p.parse_args()


def is_subpath(child: Path, parent: Path) -> bool:
    """Перевіряє, чи знаходиться child усередині parent (для захисту від зациклення)."""
    try:
        return child.resolve().is_relative_to(parent.resolve())
    except AttributeError:
        
        child_resolved = child.resolve()
        parent_resolved = parent.resolve()
        return parent_resolved in child_resolved.parents


def ext_folder_for(file_path: Path) -> str:
    """
    Повертає ім'я підтеки за розширенням.
    - без розширення → '_no_ext'
    - багатоскладові типи (.tar.gz) залишає як 'tar.gz'
    - у нижньому регістрі
    """
    if not file_path.suffixes:
        return "_no_ext"
    # Об’єднує всі суфікси, окрім крапки попереду
    combo = "".join(file_path.suffixes).lstrip(".").lower()
    return combo


def uniquify(dst_file: Path) -> Path:
    """
    Якщо файл з таким ім’ям уже існує в директорії призначення,
    додає суфікс ' (1)', ' (2)', ... до імені (зберігаючи розширення).
    """
    if not dst_file.exists():
        return dst_file
    stem, suffix = dst_file.stem, dst_file.suffix
    for i in count(1):
        candidate = dst_file.with_name(f"{stem} ({i}){suffix}")
        if not candidate.exists():
            return candidate


def safe_copy(src_file: Path, dst_root: Path) -> None:
    """
    Копіює один файл у відповідну піддиректорію всередині dst_root.
    Обробляє колізії імен та типові винятки.
    """
    try:
        subdir = ext_folder_for(src_file)
        target_dir = dst_root / subdir
        target_dir.mkdir(parents=True, exist_ok=True)

        target_path = uniquify(target_dir / src_file.name)
        shutil.copy2(src_file, target_path)  # copy2 зберігає час/права, якщо можливо
        print(f"✔ {src_file}  →  {target_path}")
    except (PermissionError, OSError) as e:
        # Не валимо весь процес через один проблемний файл
        print(f"⚠ Не вдалося скопіювати '{src_file}': {e}")


def walk_and_copy(current: Path, dst_root: Path, skip: Iterable[Path]) -> None:
    """
    Рекурсивний обхід директорій.
    БАЗОВИЙ ВИПАДОК: немає піддиректорій (або current — файл) → нічого не викликає далі.
    РЕКУРСИВНИЙ ВИПАДОК: для кожної піддиректорії викликає walk_and_copy().

    Свідомо копіює лише файли; структуру тек призначення формує за розширеннями.
    """
    try:
        # Перебір елементів у поточній директорії
        for entry in current.iterdir():
            # Пропускає цільову директорію (і її вміст), якщо вона лежить всередині джерела
            if any(is_subpath(entry, s) or entry.resolve() == s.resolve() for s in skip):
                continue

            # Якщо директорія — заходить рекурсивно
            if entry.is_dir() and not entry.is_symlink():
                walk_and_copy(entry, dst_root, skip)
            # Якщо файл — копіює
            elif entry.is_file():
                safe_copy(entry, dst_root)
            # Інше (посилання/спецфайли) — пропускає
            else:
                print(f"⤷ Пропуск '{entry}' (не файл і не звичайна директорія)")
    except PermissionError as e:
        print(f"⚠ Немає доступу до '{current}': {e}")
    except FileNotFoundError as e:
        # На випадок, якщо під час обходу щось було видалено/переміщено
        print(f"⚠ Елемент зник під час обходу '{current}': {e}")


def main() -> None:
    args = parse_args()
    src: Path = args.src
    dst: Path = args.dst

    try:
        src = src.resolve(strict=True)
        if not src.is_dir():
            raise NotADirectoryError(f"'{src}' не є директорією")
    except FileNotFoundError:
        print(f"✖ Вихідна директорія не існує: {args.src}")
        return
    except NotADirectoryError as e:
        print(f"✖ {e}")
        return

    # Створює директорію призначення
    try:
        dst = dst.resolve()
        dst.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"✖ Не вдалося підготувати директорію призначення '{dst}': {e}")
        return

    # Якщо DST всередині SRC — не заходить в DST під час обходу, щоб не зациклитися
    skip_dirs = [dst]

    print(f"Починаю копіювання з: {src}")
    print(f"Кладу у:            {dst}\n")

    walk_and_copy(src, dst, skip_dirs)

    print("\nГотово ✅")


if __name__ == "__main__":
    main()
