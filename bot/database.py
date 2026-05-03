import sqlite3
from datetime import datetime, timedelta

DB_PATH = "data/database.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        client_id TEXT UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        visits_left INTEGER,
        expires_at TEXT,
        status TEXT
    )
    """)

    # НОВОЕ — таблица посещений
    cur.execute("""
    CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        visit_time TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_user(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
    user = cur.fetchone()

    if user:
        conn.close()
        return user[0]

    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0] + 1
    client_id = f"id_client{count}"

    cur.execute(
        "INSERT INTO users (telegram_id, client_id) VALUES (?, ?)",
        (telegram_id, client_id)
    )

    conn.commit()

    cur.execute("SELECT id FROM users WHERE telegram_id=?", (telegram_id,))
    user_id = cur.fetchone()[0]

    conn.close()
    return user_id


def create_subscription(user_id, sub_type):
    tariffs = {
        "Разовый": (1, 3),
        "Недельный": (2, 7),
        "Месячный": (8, 31),
        "Годовой": (96, 365),
    }

    visits, days = tariffs[sub_type]
    expires = datetime.now() + timedelta(days=days)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO subscriptions (user_id, type, visits_left, expires_at, status)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, sub_type, visits, expires.isoformat(), "active"))

    conn.commit()
    conn.close()


def get_subscription(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT s.id, s.type, s.visits_left, s.expires_at, s.status, u.client_id, u.id
    FROM subscriptions s
    JOIN users u ON s.user_id = u.id
    WHERE u.telegram_id=?
    ORDER BY s.id DESC LIMIT 1
    """, (telegram_id,))

    result = cur.fetchone()
    conn.close()
    return result


def update_subscription_status(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT s.id, s.expires_at, s.visits_left
    FROM subscriptions s
    JOIN users u ON s.user_id = u.id
    WHERE u.telegram_id=?
    ORDER BY s.id DESC LIMIT 1
    """, (telegram_id,))

    sub = cur.fetchone()

    if not sub:
        conn.close()
        return

    sub_id, expires_at, visits = sub
    expires_at = datetime.fromisoformat(expires_at)

    if datetime.now() > expires_at or visits <= 0:
        cur.execute("UPDATE subscriptions SET status='inactive' WHERE id=?", (sub_id,))
        conn.commit()

    conn.close()


def log_visit(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO visits (user_id, visit_time)
    VALUES (?, ?)
    """, (user_id, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def decrement_visit(telegram_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT s.id, s.visits_left, s.status, u.id
    FROM subscriptions s
    JOIN users u ON s.user_id = u.id
    WHERE u.telegram_id=?
    ORDER BY s.id DESC LIMIT 1
    """, (telegram_id,))

    sub = cur.fetchone()

    if not sub:
        conn.close()
        return "Нет абонемента"

    sub_id, visits, status, user_id = sub

    if status != "active":
        conn.close()
        return "Абонемент неактивен"

    if visits <= 0:
        cur.execute("UPDATE subscriptions SET status='inactive' WHERE id=?", (sub_id,))
        conn.commit()
        conn.close()
        return "Посещения закончились"

    visits -= 1

    new_status = "active"
    if visits == 0:
        new_status = "inactive"

    cur.execute("""
    UPDATE subscriptions 
    SET visits_left=?, status=? 
    WHERE id=?
    """, (visits, new_status, sub_id))

    # ЛОГИРОВАНИЕ ПОСЕЩЕНИЯ
    cur.execute("""
    INSERT INTO visits (user_id, visit_time)
    VALUES (?, ?)
    """, (user_id, datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return f"Посещение засчитано! Осталось: {visits}"