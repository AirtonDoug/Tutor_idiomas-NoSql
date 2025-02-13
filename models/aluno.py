from pydantic import BaseModel, Field
from typing import Optional, List

class Aluno(BaseModel):
    nome: str
    email: str
    nickname: str
    senha: str
    turma_ids: List[str] = []

class AlunoInDB(Aluno):
    id: Optional[str] = Field(default=None, alias='_id')

    class Config:
        allow_population_by_field_name = True