from fastapi import APIRouter, HTTPException, Query
from database import get_engine
from models.modelos import Turma,Conversation, Tutor, TutorEmbed
from odmantic import ObjectId
from datetime import datetime
from typing import List
router = APIRouter(
    prefix="/turma",  # Prefix for all routes
    tags=["Turmas"],   # Tag for automatic documentation
)

engine = get_engine()

# Turmas
@router.post("/", response_model=Turma)
async def create_turma(nome: str, nivel: str, tutor_id: str):
    # Busca o tutor pelo ID
    tutor = await engine.find_one(Tutor, Tutor.id == ObjectId(tutor_id))
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor não encontrado")
    
    # Cria o TutorEmbed com os dados do tutor
    tutor_embed = TutorEmbed(
        nome=tutor.nome,
        email=tutor.email,
        lingua=tutor.lingua,
        id=tutor.id
    )
    
    # Cria a nova turma
    turma = Turma(
        nome=nome,
        nivel=nivel,
        tutor=tutor_embed,
        aluno=[],
        conversation=[]
    )
    
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

#@router.get("/{turma_id}/aluno/quantidade", response_model=dict)
#async def get_total_alunos_for_turma(turma_id: str):
    #turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    #if not turma:
        #raise HTTPException(status_code=404, detail="Turma not found")
    #total_alunos = len(turma.aluno)
    #return {"total_alunos": total_alunos}

@router.get("/aluno/por_turma")
async def get_alunos_por_turma():
    """ Retorna a quantidade de alunos por turma
        Faz um lookup na coleção de aluno para contar a quantidade de alunos por turma
        mostra em ordem crescente por nome da turma nivel e total de alunos
    """
    collection = engine.get_collection(Turma)
    pipeline = [
        {
            "$lookup": {
                "from": "aluno",
                "localField": "_id",
                "foreignField": "turma_id",
                "as": "aluno"
            }
        },
        {
            "$addFields": {
                "total_alunos": {"$size": "$aluno"}
            }
        },
                {
            "$lookup": {
                "from": "tutor",
                "localField": "tutor",
                "foreignField": "_id",
                "as": "tutor"
            }
        },
        {
            "$unwind": "$tutor"
        },
        {
            "$project": {
                "_id": {"$toString": "$_id"},
                "nome": 1,
                "nivel": 1,
                "lingua": "$tutor.lingua",
                "total_alunos": 1
            }
        }
    ]
    turmas = await collection.aggregate(pipeline).to_list(length=None)
    
    turmas =[
    {
        "id": turma["_id"],
        "nome": turma["nome"],
        "nivel": turma["nivel"],
        "lingua": turma["lingua"],
        "total_alunos": turma["total_alunos"]
    } 
    for turma in turmas
    ]
    
    return turmas

@router.delete("/{turma_id}")
async def delete_turma(turma_id: str):
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    await engine.delete(turma)
    return {"ok": True}


# Conversations
@router.post("/{turma_id}/conversations/")
async def create_conversation_for_turma(turma_id: str, nome: str, data_horario: str):
    # Converte a string "DD MM AAAA HH MM SS" para datetime
    try:
        data_horario_dt = datetime.strptime(data_horario, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de data inválido. Use 'DD-MM-AAAA HH MM SS'"
        )

    # Busca a turma
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    
    # Cria a conversa
    conversation = Conversation(nome=nome, data_horario=data_horario_dt)
    
    # Adiciona a conversa à turma
    turma.conversation.append(conversation)
    await engine.save(turma)
    
    return conversation

@router.get("/{turma_id}/conversations/", response_model=List[Conversation])
async def read_conversations_for_turma(turma_id: str):
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    return turma.conversations

@router.get("/{turma_id}/conversations/data", response_model=List[Conversation])
async def get_conversations_por_intervalo(
    turma_id: str,
    start_date: str = Query(..., description="Data de início no formato 'DD-MM-AAAA HH:MM:SS'"),
    end_date: str = Query(..., description="Data de fim no formato 'DD-MM-AAAA HH:MM:SS'")
):
    # Converte as strings "DD-MM-AAAA HH:MM:SS" para datetime
    try:
        start_date_dt = datetime.strptime(start_date, "%d-%m-%Y %H:%M:%S")
        end_date_dt = datetime.strptime(end_date, "%d-%m-%Y %H:%M:%S")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de data inválido. Use 'DD-MM-AAAA HH:MM:SS'"
        )

    # Busca a turma
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    
    # Filtra as conversas pelo intervalo de datas
    conversations = [
        conv for conv in turma.conversation
        if start_date_dt <= conv.data_horario <= end_date_dt
    ]
    
    if not conversations:
        raise HTTPException(
            status_code=404,
            detail="No conversations found in this date range for the specified turma"
        )
    
    return conversations




@router.put("/{turma_id}/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation_for_turma(turma_id: str, conversation_id: str, conversation_data: dict):
    # Busca a turma
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    
    # Busca a conversa
    conversation = next((conv for conv in turma.conversations if str(conv.id) == conversation_id), None)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Atualiza os campos da conversa
    for key, value in conversation_data.items():
        if key == "data_horario":
            try:
                # Converte a string "DD-MM-AAAA HH:MM:SS" para datetime
                value = datetime.strptime(value, "%d-%m-%Y %H:%M:%S")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Formato de data inválido. Use 'DD-MM-AAAA HH:MM:SS'"
                )
        setattr(conversation, key, value)
    
    await engine.save(turma)
    return conversation


@router.delete("/{turma_id}/conversations/{conversation_id}")
async def delete_conversation_for_turma(turma_id: str, conversation_id: str):
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    conversation = next((conv for conv in turma.conversations if str(conv.id) == conversation_id), None)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    turma.conversations.remove(conversation)
    await engine.save(turma)
    return {"ok": True}