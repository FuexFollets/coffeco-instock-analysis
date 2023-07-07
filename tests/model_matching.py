from __future__ import annotations

from dataclasses import dataclass

from data_management.database.wrapper import SQLDatabase, SQLDataType, SQLColumn, SQLTable
from data_management.database.models.model import Model


my_db: SQLDatabase = SQLDatabase("./test.db")
testtable: SQLTable = my_db.query_table("testtable")


@dataclass
class MatchingModel(Model, sql_table_name = "testtable"):
    name: SQLDataType.BLOB.value.py_type
    age: SQLDataType.BLOB.value.py_type
    f1: SQLDataType.REAL.value.py_type
    f2: SQLDataType.REAL.value.py_type

@dataclass
class NotMatchingModel(Model, sql_table_name = "testtable"):
    name: SQLDataType.BLOB.value.py_type
    age: SQLDataType.INTEGER.value.py_type
    f1: SQLDataType.REAL.value.py_type
    f2: SQLDataType.TEXT.value.py_type
