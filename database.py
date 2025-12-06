import sqlite3

def init_db():
    conn = sqlite3.connect("snake.db")
    cur = conn.cursor()

    # users table – store passwords as BLOB for bcrypt
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password BLOB
        )
    """)

    # scores table – record all best scores
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            score INTEGER
        )
    """)

    conn.commit()
    conn.close()


def add_user(username, password_hash):
    try:
        conn = sqlite3.connect("snake.db")
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, (username, sqlite3.Binary(password_hash)))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print("add_user ERROR:", e)
        return False


def verify_user(username):
    conn = sqlite3.connect("snake.db")
    cur = conn.cursor()

    cur.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()

    conn.close()

    if row:
        user_id, uname, pwd = row

        # Convert from memoryview → bytes
        if isinstance(pwd, memoryview):
            pwd = pwd.tobytes()

        return (user_id, uname, pwd)

    return None


def add_score(username, score):
    conn = sqlite3.connect("snake.db")
    cur = conn.cursor()

    # Retrieve existing best score
    cur.execute("SELECT MAX(score) FROM scores WHERE username = ?", (username,))
    row = cur.fetchone()
    best = row[0] if row and row[0] is not None else None

    # Only insert if new best score
    if best is None or score > best:
        cur.execute(
            "INSERT INTO scores (username, score) VALUES (?, ?)",
            (username, score)
        )
        conn.commit()

    conn.close()


def get_leaderboard():
    conn = sqlite3.connect("snake.db")
    cur = conn.cursor()

    # GROUP BY → only show best score per user
    cur.execute("""
        SELECT username, MAX(score)
        FROM scores
        GROUP BY username
        ORDER BY MAX(score) DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows
