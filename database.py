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

        # store as BLOB explicitly
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, sqlite3.Binary(password_hash))
        )

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print("DB add_user error:", e)
        return False


def verify_user(username):
    conn = sqlite3.connect("snake.db")
    cur = conn.cursor()

    cur.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()

    conn.close()

    if row:
        user_id, uname, password_blob = row

        # ensure password is bytes (SQLite might return memoryview)
        if isinstance(password_blob, memoryview):
            password_blob = password_blob.tobytes()

        return (user_id, uname, password_blob)

    return None


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

