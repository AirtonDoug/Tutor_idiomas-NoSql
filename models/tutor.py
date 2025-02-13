from pydantic import BaseModel, Field
from typing import Optional, List

class Tutor(BaseModel):
    nome: str
    email: str
    lingua: str
    turma_ids: List[str] = []

class TutorInDB(Tutor):
    id: Optional[str] = Field(default=None, alias='_id')

    class Config:
        allow_population_by_field_name = True