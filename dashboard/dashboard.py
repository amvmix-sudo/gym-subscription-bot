import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter

DB_PATH = "data/database.db"

DAYS_RU = {
    "Monday": "Пн",
    "Tuesday": "Вт",
    "Wednesday": "Ср",
    "Thursday": "Чт",
    "Friday": "Пт",
    "Saturday": "Сб",
    "Sunday": "Вс",
}


def load_visits():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT visit_time FROM visits")
    data = cur.fetchall()
    conn.close()
    return [datetime.fromisoformat(x[0]) for x in data]


def load_subscriptions():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT type FROM subscriptions")
    data = cur.fetchall()
    conn.close()
    return [x[0] for x in data]


def autolabel(ax, rects):
    """Подписи, которые НЕ вылезают за график"""
    y_max = ax.get_ylim()[1]

    for rect in rects:
        height = rect.get_height()

        # если столбец упёрся в потолок — рисуем внутри
        if height >= y_max:
            ax.text(
                rect.get_x() + rect.get_width() / 2,
                y_max - 0.5,
                f"{int(height)}",
                ha="center",
                va="top",
                color="white",
                fontsize=10,
                fontweight="bold"
            )
        else:
            ax.text(
                rect.get_x() + rect.get_width() / 2,
                height + 0.2,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=10
            )


def main():
    visits = load_visits()
    subs = load_subscriptions()

    if not visits:
        print("Нет данных")
        return

    # ---------- ДНИ ----------
    days_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days_ru = [DAYS_RU[d] for d in days_en]

    day_counter = Counter([v.strftime("%A") for v in visits])
    day_values = [day_counter.get(d, 0) for d in days_en]

    # ---------- ЧАСЫ ----------
    hours = list(range(7, 24))
    hour_counter = Counter([v.hour for v in visits])
    hour_values = [hour_counter.get(h, 0) for h in hours]

    # ---------- АБОНЕМЕНТЫ ----------
    subs_order = ["Разовый", "Недельный", "Месячный", "Годовой"]
    sub_counter = Counter(subs)
    sub_values = [sub_counter.get(s, 0) for s in subs_order]

    fig, axes = plt.subplots(3, 1, figsize=(10, 12))

    # --- ДНИ ---
    r1 = axes[0].bar(days_ru, day_values)
    axes[0].set_title("Посещения по дням недели")
    axes[0].set_ylim(0, 10)
    axes[0].set_yticks(range(0, 11))
    axes[0].grid(axis="y", linestyle="--", alpha=0.5)
    autolabel(axes[0], r1)

    # --- ЧАСЫ ---
    r2 = axes[1].bar(hours, hour_values)
    axes[1].set_title("Посещения по часам")
    axes[1].set_ylim(0, 10)
    axes[1].set_yticks(range(0, 11))
    axes[1].set_xticks(hours)
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)
    autolabel(axes[1], r2)

    # --- АБОНЕМЕНТЫ ---
    r3 = axes[2].bar(subs_order, sub_values)
    axes[2].set_title("Популярность абонементов")
    axes[2].set_ylim(0, 10)
    axes[2].set_yticks(range(0, 11))
    axes[2].grid(axis="y", linestyle="--", alpha=0.5)
    autolabel(axes[2], r3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()