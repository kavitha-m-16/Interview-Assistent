import sqlite3
import json
import hashlib
import secrets
import os
from datetime import datetime

DB_FOLDER = "data"
DB_PATH = os.path.join(DB_FOLDER, "intervaiq.db")


def get_connection():
    os.makedirs(DB_FOLDER, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_name TEXT,
            profile_json TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company TEXT,
            role TEXT,
            overall_score REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            question TEXT,
            category TEXT,
            difficulty TEXT,
            topic TEXT,
            answer TEXT,
            score REAL,
            result TEXT,
            technical_accuracy REAL,
            relevance REAL,
            completeness REAL,
            clarity REAL,
            what_went_well TEXT,
            what_went_wrong TEXT,
            explanation TEXT,
            model_answer TEXT,
            improvement_tip TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()


def hash_password(password):
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 200_000
    )
    return f"{salt.hex()}${password_hash.hex()}"


def verify_password(password, stored_password):
    try:
        salt_hex, hash_hex = stored_password.split("$")
        salt = bytes.fromhex(salt_hex)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 200_000
        )
        return secrets.compare_digest(password_hash.hex(), hash_hex)
    except Exception:
        return False


def create_user(name, email, password):
    connection = get_connection()
    cursor = connection.cursor()
    email = email.strip().lower()
    name = name.strip()

    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        connection.close()
        return False, "An account with this email already exists."

    cursor.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (name, email, hash_password(password), datetime.now().isoformat()),
    )
    connection.commit()
    user_id = cursor.lastrowid
    connection.close()
    return True, user_id


def verify_user(email, password):
    connection = get_connection()
    cursor = connection.cursor()
    email = email.strip().lower()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    connection.close()

    if user and verify_password(password, user["password_hash"]):
        return dict(user)
    return None


def get_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, name, email, created_at FROM users WHERE id = ?",
        (user_id,),
    )
    user = cursor.fetchone()
    connection.close()
    return dict(user) if user else None


def save_resume(user_id, resume_name, profile_json):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO resumes (user_id, resume_name, profile_json, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, resume_name, profile_json, datetime.now().isoformat()),
    )
    connection.commit()
    resume_id = cursor.lastrowid
    connection.close()
    return resume_id


def get_user_resumes(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM resumes
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]


def create_interview(user_id, company, role):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO interviews (user_id, company, role, overall_score, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, company, role, 0, datetime.now().isoformat()),
    )
    connection.commit()
    interview_id = cursor.lastrowid
    connection.close()
    return interview_id


def save_question_result(interview_id, user_id, question_data):
    connection = get_connection()
    cursor = connection.cursor()

    def db_text(value):
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return str(value) if value is not None else ""

    cursor.execute(
        """
        INSERT INTO interview_results (
            interview_id, user_id, question, category, difficulty, topic,
            answer, score, result, technical_accuracy, relevance,
            completeness, clarity, what_went_well, what_went_wrong,
            explanation, model_answer, improvement_tip, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            interview_id,
            user_id,
            question_data.get("question", ""),
            question_data.get("category", ""),
            question_data.get("difficulty", ""),
            question_data.get("topic", ""),
            question_data.get("answer", ""),
            question_data.get("score", 0),
            question_data.get("result", ""),
            question_data.get("technical_accuracy", 0),
            question_data.get("relevance", 0),
            question_data.get("completeness", 0),
            question_data.get("clarity", 0),
            db_text(question_data.get("what_went_well", "")),
            db_text(question_data.get("what_went_wrong", "")),
            question_data.get("explanation", ""),
            question_data.get("model_answer", ""),
            question_data.get("improvement_tip", ""),
            datetime.now().isoformat(),
        ),
    )
    connection.commit()
    result_id = cursor.lastrowid
    connection.close()
    return result_id


def update_interview_score(interview_id, user_id, overall_score):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE interviews
        SET overall_score = ?
        WHERE id = ? AND user_id = ?
        """,
        (overall_score, interview_id, user_id),
    )
    connection.commit()
    connection.close()


def get_user_interviews(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM interviews
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]


def get_interview_results(interview_id, user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM interview_results
        WHERE interview_id = ? AND user_id = ?
        ORDER BY id ASC
        """,
        (interview_id, user_id),
    )
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]


def get_user_interview_history(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            i.id AS interview_id,
            i.company,
            i.role,
            i.overall_score,
            i.created_at,
            r.question,
            r.category,
            r.difficulty,
            r.topic,
            r.answer,
            r.score,
            r.result,
            r.technical_accuracy,
            r.relevance,
            r.completeness,
            r.clarity,
            r.what_went_well,
            r.what_went_wrong,
            r.explanation,
            r.model_answer,
            r.improvement_tip
        FROM interviews i
        LEFT JOIN interview_results r ON i.id = r.interview_id
        WHERE i.user_id = ? AND (r.user_id = ? OR r.user_id IS NULL)
        ORDER BY i.id DESC, r.id ASC
        """,
        (user_id, user_id),
    )
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    print("IntervAIQ database initialized successfully!")
