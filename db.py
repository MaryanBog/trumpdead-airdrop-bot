import sqlite3

conn = sqlite3.connect("airdrop.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS claims (
    user_id INTEGER PRIMARY KEY,
    wallet TEXT
)
""")
conn.commit()

def has_claimed(user_id):
    cursor.execute("SELECT 1 FROM claims WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def save_claim(user_id, wallet):
    cursor.execute("INSERT INTO claims (user_id, wallet) VALUES (?, ?)", (user_id, wallet))
    conn.commit()
