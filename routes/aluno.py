from fastapi import APIRouter, HTTPException, Query
from database import get_engine
from models.modelos import Aluno, Turma
from odmantic import ObjectId

router = APIRouter(
    prefix="/alunos",  # Prefix for all routes
    tags=["Alunos"],   # Tag for automatic documentation
)

engine = get_engine()

@router.post("/{turma_id}/alunos/", response_model=Aluno)
async def create_aluno_for_turma(turma_id: str, aluno: Aluno):
    # Verifica se o aluno já existe pelo email
    existing_aluno = await engine.find_one(Aluno, Aluno.email == aluno.email)
    if existing_aluno:
        raise HTTPException(status_code=400, detail="Aluno com esse email ja cadastrado")

    # Busca a turma pelo ID
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")

    # Atribui automaticamente o tutor da turma ao aluno
    aluno.tutor_id = turma.tutor.id
    aluno.turma_id = ObjectId(turma_id)
    
    await engine.save(aluno)
    return aluno

@router.get("/{turma_id}/alunos/", response_model=list[Aluno])
async def read_alunos_for_turma(turma_id: str, offset: int = 0, limit: int = Query(default=10, le=100)):
    alunos = await engine.find(Aluno, skip=offset, limit=limit)
    return alunos

@router.get("/aluno/{aluno_id}", response_model=Aluno)
async def read_aluno_by_id(aluno_id: str):
    aluno = await engine.find_one(Aluno, Aluno.id == ObjectId(aluno_id))
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno not found")
    return aluno

@router.get("/alunos/busca", response_model=list[Aluno])
async def search_alunos(texto: str):
    alunos = await engine.find(Aluno, Aluno.nome.match(texto))
    if not alunos:
        raise HTTPException(status_code=404, detail="No alunos found")
    return alunos

@router.put("/{turma_id}/alunos/{aluno_id}", response_model=Aluno)
async def update_aluno_for_turma(turma_id: str, aluno_id: str, aluno_data: dict):
    aluno = await engine.find_one(Aluno, Aluno.id == ObjectId(aluno_id))
    if not aluno or aluno.turma_id != ObjectId(turma_id):
        raise HTTPException(status_code=404, detail="Aluno not found")
    for key, value in aluno_data.items():
        setattr(aluno, key, value)
    await engine.save(aluno)
    return aluno

@router.delete("/{turma_id}/alunos/{aluno_id}")
async def delete_aluno_for_turma(turma_id: str, aluno_id: str):
    aluno = await engine.find_one(Aluno, Aluno.id == ObjectId(aluno_id))
    if not aluno or aluno.turma_id != ObjectId(turma_id):
        raise HTTPException(status_code=404, detail="Aluno not found")
    await engine.delete(aluno)
    return {"ok": True}

@router.put("/{aluno_id}/trocar-turma", response_model=Aluno)
async def trocar_turma_de_aluno(aluno_id: str, nova_turma_id: str):
    aluno = await engine.find_one(Aluno, Aluno.id == ObjectId(aluno_id))
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    nova_turma = await engine.find_one(Turma, Turma.id == ObjectId(nova_turma_id))
    if not nova_turma:
        raise HTTPException(status_code=404, detail="Nova turma não encontrada")

    # Atualiza o tutor do aluno com base na nova turma
    aluno.tutor = nova_turma.tutor
    aluno.turma_id = ObjectId(nova_turma_id)
    await engine.save(aluno)
    return aluno