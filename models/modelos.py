from odmantic import Model, Reference, ObjectId, EmbeddedModel
from typing import Optional, List
from datetime import datetime


class TutorEmbed(EmbeddedModel):
    nome: str
    email: str
    lingua: str
    id: ObjectId

class Tutor(Model):
    nome: str
    email: str
    lingua: str
    
class Aluno(Model):
    nome: str
    email: str
    senha: str
    nickname: str
    tutor_id: Optional[ObjectId] = None  
    turma_id: Optional[ObjectId] = None  

class Conversation(Model):
    nome: str
    data_horario: datetime
 
    
class Turma(Model):
    nome: str
    nivel: str
    conversation: List[Conversation] = []
    tutor: TutorEmbed  # Usando o modelo embutido
    aluno: List[Aluno] = []