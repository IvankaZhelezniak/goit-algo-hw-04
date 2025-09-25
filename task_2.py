#!/usr/bin/env python3
"""
Програма, яка малює фрактал сніжинка Коха (Koch snowflake) рекурсивно. 
Кохова сніжинка (Koch snowflake) — рекурсивний фрактал.
Користувач задає рівень рекурсії (order). Чим більший order, тим детальніший малюнок.

Запуск (приклади):
    python task_2.py --order 3
    python task_2.py -o 5 --size 360                 (size — базова сторона трикутника в пікселях.)
"""

from __future__ import annotations

import argparse
import math
import turtle


#  РЕКУРСИВНЕ ЯДРО 
def koch_curve(t: turtle.Turtle, order: int, length: float) -> None:
    """
    Малює ОДИН сегмент кривої Коха довжиною `length`.

    Базовий випадок:
        order == 0  → просто пряма лінія довжиною length.

    Рекурсивний випадок:
        розбиває сегмент на 4 підсегменти (кожен у 3 рази коротший),
        між якими черепаха повертає: +60°, -120°, +60°.
    """
    if order == 0:
        t.forward(length)
    else:
        length /= 3.0
        koch_curve(t, order - 1, length)
        t.left(60)
        koch_curve(t, order - 1, length)
        t.right(120)
        koch_curve(t, order - 1, length)
        t.left(60)
        koch_curve(t, order - 1, length)


def draw_koch_snowflake(order: int, size: int = 300) -> None:
    """
    Малює повну сніжинку: три сторони рівностороннього трикутника,
    кожна — це крива Коха потрібного порядку.
    """
    # Налаштування вікна/черепахи
    screen = turtle.Screen()
    screen.title(f"Koch snowflake — order={order}")
    screen.bgcolor("white")
    screen.tracer(False)  # прискорює промальовку

    t = turtle.Turtle(visible=False)
    t.speed(0)
    t.penup()

    # Центруєм фігуру вікні: ставить у нижню ліву вершину
    h = size * math.sqrt(3) / 2   # висота рівностороннього трикутника
    t.goto(-size / 2, -h / 3)     # приблизно центровано
    t.pendown()

    # 3 сторони сніжинки
    for _ in range(3):
        koch_curve(t, order, size)
        t.right(120)

    screen.update()
    # Залишає вікно відкритим
    screen.mainloop()


# CLI-ПАРСИНГ
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Малює фрактал «сніжинка Коха» рекурсивно."
    )
    p.add_argument(
        "-o", "--order",
        type=int, default=3,
        help="рівень рекурсії (ціле число від 0 до 7; типово 3)"
    )
    p.add_argument(
        "--size", type=int, default=300,
        help="довжина сторони базового трикутника у пікселях (типово 300)"
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # Легка валідація: надто великі порядки сильно повільні
    order = max(0, min(args.order, 7))
    if order != args.order:
        print(f"⚠️ order={args.order} відкориговано до {order} (допустимо 0..7).")

    size = max(30, args.size)

    draw_koch_snowflake(order=order, size=size)


if __name__ == "__main__":
    main()
