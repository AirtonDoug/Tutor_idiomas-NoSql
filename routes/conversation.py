from fastapi import APIRouter, HTTPException
from database import get_engine
from models.modelos import Turma, Conversation
from odmantic import ObjectId
from datetime import datetime

router = APIRouter(
    prefix="/conversation",  # Prefix for all routes
    tags=["Conversations"],   # Tag for automatic documentation
)

engine = get_engine()

@router.post("/{turma_id}/conversation/", response_model=Conversation)
async def create_conversation_for_turma(turma_id: str, conversation: Conversation):
    existing_conversation = await engine.find_one(Conversation, Conversation.name == conversation.name)
    if existing_conversation:
        conversation = existing_conversation
    else:
        await engine.save(conversation)
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    turma.conversations.append(conversation)
    await engine.save(turma)
    return conversation

@router.get("/{turma_id}/conversation/", response_model=list[Conversation])
async def read_conversations_for_turma(turma_id: str):
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    return turma.conversations

@router.get("/{turma_id}/conversations/data", response_model=list[Conversation])
async def get_conversations_por_intervalo(turma_id: str, start_date: datetime, end_date: datetime):
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    conversations = [conv for conv in turma.conversations if start_date <= conv.date <= end_date]
    if not conversations:
        raise HTTPException(status_code=404, detail="No conversations found in this date range for the specified turma")
    return conversations

@router.put("/{turma_id}/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation_for_turma(turma_id: str, conversation_id: str, conversation_data: dict):
    conversation = await engine.find_one(Conversation, Conversation.id == ObjectId(conversation_id))
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    for key, value in conversation_data.items():
        setattr(conversation, key, value)
    await engine.save(conversation)
    return conversation

@router.delete("/{turma_id}/conversations/{conversation_id}")
async def delete_conversation_for_turma(turma_id: str, conversation_id: str):
    turma = await engine.find_one(Turma, Turma.id == ObjectId(turma_id))
    if not turma:
        raise HTTPException(status_code=404, detail="Turma not found")
    conversation = await engine.find_one(Conversation, Conversation.id == ObjectId(conversation_id))
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    turma.conversations.remove(conversation)
    await engine.save(turma)
    await engine.delete(conversation)
    return {"ok": True}