from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    login: str
    password_hash: str
    first_name: str
    last_name: str

@dataclass
class Parcel:
    id: int
    owner_id: int
    description: str
    weight: float
    status: str = "created"

@dataclass
class Delivery:
    id: int
    parcel_id: int
    sender_id: int
    recipient_id: int
    status: str = "pending"