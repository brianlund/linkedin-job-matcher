# job_cache.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'job_cache.db')

def init_cache():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_jobs (
            job_id TEXT PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()

def job_seen(job_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_jobs WHERE job_id = ?", (job_id,))
    seen = cursor.fetchone() is not None
    conn.close()
    return seen

def mark_job_seen(job_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO processed_jobs (job_id) VALUES (?)", (job_id,))
    conn.commit()
    conn.close()
