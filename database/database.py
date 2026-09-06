import sqlite3
import json
import os
from datetime import datetime

class ResumeDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "resume_history.db")
        self.db_path = db_path
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    resume_name TEXT NOT NULL,
                    ats_score INTEGER NOT NULL,
                    job_role TEXT NOT NULL,
                    skills TEXT NOT NULL,
                    missing_skills TEXT NOT NULL,
                    suggestions TEXT NOT NULL,
                    details TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_analysis(self, resume_name, ats_score, job_role, skills, missing_skills, suggestions, details):
        with self.get_connection() as conn:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("""
                INSERT INTO analyses (timestamp, resume_name, ats_score, job_role, skills, missing_skills, suggestions, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                resume_name,
                ats_score,
                job_role,
                json.dumps(skills),
                json.dumps(missing_skills),
                json.dumps(suggestions),
                json.dumps(details)
            ))
            conn.commit()

    def get_history(self):
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM analyses ORDER BY id DESC")
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "resume_name": row["resume_name"],
                    "ats_score": row["ats_score"],
                    "job_role": row["job_role"],
                    "skills": json.loads(row["skills"]),
                    "missing_skills": json.loads(row["missing_skills"]),
                    "suggestions": json.loads(row["suggestions"]),
                    "details": json.loads(row["details"])
                })
            return history
