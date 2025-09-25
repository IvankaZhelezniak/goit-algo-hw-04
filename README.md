# Порівняння сортувань: Merge vs Insertion vs Timsort

Алгоритми: **Insertion sort** (вставками), **Merge sort** (злиттям), **Timsort** (`sorted`).
Шаблони: `random`, `sorted`, `reversed`, `nearly_sorted` (~1% перестановок).
Розміри: 1k, 2k, 5k (всі) + 10k, 20k, 50k (лише Merge і Timsort).

## Результати (секунди) для `random` (1k..5k)
| n | Insertion | Merge | Timsort (built-in) |
|---|---|---|---|
| 1000 | 0.0310 | 0.0024 | 0.0001 |
| 2000 | 0.1645 | 0.0055 | 0.0003 |
| 5000 | 1.0815 | 0.0221 | 0.0009 |

## Емпірична перевірка складності
Очікування: O(n) ≈ ×2 і ×2.5; O(n log n) ≈ ×2.1 і ×2.32; O(n²) ≈ ×4 і ×6.25.

| pattern | algorithm | 1k→2k | 2k→5k |
|---|---|---|---|
| random | Insertion | 5.31 | 6.57 |
| random | Merge | 2.32 | 4.02 |
| random | Timsort (built-in) | 2.24 | 3.51 |
| reversed | Insertion | 5.01 | 6.57 |
| reversed | Merge | 2.13 | 3.53 |
| reversed | Timsort (built-in) | 1.94 | 2.50 |
| nearly_sorted | Insertion | 4.43 | 5.91 |
| nearly_sorted | Merge | 2.24 | 3.12 |
| nearly_sorted | Timsort (built-in) | 2.20 | 2.43 |

## Висновки
1. **Timsort** стабільно найшвидший і майже лінійний на `sorted`/`nearly_sorted` завдяки виявленню пробіжок + вставкам на малих підмасивах.
2. **Merge sort** дає очікуване O(n log n) і добре масштабується, але повільніший за Timsort через відсутність адаптивності.
3. **Insertion sort** має квадратичне зростання на випадкових/зворотних наборах; придатний лише для малих або майже впорядкованих масивів.

Практичний висновок: для реальних задач використовуйте вбудований `sorted`/`list.sort` (Timsort).
