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

    def __str__(self):
        return f"SQLColumn(name={self.name}, cid={self.cid}, data_type={self.data_type}, " \
               f"not_null={self.not_null}, default_value={self.default_value}, primary_key={self.primary_key})"

    def __repr__(self):
        return str(self)


class SQLTable:
    def __init__(self,
                 name: str,
                 /,
                 *,
                 connection: sqlite3.Connection = None,
                 cursor: sqlite3.Cursor = None,
                 columns: list[SQLColumn] = None):
        self.name: str = name
        self.connection: sqlite3.Connection = connection
        self.cursor: sqlite3.Cursor = cursor

        if connection is not None and cursor is not None:
            self.cursor.execute(f"PRAGMA table_xinfo({self.name});")
            columns: list[tuple[int, str, SQLDataType, int, Any, bool]] = self.cursor.fetchall()

            self.columns: list[SQLColumn] = [SQLColumn(column[1], cid=column[0], data_type=column[2],
                                                       not_null=column[3], default_value=column[4],
                                                       primary_key=column[5]) for column in columns]
        else:
            self.columns: list[SQLColumn] = columns

    def query_table_values(self) -> list[tuple]:
        self.cursor.execute(f"SELECT rowid, * FROM {self.name};")

        return self.cursor.fetchall()

    def query_column_values(self, column: str, rowid: int = None) -> list[tuple]:
        if rowid is not None:
            self.cursor.execute(f"SELECT {column} FROM {self.name} WHERE rowid={rowid};")
        else:
            self.cursor.execute(f"SELECT {column} FROM {self.name};")

        return self.cursor.fetchall()

    def query_row(self, rowid: int) -> tuple:
        self.cursor.execute(f"SELECT * FROM {self.name} WHERE rowid={rowid};")

        return self.cursor.fetchone()

    def insert_row(self, values: list[Any] | dict[str, Any]):
        fields: list[str] = [column.name for column in self.columns]
        insert_string: str = ', '.join('?' * len(fields))

        if isinstance(values, dict):
            inserted_values: list[Any] = [values[field] if field in values else None for field in fields]

            self.cursor.execute(f"INSERT INTO {self.name}({fields}) VALUES({insert_string});", inserted_values)
            self.connection.commit()

        elif isinstance(values, list):
            self.cursor.execute(f"INSERT INTO {self.name}({fields}) VALUES({insert_string});", values)
            self.connection.commit()

        return self

    def delete_row(self, rowid: int):
        self.cursor.execute(f"DELETE FROM {self.name} WHERE rowid={rowid};")
        self.connection.commit()

        return self

    def delete_column(self, column: str):
        self.cursor.execute(f"ALTER TABLE {self.name} DROP COLUMN {column};")
        self.connection.commit()

        return self

    def delete_unused_columns(self):
        for column in self.columns:
            if all(value[0] is None for value in self.query_column_values(column.name)):
                self.delete_column(column.name)

        return self

    def update_value(self, column: str, rowid: int, value: Any):
        self.cursor.execute(f"UPDATE {self.name} SET {column}={value} WHERE rowid={rowid};")
        self.connection.commit()

        return self

    def __str__(self):
        return f"SQLTable(name={self.name}, columns={self.columns})"


class SQLDatabase:
    def __init__(self, path: str | Path):
        self.path: Path = Path(path)
        self.connection: sqlite3.Connection = sqlite3.connect(self.path)
        self.cursor: sqlite3.Cursor = self.connection.cursor()

    def query_table_names(self) -> list[str]:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        return [table[0] for table in self.cursor.fetchall()]

    def query_table(self, name: str) -> SQLTable:
        return SQLTable(name, connection=self.connection, cursor=self.cursor)

    def query_all_tables(self) -> list[SQLTable]:
        return [self.query_table(name) for name in self.query_table_names()]

    def create_table(self, sqltable: SQLTable):
        table_columns = ', '.join(column.name + column.data_type for column in sqltable.columns)

        self.cursor.execute(f"CREATE TABLE {sqltable.name} ({table_columns});")
        self.connection.commit()

        return self
