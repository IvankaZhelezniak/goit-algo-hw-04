# file: task_3.py
"""
Порівняння сортувань: Insertion vs Merge vs Timsort (built-in).
Вимірювання часу виконання через timeit на різних шаблонах даних і розмірах.

Запуск:
    python task_3.py
    python task_3.py --plots        # + графіки (потрібен matplotlib)
    python task_3.py --no-readme    # без генерації README

Вивід (каталог reports/):
    - sort_bench_results.csv
    - sort_growth_factors.csv
    - sort_bench_<pattern>.png  (якщо --plots)
    - README.md           (аналіз і висновки для дз)
"""

from __future__ import annotations

import argparse
import random
import timeit
from pathlib import Path
from typing import Callable, Dict, List


# Алгоритми сортування

def insertion_sort(lst: List[int]) -> List[int]:
    a = lst[:]
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and key < a[j]:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a

def _merge(left: List[int], right: List[int]) -> List[int]:
    res: List[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            res.append(left[i]); i += 1
        else:
            res.append(right[j]); j += 1
    if i < len(left): res.extend(left[i:])
    if j < len(right): res.extend(right[j:])
    return res

def merge_sort(arr: List[int]) -> List[int]:
    a = arr[:]
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    return _merge(merge_sort(a[:mid]), merge_sort(a[mid:]))

def timsort(arr: List[int]) -> List[int]:
    return sorted(arr)  # вбудований Timsort

ALGORITHMS: Dict[str, Callable[[List[int]], List[int]]] = {
    "Insertion": insertion_sort,
    "Merge": merge_sort,
    "Timsort (built-in)": timsort,
}


# Генерація даних

def make_dataset(n: int, pattern: str, seed: int = 42) -> List[int]:
    rnd = random.Random(seed)
    if pattern == "random":
        return [rnd.randint(0, 1_000_000) for _ in range(n)]
    if pattern == "sorted":
        return list(range(n))
    if pattern == "reversed":
        return list(range(n, 0, -1))
    if pattern == "nearly_sorted":
        a = list(range(n))
        swaps = max(1, n // 100)  # ~1% випадкових перестановок
        for _ in range(swaps):
            i, j = rnd.randrange(n), rnd.randrange(n)
            a[i], a[j] = a[j], a[i]
        return a
    raise ValueError("Unknown pattern")


#  Бенчмарк часу

def time_algorithm(func: Callable[[List[int]], List[int]], data: List[int], repeats: int = 3) -> float:
    def stmt():
        func(data[:])  # кожен запуск на копії
    timer = timeit.Timer(stmt)
    times = timer.repeat(repeat=repeats, number=1)
    return min(times)

def run_benchmarks(sizes, large_sizes, patterns, repeats: int) -> List[dict]:
    rows: List[dict] = []
    for pattern in patterns:
        # невеликі розміри — для всіх (включно з Insertion)
        for n in sizes:
            data = make_dataset(n, pattern, seed=123)
            for name, func in ALGORITHMS.items():
                t = time_algorithm(func, data, repeats=repeats)
                rows.append({"pattern": pattern, "n": n, "algorithm": name, "time_sec": t})
        # великі — тільки Merge і Timsort
        for n in large_sizes:
            data = make_dataset(n, pattern, seed=777)
            for name, func in ALGORITHMS.items():
                if name == "Insertion":
                    continue
                t = time_algorithm(func, data, repeats=repeats)
                rows.append({"pattern": pattern, "n": n, "algorithm": name, "time_sec": t})
    return rows


# Збереження/графіки/README

def ensure_reports_dir() -> Path:
    out = Path("reports")
    out.mkdir(parents=True, exist_ok=True)
    return out

def save_csv(rows: List[dict], outdir: Path) -> Path:
    import csv
    path = outdir / "sort_bench_results.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pattern", "n", "algorithm", "time_sec"])
        writer.writeheader()
        writer.writerows(rows)
    return path

def compute_growth(rows: List[dict]) -> List[dict]:
    sizes = [1000, 2000, 5000]
    patterns = ["random", "reversed", "nearly_sorted"]
    result: List[dict] = []
    for pattern in patterns:
        for algo in ["Insertion", "Merge", "Timsort (built-in)"]:
            ts = []
            for n in sizes:
                vals = [r["time_sec"] for r in rows
                        if r["pattern"] == pattern and r["n"] == n and r["algorithm"] == algo]
                if not vals: ts.append(float("nan"))
                else:        ts.append(min(vals))
            g1 = ts[1] / ts[0]
            g2 = ts[2] / ts[1]
            result += [
                {"pattern": pattern, "algorithm": algo, "pair": "1k→2k", "growth": g1},
                {"pattern": pattern, "algorithm": algo, "pair": "2k→5k", "growth": g2},
            ]
    return result

def save_growth_csv(growth: List[dict], outdir: Path) -> Path:
    import csv
    path = outdir / "sort_growth_factors.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pattern", "algorithm", "pair", "growth"])
        writer.writeheader()
        writer.writerows(growth)
    return path

def try_make_plots(rows: List[dict], outdir: Path):
    try:
        import matplotlib.pyplot as plt  # опційно
    except Exception:
        print("⚠ matplotlib не знайдено — графіки пропущено.")
        return []
    paths = []
    patterns = sorted({r["pattern"] for r in rows})
    for pattern in patterns:
        data = [r for r in rows if r["pattern"] == pattern]
        ns = sorted({r["n"] for r in data})
        algos = sorted({r["algorithm"] for r in data})
        plt.figure()
        for algo in algos:
            y = []
            for n in ns:
                vals = [r["time_sec"] for r in data if r["n"] == n and r["algorithm"] == algo]
                y.append(min(vals) if vals else float("nan"))
            plt.plot(ns, y, marker="o", label=algo)
        plt.xlabel("n (розмір масиву)")
        plt.ylabel("час (сек)")
        plt.title(f"Час сортування vs n — {pattern}")
        plt.legend()
        p = outdir / f"sort_bench_{pattern}.png"
        plt.savefig(p, bbox_inches="tight")
        plt.close()
        paths.append(p)
    return paths

