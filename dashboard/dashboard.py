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


def plot_by_days(visits):
    days = [v.strftime("%A") for v in visits]
    counter = Counter(days)

    plt.figure()
    plt.title("Посещения по дням недели")
    plt.bar(counter.keys(), counter.values())
    plt.xticks(rotation=45)
    plt.show()


def plot_by_hours(visits):
    hours = [v.hour for v in visits]
    counter = Counter(hours)

    plt.figure()
    plt.title("Посещения по часам")
    plt.bar(counter.keys(), counter.values())
    plt.show()


def plot_subscriptions(subs):
    counter = Counter(subs)

    plt.figure()
    plt.title("Популярность абонементов")
    plt.bar(counter.keys(), counter.values())
    plt.show()


def main():
    visits = load_visits()
    subs = load_subscriptions()

    if not visits:
        print("Нет данных для графиков")
        return

    plot_by_days(visits)
    plot_by_hours(visits)
    plot_subscriptions(subs)


if __name__ == "__main__":
    main()