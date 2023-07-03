from __future__ import annotations

from hashlib import sha256

from data_management.constants import USER_DB_PATH, USER_DB_TABLE_NAME
from data_management.database.wrapper import SQLColumn, SQLTable, SQLDatabase


class UserAuth:
    def __init__(self):
        self.user_table: SQLTable = SQLDatabase(USER_DB_PATH).query_table(USER_DB_TABLE_NAME)

    @staticmethod
    def gen_token(username: str, password: str) -> str:
        return sha256((username + password).encode()).hexdigest()

    def verify_token(self, username: str, password: str) -> bool:
        token = self.gen_token(username, password)