from pathlib import Path  # переконайся, що імпорт є вище

def write_readme(rows: List[dict], growth: List[dict], plot_paths, outdir: Path) -> Path:
    # ---- зведення для random 1k..5k ----
    algos = ["Insertion", "Merge", "Timsort (built-in)"]
    ns = [1000, 2000, 5000]

    def cell(n: int, a: str) -> str:
        vals = [r["time_sec"] for r in rows
                if r["pattern"] == "random" and r["n"] == n and r["algorithm"] == a]
        return f"{min(vals):.4f}" if vals else "-"

    table = "| n | " + " | ".join(algos) + " |\n"
    table += "|" + "|".join(["---"] * (len(algos) + 1)) + "|\n"
    for n in ns:
        table += f"| {n} | " + " | ".join(cell(n, a) for a in algos) + " |\n"

    # таблиця коефіцієнтів зростання (емпірична перевірка)
    pats = ["random", "reversed", "nearly_sorted"]
    pairs = ["1k→2k", "2k→5k"]

    header = "| pattern | algorithm | " + " | ".join(pairs) + " |\n"
    header += "|" + "|".join(["---"] * (2 + len(pairs))) + "|\n"
    lines = [header]

    for p in pats:
        for a in algos:
            row = [g for g in growth if g["pattern"] == p and g["algorithm"] == a]
            if row:
                d = {r["pair"]: r["growth"] for r in row}
                values = " | ".join(f"{d.get(pair, float('nan')):.2f}" for pair in pairs)
                lines.append(f"| {p} | {a} | {values} |\n")
            else:
                lines.append(f"| {p} | {a} | " + " | ".join("-" for _ in pairs) + " |\n")
    growth_table = "".join(lines)

    #  текст README 
    text = []
    text.append("# Порівняння сортувань: Merge vs Insertion vs Timsort\n\n")
    text.append("Алгоритми: **Insertion sort** (вставками), **Merge sort** (злиттям), **Timsort** (`sorted`).\n")
    text.append("Шаблони: `random`, `sorted`, `reversed`, `nearly_sorted` (~1% перестановок).\n")
    text.append("Розміри: 1k, 2k, 5k (всі) + 10k, 20k, 50k (лише Merge і Timsort).\n\n")
    text.append("## Результати (секунди) для `random` (1k..5k)\n")
    text.append(table + "\n")
    if plot_paths:
        text.append("## Графіки\n")
        for p in plot_paths:
            text.append(f"- {p.name}\n")
        text.append("\n")
    text.append("## Емпірична перевірка складності\n")
    text.append("Очікування: O(n) ≈ ×2 і ×2.5; O(n log n) ≈ ×2.1 і ×2.32; O(n²) ≈ ×4 і ×6.25.\n\n")
    text.append(growth_table + "\n")
    text.append("## Висновки\n")
    text.append("1. **Timsort** стабільно найшвидший і майже лінійний на `sorted`/`nearly_sorted` завдяки виявленню пробіжок + вставкам на малих підмасивах.\n")
    text.append("2. **Merge sort** дає очікуване O(n log n) і добре масштабується, але повільніший за Timsort через відсутність адаптивності.\n")
    text.append("3. **Insertion sort** має квадратичне зростання на випадкових/зворотних наборах; придатний лише для малих або майже впорядкованих масивів.\n")
    text.append("\nПрактичний висновок: для реальних задач використовуйте вбудований `sorted`/`list.sort` (Timsort).\n")

    # 👉 пише прямо в кореневий README.md
    path = Path("README.md")
    path.write_text("".join(text), encoding="utf-8")
    return path


# CLI парсинг

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Benchmarks: Insertion vs Merge vs Timsort.")
    p.add_argument("--sizes", nargs="+", type=int, default=[1000, 2000, 5000],
                   help="розміри для всіх трьох алгоритмів")
    p.add_argument("--large-sizes", nargs="+", type=int, default=[10000, 20000, 50000],
                   help="розміри лише для Merge і Timsort")
    p.add_argument("--patterns", nargs="+",
                   default=["random", "sorted", "reversed", "nearly_sorted"],
                   help="шаблони даних")
    p.add_argument("--repeats", type=int, default=3, help="повторів timeit (беремо мінімум)")
    p.add_argument("--plots", action="store_true", help="згенерувати графіки (потрібен matplotlib)")
    p.add_argument("--no-readme", action="store_true", help="не створювати README_task3.md")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    outdir = ensure_reports_dir()

    print("▶️ Запуск бенчмарків…")
    rows = run_benchmarks(args.sizes, args.large_sizes, args.patterns, repeats=args.repeats)
    csv_path = save_csv(rows, outdir)
    print(f"✓ Результати: {csv_path}")

    growth = compute_growth(rows)
    growth_csv = save_growth_csv(growth, outdir)
    print(f"✓ Коефіцієнти зростання: {growth_csv}")

    plots = try_make_plots(rows, outdir) if args.plots else []
    if plots:
        print("✓ Графіки:")
        for p in plots: print(f"  - {p}")

    if not args.no_readme:
        readme_path = write_readme(rows, growth, plots, outdir)
        print(f"✓ Звіт: {readme_path}")

    print("\nГотово ✅ (див. каталог: reports/)")

if __name__ == "__main__":
    main()
