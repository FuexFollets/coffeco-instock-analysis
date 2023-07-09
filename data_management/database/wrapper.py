from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Iterable, Type
from dataclasses import dataclass
from enum import Enum

import sqlite3

import data_management.database.models.model as db_model


@dataclass
class StringTypePair:
    sql_type: str
    py_type: type

    def equal_types(self, other: StringTypePair) -> bool:
        return self.py_type == other.py_type

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
        return [SQLDataType.NULL, SQLDataType.INTEGER, SQLDataType.REAL, SQLDataType.TEXT, SQLDataType.BLOB, SQLDataType.DEFAULT]

@dataclass
class SQLColumn:
    def __init__(
        self,
        name: str,
        /,
        *,
        cid: Optional[int] = None,
        data_type: SQLDataType = SQLDataType.DEFAULT,
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
            f"SQLColumn(name={self.name}, cid={self.cid}, data_type={self.data_type}, " \
            f"not_null={self.not_null}, default_value={self.default_value}, primary_key={self.primary_key})"
        )

    def simple_str(self):
        return f"SQLColumn(name={self.name}, data_type={self.data_type})"

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
                tuple[int, str, str, bool, Any, bool]
            ] = self.cursor.fetchall()

            self.columns: list[SQLColumn] = [
                SQLColumn(
                    db_column[1],
                    cid=db_column[0],
                    data_type=SQLDataType.from_string(db_column[2]),
                    not_null=db_column[3],
                    default_value=db_column[4],
                    primary_key=db_column[5],
                )
                for db_column in db_columns
            ]
        elif columns is not None:
            self.columns: list[SQLColumn] = columns

    def matches_model(self, model: Type[db_model.Model]) -> bool:
        model_datatype_fields: list[SQLColumn] = model.to_sql_table().columns

        if len(self.columns) != len(model_datatype_fields):
            return False

        for this_column, model_column in zip(self.columns, model_datatype_fields):
            if this_column.data_type.value.py_type != model_column.data_type.value.py_type:
                return False

        return True


    def query_values(self, export_model: Optional[Type[db_model.Model]] = None) -> list[tuple] | list[db_model.Model]:
        if self.cursor is None:
            raise ValueError("table has no assigned cursor")

        self.cursor.execute(f"SELECT rowid, * FROM {self.name};")
        fields = self.cursor.fetchall()

        if export_model is None:
            return fields

        return [export_model(*row_content) for row_content in fields]


    def query_columns(self, columns: list[str] | str, rowid: Optional[int] = None) -> list[tuple]:
        if self.cursor is None:
            raise ValueError("table has no assigned cursor")

        column_selection_string: str = ", ".join(columns) if isinstance(columns, list) else columns

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

    def insert_row(self, values: list[Any] | dict[str, Any] | Type[db_model.Model]):
        fields: list[str] = [column.name for column in self.columns]
        fields_string: str = ", ".join(fields)
        insert_string: str = ", ".join("?" * len(fields))

        if self.cursor is None or self.connection is None:
            raise ValueError("table has no assigned cursor or connection")

        if isinstance(values, db_model.Model):
            print(f"{insert_string = }")
            print(f"{[*values.__dict__.values()] = }")
            print(f"{fields_string = }")

            self.cursor.execute(
                f"INSERT INTO {self.name}({fields_string}) VALUES({insert_string});",
                [*values.__dict__.values()][1:]
            )
            self.connection.commit()

        elif isinstance(values, dict):
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
            if all(value[0] is None for value in self.query_columns([column.name])):
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
        column_strings: list[str] = [column.simple_str() for column in self.columns]

        return f"SQLTable(name={self.name}, columns={column_strings})"

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
