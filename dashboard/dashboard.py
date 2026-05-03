import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter

DB_PATH = "data/database.db"

# Русские названия дней
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
    """Подписывает значения над столбцами"""
    for rect in rects:
        height = rect.get_height()
        ax.annotate(
            f"{int(height)}",
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
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

    # ---------- ДНИ НЕДЕЛИ ----------
    days_order_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days_order_ru = [DAYS_RU[d] for d in days_order_en]

    day_counter = Counter([v.strftime("%A") for v in visits])
    day_values = [day_counter.get(day, 0) for day in days_order_en]

    # ---------- ЧАСЫ ----------
    hours_range = list(range(7, 24))
    hour_counter = Counter([v.hour for v in visits])
    hour_values = [hour_counter.get(h, 0) for h in hours_range]

    # ---------- АБОНЕМЕНТЫ ----------
    subs_order = ["Разовый", "Недельный", "Месячный", "Годовой"]
    sub_counter = Counter(subs)
    sub_values = [sub_counter.get(s, 0) for s in subs_order]

    # ---------- СТИЛЬ ----------
    plt.rcParams["font.size"] = 11

    fig, axes = plt.subplots(3, 1, figsize=(10, 12))

    # --- 1. Дни недели ---
    rects1 = axes[0].bar(days_order_ru, day_values)
    axes[0].set_title("Посещения по дням недели")
    axes[0].set_ylim(0, 10)
    axes[0].set_yticks(range(0, 11))
    axes[0].grid(axis="y", linestyle="--", alpha=0.5)
    autolabel(axes[0], rects1)

    # --- 2. Часы ---
    rects2 = axes[1].bar(hours_range, hour_values)
    axes[1].set_title("Посещения по часам")
    axes[1].set_ylim(0, 10)
    axes[1].set_yticks(range(0, 11))
    axes[1].set_xticks(hours_range)
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)
    autolabel(axes[1], rects2)

    # --- 3. Абонементы ---
    rects3 = axes[2].bar(subs_order, sub_values)
    axes[2].set_title("Популярность абонементов")
    axes[2].set_ylim(0, 10)
    axes[2].set_yticks(range(0, 11))
    axes[2].grid(axis="y", linestyle="--", alpha=0.5)
    autolabel(axes[2], rects3)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()