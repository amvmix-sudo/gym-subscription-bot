import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter

DB_PATH = "data/database.db"


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


def main():
    visits = load_visits()
    subs = load_subscriptions()

    if not visits:
        print("Нет данных")
        return

    # ---------- ДНИ НЕДЕЛИ ----------
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_counter = Counter([v.strftime("%A") for v in visits])
    day_values = [day_counter.get(day, 0) for day in days_order]

    # ---------- ЧАСЫ ----------
    hours_range = list(range(7, 24))  # 07:00 - 23:00
    hour_counter = Counter([v.hour for v in visits])
    hour_values = [hour_counter.get(h, 0) for h in hours_range]

    # ---------- АБОНЕМЕНТЫ ----------
    subs_order = ["Разовый", "Недельный", "Месячный", "Годовой"]
    sub_counter = Counter(subs)
    sub_values = [sub_counter.get(s, 0) for s in subs_order]

    # ---------- ГРАФИКИ ----------
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))

    # 1. Дни недели
    axes[0].bar(days_order, day_values)
    axes[0].set_title("Посещения по дням недели")
    axes[0].set_ylim(0, 10)
    axes[0].set_yticks(range(0, 11))

    # 2. Часы
    axes[1].bar(hours_range, hour_values)
    axes[1].set_title("Посещения по часам")
    axes[1].set_ylim(0, 10)
    axes[1].set_yticks(range(0, 11))
    axes[1].set_xticks(hours_range)

    # 3. Абонементы
    axes[2].bar(subs_order, sub_values)
    axes[2].set_title("Популярность абонементов")
    axes[2].set_ylim(0, 10)
    axes[2].set_yticks(range(0, 11))

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()