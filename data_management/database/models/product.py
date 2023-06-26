from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Product:
    id: bytes
    name: str
    price: float

    # Add other fields as needed
