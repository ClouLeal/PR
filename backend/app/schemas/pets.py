from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel


class PetCreate(BaseModel):
    name: str
    species: str
    breed: str | None = None
    birth_date: date | None = None


class PetResponse(BaseModel):
    id: UUID
    name: str
    species: str
    breed: str | None = None
    birth_date: date | None = None
    created_at: datetime

    class Config:
        from_attributes = True
