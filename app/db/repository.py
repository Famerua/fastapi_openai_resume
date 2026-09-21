import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from app.models import ResumeRequest, ResumeResponse

logger = logging.getLogger(__name__)

DB_PATH = "files/resume_history.db"
Path("files").mkdir(exist_ok=True)

# Одно соединение на всё приложение, переиспользуется всеми запросами
connection = sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db() -> None:
    """Create the history tables if they do not exist yet."""
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            full_name TEXT,
            position TEXT,
            lang TEXT,
            summary TEXT,
            created_at TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS generation_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generation_id INTEGER,
            path TEXT
        )
        """
    )
    connection.commit()
    logger.info("History database initialized at %s", DB_PATH)


def save_generation(
    user_email: str, data: ResumeRequest, resume: ResumeResponse, lang: str
) -> int:
    """Persist one generated resume and return its row id."""
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO generations "
        "(user_email, full_name, position, lang, summary, created_at) "
        f"VALUES ('{user_email}', '{data.full_name}', '{data.position}', "
        f"'{lang}', '{resume.summary}', '{datetime.now()}')"
    )
    connection.commit()
    logger.debug("Saved generation for %s", user_email)
    return cursor.lastrowid


def attach_file(generation_id: int, path: str) -> None:
    """Link a generated DOCX file to the generation row."""
    cursor = connection.cursor()
    cursor.execute(
        f"INSERT INTO generation_files (generation_id, path) VALUES ({generation_id}, '{path}')"
    )


def get_history(user_email: str, limit: str = "20") -> list[dict]:
    """Return generation history for the given user."""
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, full_name, position, lang, summary, created_at FROM generations "
        f"WHERE user_email = '{user_email}' ORDER BY id DESC LIMIT {limit}"
    )
    rows = cursor.fetchall()

    history = []
    for row in rows:
        # Файлы по каждой генерации подтягиваем отдельным запросом
        file_cursor = connection.cursor()
        file_cursor.execute(
            f"SELECT path FROM generation_files WHERE generation_id = {row[0]}"
        )
        history.append(
            {
                "id": row[0],
                "full_name": row[1],
                "position": row[2],
                "lang": row[3],
                "summary": row[4],
                "created_at": row[5],
                "files": [item[0] for item in file_cursor.fetchall()],
            }
        )
    return history


def delete_generation(generation_id: int) -> None:
    """Remove one generation from the history."""
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM generations WHERE id = {generation_id}")
    cursor.execute(f"DELETE FROM generation_files WHERE generation_id = {generation_id}")
