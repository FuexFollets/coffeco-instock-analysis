from __future__ import annotations

from pathlib import Path
import sqlite3


class Database:
    def __init__(self, path: str | Path):
        self.path: Path = Path(path)
        self.connection: sqlite3.Connection = sqlite3.connect(self.path)
        self.cursor: sqlite3.Cursor = self.connection.cursor()

    def query_table_names(self) -> list[str]:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        return [table[0] for table in self.cursor.fetchall()]

    def create_table(self, name: str, columns: list[str]):
        try:
            self.cursor.execute(f"CREATE TABLE {name} ({', '.join(columns)});")
            return self

        except sqlite3.OperationalError:
            return self

    def insert_into_table(self, table: str, values: list[str]):
        values_string: str = ', '.join(self.query_table_columns(table))
        insert_string: str = ', '.join('?' * len(values))

        self.cursor.execute(f"INSERT INTO {table}({values_string}) VALUES({insert_string});", values)
        self.connection.commit()

        return self

    def query_table_columns(self, table: str) -> list[str]:
        self.cursor.execute(f"PRAGMA table_info({table});")

        return [column[1] for column in self.cursor.fetchall()]

    def query_table_values(self, table: str) -> list[tuple]:
        self.cursor.execute(f"SELECT * FROM {table};")

        return self.cursor.fetchall()
