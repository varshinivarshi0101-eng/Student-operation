import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class StudentDatabase:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date_of_birth TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    course TEXT,
                    address TEXT,
                    enrollment_date TEXT,
                    CHECK (email IS NOT NULL OR phone IS NOT NULL)
                )
                """
            )
