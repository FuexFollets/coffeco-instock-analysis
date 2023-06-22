from __future__ import annotations

from typing import NoneType
import sqlite3

from data_management import constants


def table_names(db_connection: sqlite3.Connection) -> list[str]:
    cursor: sqlite3.Cursor = db_connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    return [table[0] for table in cursor.fetchall()]


def initialize_users(db_connection: sqlite3.Conection) -> NoneType:
    if constants.USER_DB_TABLE_NAME not in table_names(db_connection):
        db_connection: sqlite3.Connection = sqlite3.connect(constants.USER_DB_PATH)
        cursor: sqlite3.Cursor = db_connection.cursor()
        cursor.execute(f"CREATE TABLE {constants.USER_DB_TABLE_NAME}")
