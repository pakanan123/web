# setup_db.py
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

conn = sqlite3.connect('quiz_data.db')
c = conn.cursor()

# users, questions, scores
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    choice1 TEXT NOT NULL,
    choice2 TEXT NOT NULL,
    choice3 TEXT NOT NULL,
    answer TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    created_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# add sample questions if table empty
c.execute("SELECT COUNT(*) FROM questions")
if c.fetchone()[0] == 0:
    sample = [
        ("เลขฐาน 10 = 15, แปลงเป็น Binary คือ?", "1111", "1110", "1011", "1111"),
        ("เลขฐาน 10 = 10, แปลงเป็น Binary คือ?", "1001", "1010", "1100", "1010"),
        ("เลขฐาน 10 = 255, แปลงเป็น Hex คือ?", "0xFF", "FF", "F0", "FF"),
        ("ภาษาใดใช้พัฒนา Flask?", "Java", "Python", "C#", "Python"),
        ("HTML มีหน้าที่อะไร?", "ออกแบบรูปแบบข้อมูล", "สร้างโครงหน้าเว็บ", "เก็บข้อมูล", "สร้างโครงหน้าเว็บ")
    ]
    c.executemany('INSERT INTO questions (question,choice1,choice2,choice3,answer) VALUES (?,?,?,?,?)', sample)

# optional: add demo user (username: demo, password: demo123)
c.execute("SELECT COUNT(*) FROM users WHERE username = 'demo'")
if c.fetchone()[0] == 0:
    pw = generate_password_hash('demo123')
    c.execute("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)", ('demo', pw, datetime.utcnow().isoformat()))

conn.commit()
conn.close()
print("Database initialized (quiz_data.db).")