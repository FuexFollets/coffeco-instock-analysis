from __future__ import annotations

USER_DB_PATH: str = "data/users.db"
USER_DB_TABLE_NAME: str = "users"
USER_DB_TABLE_COLUMNS: list[str] = ["id", "email", "token"]
USER_DB_TABLE_COLUMN_TYPES: list[str] = ["INTEGER PRIMARY KEY", "TEXT", "TEXT"]
