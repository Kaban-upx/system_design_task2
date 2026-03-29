from pydantic import BaseModel, Field
from typing import Optional, List

# --- User ---
class UserCreate(BaseModel):
    login: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=72)  # ← Добавлено ограничение
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)

class UserResponse(BaseModel):
    id: int
    login: str
    first_name: str
    last_name: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Parcel ---
class ParcelCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    weight: float = Field(..., gt=0)  # ← gt=0 означает "greater than 0" (строго больше нуля)

class ParcelResponse(BaseModel):
    id: int
    owner_id: int
    description: str
    weight: float
    status: str

# --- Delivery ---
class DeliveryCreate(BaseModel):
    parcel_id: int = Field(..., gt=0)
    recipient_id: int = Field(..., gt=0)

class DeliveryResponse(BaseModel):
    id: int
    parcel_id: int
    sender_id: int
    recipient_id: int
    status: str