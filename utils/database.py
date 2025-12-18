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


def save_analysis(user_type, role, score, present, missing, resume_text):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    resume_hash = generate_resume_hash(resume_text)

    cursor.execute("""
        INSERT INTO analysis_history
        (user_type, role, match_score, present_skills, missing_skills, resume_hash, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_type,
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


def fetch_analysis_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, match_score, present_skills, missing_skills, resume_hash, timestamp
        FROM analysis_history
        ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "role": row[0],
            "score": row[1],
            "present": row[2].split(",") if row[2] else [],
            "missing": row[3].split(",") if row[3] else [],
            "resume_hash": row[4][:10],  # short hash for display
            "timestamp": row[5]
        })

    return history
