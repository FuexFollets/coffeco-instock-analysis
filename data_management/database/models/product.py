from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    id: bytes
    name: str
    price: float
    amount: Optional(int)
