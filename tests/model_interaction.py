from __future__ import annotations

from dataclasses import dataclass

from data_management.database.models.model import Model


@dataclass
class MyModel(Model, sql_table_name = "testtable"):
    name: str
    f1: float

instance = MyModel("test", 1.0)
