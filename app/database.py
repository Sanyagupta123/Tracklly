import os
import sqlite3
from pathlib import Path
from typing import Optional, Union

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "careerpilot.db"


def get_database_path() -> Path:
    configured = os.getenv("CAREERPILOT_DB_PATH")
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_DB_PATH


def get_connection(db_path: Optional[Union[str, Path]] = None) -> sqlite3.Connection:
    resolved = Path(db_path) if db_path is not None else get_database_path()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(resolved))
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_path: Optional[Union[str, Path]] = None) -> str:
    resolved = Path(db_path) if db_path is not None else get_database_path()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with get_connection(resolved) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                job_description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Applied' CHECK (status IN ('Wishlist', 'Applied', 'Interview', 'Offer', 'Rejected')),
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    return str(resolved)
