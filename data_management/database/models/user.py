from __future__ import annotations

from dataclasses import dataclass

from data_management.database.models.model import Model
from data_management.database.wrapper import SQLDataType


@dataclass
class User(Model, sql_table_name="users"):
    id: SQLDataType.TEXT.value.py_type
    email: str
    token: bytes
