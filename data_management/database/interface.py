from __future__ import annotations

from pathlib import Path
from typing import Literal, Any
from dataclasses import dataclass

import sqlite3


ANY: str = ""
NULL: str = "NULL"
INTEGER: str = "INTEGER"
REAL: str = "REAL"
TEXT: str = "TEXT"
BLOB: str = "BLOB"

SQLDataType = Literal[NULL, INTEGER, REAL, TEXT, BLOB, ANY]


@dataclass
class SQLColumn:
    def __init__(self,
                 name: str,
                 /,
                 *,
                 cid: int = -1,
                 data_type: SQLDataType = ANY,
                 not_null: bool = False,
                 default_value: Any = None,
                 primary_key: bool = False):
        self.name: str = name
        self.cid: int = cid
        self.data_type: SQLDataType = data_type
        self.not_null: bool = not_null
        self.default_value: Any = default_value
        self.primary_key: bool = primary_key



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

    def create_table_column(self, table: str, column: str, data_type: SQLDataType):
        self.cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {data_type};")
        self.connection.commit()

        return self

    def insert_into_table(self, table: str, values: list[Any] | dict[str, Any]):
        fields: list[str] = self.query_table_columns(table)
        insert_string: str = ', '.join('?' * len(fields))

        if isinstance(values, dict):
            inserted_values: list[Any] = [values[field] if field in values else None for field in fields]

            self.cursor.execute(f"INSERT INTO {table}({fields}) VALUES({insert_string});", inserted_values)
            self.connection.commit()

        elif isinstance(values, list):
            self.cursor.execute(f"INSERT INTO {table}({fields}) VALUES({insert_string});", values)
            self.connection.commit()

        return self

    def query_all_values(self, table: str) -> list[tuple]:
        self.cursor.execute(f"SELECT rowid, * FROM {table};")

        return self.cursor.fetchall()

    def query_table_columns(self, table: str) -> list[str]:
        self.cursor.execute(f"PRAGMA table_info({table});")

        return [column[1] for column in self.cursor.fetchall()]

    def query_row_value(self, table: str, rowid: int = None) -> list[tuple] | tuple:
        if (rowid is None):
            self.cursor.execute(f"SELECT * FROM {table};")

            return self.cursor.fetchall()

        self.cursor.execute(f"SELECT * FROM {table} WHERE rowid={rowid};")
        return self.cursor.fetchone()

    def query_column_value(self, table: str, column: str, rowid: int = None) -> list[tuple]:
        if rowid is not None:
            self.cursor.execute(f"SELECT {column} FROM {table} WHERE rowid={rowid};")
        else:
            self.cursor.execute(f"SELECT {column} FROM {table};")

        return self.cursor.fetchall()

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

    def update_table_value(self, table: str, rowid: int, column: str, value: str):
        self.cursor.execute(f"UPDATE {table} SET {column}={value} WHERE rowid={rowid};")
        self.connection.commit()

        return self

    def delete_empty_table_columns(self, table: str):
        table_columns: list[str] = self.query_table_columns(table)

        for column in table_columns:
            if all(value is None for value in self.query_column_value(table, column)):
                self.delete_table_column(table, column)
