from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from data_management.database.models.product import Product


@dataclass
class DataEntry:
    id: bytes
    date: datetime
    product: Product
    amount: int

    # Add other fields as needed
