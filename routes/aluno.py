from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from models.aluno import Aluno, AlunoInDB
from database import get_database

router = APIRouter()

# Create a new aluno
@router.post("/", response_model=AlunoInDB)
async def create_aluno(aluno: Aluno, db=Depends(get_database)):
    aluno_dict = aluno.dict()
    result = await db.alunos.insert_one(aluno_dict)
    aluno_dict['id'] = str(result.inserted_id)
    return AlunoInDB(**aluno_dict)

# Read all alunos
@router.get("/", response_model=List[AlunoInDB])
async def read_alunos(db=Depends(get_database)):
    alunos = await db.alunos.find().to_list(1000)
    return [AlunoInDB(**aluno, id=str(aluno['_id'])) for aluno in alunos]

# Read a single aluno by ID
@router.get("/{aluno_id}", response_model=AlunoInDB)
async def read_aluno(aluno_id: str, db=Depends(get_database)):
    aluno = await db.alunos.find_one({"_id": ObjectId(aluno_id)})
    if aluno is None:
        raise HTTPException(status_code=404, detail="Aluno not found")
    return AlunoInDB(**aluno, id=str(aluno['_id']))

# Update an aluno by ID
@router.put("/{aluno_id}", response_model=AlunoInDB)
async def update_aluno(aluno_id: str, aluno: Aluno, db=Depends(get_database)):
    result = await db.alunos.update_one({"_id": ObjectId(aluno_id)}, {"$set": aluno.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Aluno not found")
    updated_aluno = await db.alunos.find_one({"_id": ObjectId(aluno_id)})
    return AlunoInDB(**updated_aluno, id=str(updated_aluno['_id']))

# Delete an aluno by ID
@router.delete("/{aluno_id}", response_model=dict)
async def delete_aluno(aluno_id: str, db=Depends(get_database)):
    result = await db.alunos.delete_one({"_id": ObjectId(aluno_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Aluno not found")
    return {"message": "Aluno deleted successfully"}