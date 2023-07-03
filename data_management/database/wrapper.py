from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Iterable, Type
from dataclasses import dataclass
from enum import Enum

import sqlite3

from data_management.database.models.model import Model


@dataclass
class StringTypePair:
    sql_type: str
    py_type: type


class SQLDataType(Enum):
    NULL = StringTypePair("NULL", type(None))
    INTEGER = StringTypePair("INTEGER", int)
    REAL = StringTypePair("REAL", float)
    TEXT = StringTypePair("TEXT", str)
    BLOB = StringTypePair("BLOB", bytes)

    DEFAULT = StringTypePair("", bytes)

    @classmethod
    def from_string(cls, string: str) -> SQLDataType:
        for member in cls.members():
            if member.value.sql_type == string:
                return member

        raise ValueError(f"no SQLDataType with name '{string}'")

    @classmethod
    def from_type(cls, py_type: type) -> SQLDataType:
        for member in cls.members():
            if member.value.py_type == py_type:
                return member

        raise ValueError(f"no SQLDataType with type '{py_type}'")

    @staticmethod
    def members() -> Iterable[SQLDataType]:
        yield from SQLDataType.__members__.values()

@dataclass
class SQLColumn:
    def __init__(
        self,
        name: str,
        /,
        *,
        cid: Optional[int] = None,
        data_type: SQLDataType = SQLDataType.BLOB,
        not_null: bool = False,
        default_value: Any = None,
        primary_key: bool = False,
    ):
        self.name: str = name
        self.cid: Optional[int] = cid
        self.data_type: SQLDataType = data_type
        self.not_null: bool = not_null
        self.default_value: Any = default_value
        self.primary_key: bool = primary_key

    def __str__(self):
        return (
            f"SQLColumn(name={self.name}, cid={self.cid}, data_type={self.data_type.name}, " \
            f"not_null={self.not_null}, default_value={self.default_value}, primary_key={self.primary_key})"
        )

    def __repr__(self):
        return str(self)


class SQLTable:
    def __init__(
        self,
        name: str,
        /,
        *,
        connection: Optional[sqlite3.Connection] = None,
        cursor: Optional[sqlite3.Cursor] = None,
        columns: Optional[list[SQLColumn]] = None,
    ):
        self.name: str = name
        self.connection: Optional[sqlite3.Connection] = connection
        self.cursor: Optional[sqlite3.Cursor] = cursor

        if self.connection is not None and self.cursor is not None:
            self.cursor.execute(f"PRAGMA table_xinfo({self.name});")
            db_columns: list[
                tuple[int, str, SQLDataType, bool, Any, bool]
            ] = self.cursor.fetchall()

            self.columns: list[SQLColumn] = [
                SQLColumn(
                    db_column[1],
                    cid=db_column[0],
                    data_type=db_column[2],
                    not_null=db_column[3],
                    default_value=db_column[4],
                    primary_key=db_column[5],
                )
                for db_column in db_columns
            ]
        elif columns is not None:
            self.columns: list[SQLColumn] = columns

    def query_table_values(self) -> list[tuple]:
        if self.cursor is not None:
            self.cursor.execute(f"SELECT rowid, * FROM {self.name};")
            return self.cursor.fetchall()

        raise ValueError("table has no assigned cursor")

    def query_column_values(self, column: list[str], rowid: Optional[int] = None) -> list[tuple]:
        if self.cursor is None:
            raise ValueError("table has no assigned cursor")

        column_selection_string: str = ", ".join(column)

        if rowid is not None:
            self.cursor.execute(
                f"SELECT {column_selection_string} FROM {self.name} WHERE rowid={rowid};"
            )
        else:
            self.cursor.execute(f"SELECT {column_selection_string} FROM {self.name};")

        return self.cursor.fetchall()

    def query_row(self, rowid: int) -> tuple:
        if self.cursor is None:
            raise ValueError("table has no assigned cursor")

        self.cursor.execute(f"SELECT * FROM {self.name} WHERE rowid={rowid};")

        return self.cursor.fetchone()

    def insert_row(self, values: list[Any] | dict[str, Any]):
        fields: list[str] = [column.name for column in self.columns]
        fields_string: str = ", ".join(fields)
        insert_string: str = ", ".join("?" * len(fields))

        if self.cursor is None or self.connection is None:
            raise ValueError("table has no assigned cursor or connection")

        if isinstance(values, dict):
            inserted_values: list[Any] = [
                values[field] if field in values else None for field in fields
            ]

            self.cursor.execute(
                f"INSERT INTO {self.name}({fields_string}) VALUES({insert_string});",
                inserted_values,
            )
            self.connection.commit()

        elif isinstance(values, list):
            self.cursor.execute(
                f"INSERT INTO {self.name}({fields_string}) VALUES({insert_string});",
                values,
            )
            self.connection.commit()

        else:
            raise TypeError(
                f"paramater 'values' must be a list or dict, not {type(values)}"
            )

        return self

    def delete_row(self, rowid: int):
        if self.cursor is None or self.connection is None:
            raise ValueError("table has no assigned cursor or connection")

        self.cursor.execute(f"DELETE FROM {self.name} WHERE rowid={rowid};")
        self.connection.commit()

        return self

    def delete_column(self, column: str):
        if self.cursor is None or self.connection is None:
            raise ValueError("table has no assigned cursor or connection")

        self.cursor.execute(f"ALTER TABLE {self.name} DROP COLUMN {column};")
        self.connection.commit()

        return self

    def delete_unused_columns(self):
        for column in self.columns:
            if all(value[0] is None for value in self.query_column_values([column.name])):
                self.delete_column(column.name)

        return self

    def update_value(self, column: str, rowid: int, value: Any):
        if self.cursor is None or self.connection is None:
            raise ValueError("table has no assigned cursor or connection")

        self.cursor.execute(
            f"UPDATE {self.name} SET {column}={value} WHERE rowid={rowid};"
        )
        self.connection.commit()

        return self

    def __str__(self):
        return f"SQLTable(name={self.name}, columns={self.columns})"

    def __repr__(self):
        return str(self)


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
        table_columns = ", ".join(
            column.name + column.data_type.name for column in sqltable.columns
        )

        self.cursor.execute(f"CREATE TABLE {sqltable.name} ({table_columns});")
        self.connection.commit()

        return self

    def delete_table(self, name: str):
        self.cursor.execute(f"DROP TABLE {name};")
        self.connection.commit()

        return self

    def __str__(self):
        return f"SQLDatabase(path={self.path}, tables={self.query_table_names()})"

    def __repr__(self):
        return str(self)
