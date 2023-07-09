from __future__ import annotations

from dataclasses import dataclass

from data_management.database.models.model import Model


@dataclass
class UserModel(Model, sql_table_name="users"):
    id: bytes
    email: str
    token: bytes

