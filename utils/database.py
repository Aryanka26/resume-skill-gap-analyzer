import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "database.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            match_score REAL,
            present_skills TEXT,
            missing_skills TEXT,
            resume_hash TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_analysis(role, score, present, missing, resume_text):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    resume_hash = generate_resume_hash(resume_text)

    cursor.execute("""
        INSERT INTO analysis_history
        (role, match_score, present_skills, missing_skills, resume_hash, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        role,
        score,
        ",".join(present),
        ",".join(missing),
        resume_hash,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()



def generate_resume_hash(resume_text):
    return hashlib.sha256(resume_text.encode("utf-8")).hexdigest()
