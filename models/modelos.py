from odmantic import Model, Reference, ObjectId

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
    tutor: Tutor = Reference()
    
    
class Turma(Model):
    nome: str
    nivel: str
    conversaton: list[datetime]
    tutor: Tutor = Reference()
    aluno: list[Aluno] = []


