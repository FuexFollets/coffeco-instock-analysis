from __future__ import annotations

from dataclasses import dataclass, Field
from typing import ClassVar, Optional

import data_management.database.wrapper as db_wrapper


MODEL_TABLE_NAME_FIELD = "table_name"


@dataclass
class Model:
    table_name: ClassVar[str]
    rowid: Optional[int]

    def __init_subclass__(cls, sql_table_name: str):
        cls.table_name: str = sql_table_name

    @classmethod
    def to_sql_table(cls) -> db_wrapper.SQLTable:
        fields: dict[str, Field] = cls.__dataclass_fields__
        columns: list[db_wrapper.SQLColumn] = []

        for (
            field_name,
            field_type,
        ) in fields.items():
            if field_name == MODEL_TABLE_NAME_FIELD or field_name == "rowid":
                continue

            # Forgive me for this
            SQLDataType = db_wrapper.SQLDataType
            field_sql_data_type: SQLDataType = SQLDataType.from_type(
                eval(field_type.type)
            )

            if not isinstance(field_sql_data_type, SQLDataType):
                raise TypeError(f"Field '{field_name}' must be of type SQLDataType")

            columns.append(
                db_wrapper.SQLColumn(field_name, data_type=field_sql_data_type)
            )

        return db_wrapper.SQLTable(cls.table_name, columns=columns)
