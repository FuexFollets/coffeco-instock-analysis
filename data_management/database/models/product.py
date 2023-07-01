from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Product:
    id: bytes

    sku: str
    fn_sku: str
    asin: str
    name: str

    price: float

    # Add other fields as needed
