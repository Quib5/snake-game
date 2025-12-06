import sqlite3

def init_db():
    conn = sqlite3.connect("snake.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password BLOB
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            score INTEGER
        );
    """)

    conn.commit()
    conn.close()


def add_user(username, password_hash):
    try:
        conn = sqlite3.connect("snake.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        conn.close()
        return True
    except:
        return False


def verify_user(username):
    conn = sqlite3.connect("snake.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    return user


def add_score(username, score):
    conn = sqlite3.connect("snake.db")
    cur = conn.cursor()

    # check current best for this user
    cur.execute("SELECT MAX(score) FROM scores WHERE username = ?", (username,))
    row = cur.fetchone()
    best = row[0] if row and row[0] is not None else None

    # only store if it's a new personal best
    if best is None or score > best:
        cur.execute("INSERT INTO scores (username, score) VALUES (?, ?)", (username, score))
        conn.commit()

    conn.close()


def get_leaderboard():
    conn = sqlite3.connect("snake.db")
    cur = conn.cursor()

    # one row per user: their best score
    cur.execute("""
        SELECT username, MAX(score) as best_score
        FROM scores
        GROUP BY username
        ORDER BY best_score DESC
        LIMIT 20
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

