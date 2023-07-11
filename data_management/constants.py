from __future__ import annotations

import tomllib

USER_DB_PATH: str = "data/users.db"
USER_DB_TABLE_NAME: str = "users"

CREDENTIALS: dict[str, str]

with open("credentials.toml", "r") as file:
    CREDENTIALS = tomllib.loads(file.read())
