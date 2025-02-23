from fastapi import APIRouter, HTTPException, Query
from database import get_engine
from models.modelos import Tutor, Turma, Aluno
from odmantic import ObjectId
from typing import List

router = APIRouter(
    prefix="/tutor",  # Prefix for all routes
    tags=["Tutors"],   # Tag for automatic documentation
)

engine = get_engine()

# Tutors
@router.post("/", response_model=Tutor)
async def create_tutor(tutor: Tutor):
    existing_tutor = await engine.find_one(Tutor, Tutor.email == tutor.email)
    if existing_tutor:
        raise HTTPException(status_code=400, detail="Tutor com esse email já existe")
    await engine.save(tutor)
    return tutor

@router.get("/", response_model=list[Tutor])
async def read_tutors(offset: int = 0, limit: int = Query(default=10, le=100)):
    tutors = await engine.find(Tutor, skip=offset, limit=limit)
    return tutors




@router.get("/{tutor_id}", response_model=Tutor)
async def read_tutor(tutor_id: str):
    tutor = await engine.find_one(Tutor, Tutor.id == ObjectId(tutor_id))
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return tutor

@router.put("/{tutor_id}", response_model=Tutor)
async def update_tutor(tutor_id: str, tutor_data: dict):
    tutor = await engine.find_one(Tutor, Tutor.id == ObjectId(tutor_id))
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    for key, value in tutor_data.items():
        setattr(tutor, key, value)
    await engine.save(tutor)
    return tutor

@router.delete("/{tutor_id}")
async def delete_tutor(tutor_id: str):
    tutor = await engine.find_one(Tutor, Tutor.id == ObjectId(tutor_id))
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    
    await engine.delete(tutor)
    return {"ok": True}

# Obter todas as turmas de um tutor específico
@router.get("/{tutor_id}/turmas", response_model=list[Turma])
async def get_turmas_por_tutor(tutor_id: str):
    turmas = await engine.find(Turma, Turma.tutor == ObjectId(tutor_id))
    if not turmas:
        raise HTTPException(status_code=404, detail="No turmas found for this tutor")
    return turmas

# Obter todos os alunos de um tutor específico
@router.get("/{tutor_id}/alunos", response_model=list[Aluno])
async def get_alunos_por_tutor(tutor_id: str):
    alunos = await engine.find(Aluno, Aluno.tutor_id == ObjectId(tutor_id))
    if not alunos:
        raise HTTPException(status_code=404, detail="No alunos found for this tutor")
    return alunos