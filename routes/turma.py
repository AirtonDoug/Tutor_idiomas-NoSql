from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from models.turma import Turma, TurmaInDB
from database import get_database

router = APIRouter()

# Create a new turma
@router.post("/", response_model=TurmaInDB)
async def create_turma(turma: Turma, db=Depends(get_database)):
    turma_dict = turma.dict()
    result = await db.turmas.insert_one(turma_dict)
    turma_dict['id'] = str(result.inserted_id)
    return TurmaInDB(**turma_dict)

# Read all turmas
@router.get("/", response_model=List[TurmaInDB])
async def read_turmas(db=Depends(get_database)):
    turmas = await db.turmas.find().to_list(1000)
    return [TurmaInDB(**turma, id=str(turma['_id'])) for turma in turmas]

# Read a single turma by ID
@router.get("/{turma_id}", response_model=TurmaInDB)
async def read_turma(turma_id: str, db=Depends(get_database)):
    turma = await db.turmas.find_one({"_id": ObjectId(turma_id)})
    if turma is None:
        raise HTTPException(status_code=404, detail="Turma not found")
    return TurmaInDB(**turma, id=str(turma['_id']))

# Update a turma by ID
@router.put("/{turma_id}", response_model=TurmaInDB)
async def update_turma(turma_id: str, turma: Turma, db=Depends(get_database)):
    result = await db.turmas.update_one({"_id": ObjectId(turma_id)}, {"$set": turma.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Turma not found")
    updated_turma = await db.turmas.find_one({"_id": ObjectId(turma_id)})
    return TurmaInDB(**updated_turma, id=str(updated_turma['_id']))

# Delete a turma by ID
@router.delete("/{turma_id}", response_model=dict)
async def delete_turma(turma_id: str, db=Depends(get_database)):
    result = await db.turmas.delete_one({"_id": ObjectId(turma_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Turma not found")
    return {"message": "Turma deleted successfully"}