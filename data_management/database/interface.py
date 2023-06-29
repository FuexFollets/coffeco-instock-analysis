from __future__ import annotations

from typing import NoneType
from pathlib import Path
import sqlite3


class Database:
    def __init__(self, path: str | Path):
        self.path: Path = Path(path)
        self.connection: sqlite3.Connection = sqlite3.connect(self.path)
        self.cursor: sqlite3.Cursor = self.connection.cursor()

    def table_names(self) -> list[str]:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        return [table[0] for table in self.cursor.fetchall()]

    def create_table(self, name: str, columns: list[str]) -> NoneType:
        self.cursor.execute(f"CREATE TABLE {name} ({', '.join(columns)});")

    def insert(self, table: str, values: list[str]) -> NoneType:
        self.cursor.execute(f"INSERT INTO {table} VALUES ({', '.join(values)});")

    def query_table(self, table: str) -> list[tuple]:
        self.cursor.execute(f"SELECT * FROM {table};")

        return self.cursor.fetchall()
