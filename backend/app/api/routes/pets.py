from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.base import SessionLocal
from app.models.pet import Pet
from app.schemas.pets import PetCreate, PetResponse

router = APIRouter()

#dependecy - abre e fecha a sessão do banco de dados por request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[PetResponse])
def list_pets(db: Session = Depends(get_db)):
    return db.query(Pet).all()


@router.post("", response_model=PetResponse, status_code=201)
def create_pet(pet: PetCreate, db: Session = Depends(get_db)):
    db_pet = Pet(**pet.model_dump())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet


@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(pet_id: UUID, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return pet