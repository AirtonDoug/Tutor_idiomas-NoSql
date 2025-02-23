from odmantic import Model, Reference, ObjectId
from typing import Optional, List
from datetime import datetime


class Tutor(Model):
    nome: str
    email: str
    lingua: str
    
class Aluno(Model):
    nome: str
    email: str
    senha: str
    nickname: str
    tutor_id: Optional[ObjectId] = None  # Mudamos para tutor_id
    turma_id: Optional[ObjectId] = None  # Mudamos para turma_id

class Conversation(Model):
    nome: str
    data_horario: datetime
 
    
class Turma(Model):
    nome: str
    nivel: str
    conversation: List[Conversation] = []
    tutor: Tutor = Reference()
    aluno: List[Aluno] = []