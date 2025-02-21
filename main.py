from fastapi import FastAPI
from routes import aluno, turma, tutor

# FastAPI app instance
app = FastAPI()

# Rotas para Endpoints
app.include_router(aluno.router)
app.include_router(turma.router)
app.include_router(tutor.router)