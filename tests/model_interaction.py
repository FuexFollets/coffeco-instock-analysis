from __future__ import annotations

from dataclasses import dataclass

from data_management.database.models.model import Model
from data_management.database.wrapper import SQLDataType, SQLDatabase, SQLTable


@dataclass
class MyModel(Model, sql_table_name = "testtable"):
    name: str
    f1: float


@dataclass
class MatchingModel(Model, sql_table_name = "testtable"):
    name: bytes
    age: bytes
    f1: float
    f2: float

my_db: SQLDatabase = SQLDatabase("./test.db")
testtable: SQLTable = my_db.query_table("testtable")

instance = MatchingModel(None, b"bobby", b"sammy", 1.0, 2.0)
