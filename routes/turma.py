from fastapi import APIRouter, HTTPException, Query
from database import get_engine
from models.modelos import Turma, Aluno
from odmantic import ObjectId
from datetime import datetime

router = APIRouter(
    prefix="/turmas",  # Prefix for all routes
    tags=["Turmas"],   # Tag for automatic documentation
)

engine = get_engine()

# Turmas
@router.post("/", response_model=Turma)
async def create_turma(turma: Turma):
    await engine.save(turma)
    return turma

@router.get("/", response_model=list[Turma])
async def read_turmas(offset: int = 0, limit: int = Query(default=10, le=100)):
    turmas = await engine.find(Turma, skip=offset, limit=limit)
    return turmas

@router.get("/{turma_id}", response_model=Turma)
async def read_turma(turma_id: str):
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    return turma

@router.put("/{turma_id}", response_model=Turma)
async def update_turma(turma_id: str, turma_data: dict):
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    for key, value in turma_data.items():
        setattr(turma, key, value)
    await engine.save(turma)
    return turma

@router.get("/nome/{nome_turma}", response_model=dict)
async def get_tutor_and_nivel_by_nome_turma(nome_turma: str):
    turma = await engine.find_one(Turma, Turma.nome == nome_turma)
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    return {"tutor": turma.tutor.nome, "lingua": turma.tutor.lingua, "nivel": turma.nivel}

@router.get("/{turma_id}/alunos/quantidade", response_model=dict)
async def get_total_alunos_for_turma(turma_id: str):
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    total_alunos = len(turma.alunos)
    return {"total_alunos": total_alunos}

@router.delete("/{turma_id}")
async def delete_turma(turma_id: str):
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    await engine.delete(turma)
    return {"ok": True}