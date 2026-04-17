import sqlite3
from datetime import datetime

# connect database
conn = sqlite3.connect("carbon.db", check_same_thread=False)
c = conn.cursor()

# ---------------- TABLES ----------------
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT UNIQUE,
    password TEXT
)
""")

# ✅ UPDATED: added date column
c.execute("""
CREATE TABLE IF NOT EXISTS history (
    username TEXT,
    co2 REAL,
    category TEXT,
    date TEXT
)
""")

conn.commit()

# ---------------- FUNCTIONS ----------------

# add user
def add_user(username, password):
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        conn.commit()
        return "success"
    except:
        return "exists"


# login user
def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()

    if user is None:
        return "no_user"
    elif user[1] != password:
        return "wrong_password"
    else:
        return "success"


# ✅ UPDATED: save history WITH date
def save_history(username, co2, category):
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT INTO history VALUES (?, ?, ?, ?)", (username, co2, category, today))
    conn.commit()


# ✅ UPDATED: get history WITH date
def get_history(username):
    c.execute("""
    SELECT username, co2, category, date
    FROM history
    WHERE username=?
    ORDER BY date DESC
    """, (username,))
    return c.fetchall()


# 🏆 ✅ UPDATED: MONTHLY leaderboard
def get_leaderboard():
    current_month = datetime.now().strftime("%Y-%m")

    c.execute("""
    SELECT username, AVG(co2) as avg_co2
    FROM history
    WHERE strftime('%Y-%m', date) = ?
    GROUP BY username
    ORDER BY avg_co2 ASC
    LIMIT 5
    """, (current_month,))

    return c.fetchall()