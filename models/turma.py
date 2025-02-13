from pydantic import BaseModel, Field
from typing import Optional, List

class Conversation(BaseModel):
    name: str
    date: str

class Turma(BaseModel):
    nome: str
    nivel: str
    tutor_id: str
    aluno_ids: List[str] = []

class TurmaInDB(Turma):
    id: Optional[str] = Field(default=None, alias='_id')

    class Config:
        allow_population_by_field_name = True