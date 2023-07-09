from __future__ import annotations

from hashlib import sha256
from enum import Enum

from data_management.constants import USER_DB_PATH, USER_DB_TABLE_NAME
from data_management.database.wrapper import SQLTable, SQLDatabase
from data_management.database.models.user import UserModel


class UserAuth:
    def __init__(self):
        self.user_table: SQLTable = SQLDatabase(USER_DB_PATH).query_table(
            USER_DB_TABLE_NAME
        )

    @staticmethod
    def gen_id(email: str) -> bytes:
        return sha256(email.encode()).digest()

    @staticmethod
    def gen_token(email: str, password: str) -> bytes:
        return sha256((email + password).encode()).digest()

    class VerificationStatus(Enum):
        SUCCESS = 0
        USER_NOT_FOUND = 1
        INCORRECT_TOKEN = 2

    def verify_token(self, email: str, token: bytes) -> VerificationStatus:
        users: list[UserModel] = self.user_table.query_values(export_model=UserModel)

        for user in users:
            if user.email == email:
                if user.token == token:
                    return self.VerificationStatus.SUCCESS
                else:
                    return self.VerificationStatus.INCORRECT_TOKEN

        return self.VerificationStatus.USER_NOT_FOUND
