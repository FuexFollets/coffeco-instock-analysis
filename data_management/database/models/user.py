from __future__ import annotations

from dataclasses import dataclass


@dataclass
class User:
    id: bytes
    email: str
    token: bytes
