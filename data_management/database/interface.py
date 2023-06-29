from __future__ import annotations

from pathlib import Path
from typing import Literal

import sqlite3


NULL: str = "NULL"
INTEGER: str = "INTEGER"
REAL: str = "REAL"
TEXT: str = "TEXT"
BLOB: str = "BLOB"

SQLDataType = Literal[NULL, INTEGER, REAL, TEXT, BLOB]


class Database:
    def __init__(self, path: str | Path):
        self.path: Path = Path(path)
        self.connection: sqlite3.Connection = sqlite3.connect(self.path)
        self.cursor: sqlite3.Cursor = self.connection.cursor()

    def query_table_names(self) -> list[str]:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        return [table[0] for table in self.cursor.fetchall()]

    def create_table(self, name: str, columns: list[tuple[str, SQLDataType]]):
        table_fields: str = ', '.join([f"{column[0]} {column[1]}" for column in columns])

        self.cursor.execute(f"""
                            CREATE TABLE IF NOT EXISTS {name} (
                                {table_fields}
                            );
                            """)
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

    def query_table_values(self, table: str, rowid: int = None) -> list[tuple]:
        if (rowid is None):
            self.cursor.execute(f"SELECT * FROM {table};")

            return self.cursor.fetchall()

        self.cursor.execute(f"SELECT * FROM {table} WHERE rowid={rowid};")
        return self.cursor.fetchone()

    def delete_table(self, table: str):
        self.cursor.execute(f"DROP TABLE {table};")
        self.connection.commit()

        return self

    def delete_table_column(self, table: str, column: str):
        self.cursor.execute(f"ALTER TABLE {table} DROP COLUMN {column};")
        self.connection.commit()

        return self

    def delete_table_row(self, table: str, rowid: str):
        self.cursor.execute(f"DELETE FROM {table} WHERE rowid={rowid};")
        self.connection.commit()

        return self
