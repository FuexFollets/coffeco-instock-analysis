from __future__ import annotations

from dataclasses import dataclass, Field

from data_management.database.wrapper import SQLColumn, SQLTable, SQLDataType


MODEL_TABLE_NAME_FIELD = "table_name"

@dataclass
class Model:
    table_name: str

    def __init_subclass__(cls, sql_table_name: str):
        cls.table_name: str = sql_table_name

    @classmethod
    def to_sql_table(cls) -> SQLTable:
        fields: dict[str, Field] = cls.__dataclass_fields__
        columns: list[SQLColumn] = []

        for field_name, field_type, in fields.items():
            if field_name == MODEL_TABLE_NAME_FIELD:
                continue

            if not isinstance(field_type.type, SQLDataType):
                raise TypeError(f"Field '{field_name}' must be of type SQLDataType")

            columns.append(SQLColumn(field_name, data_type=field_type.type))

        return SQLTable(cls.table_name, columns=columns)

