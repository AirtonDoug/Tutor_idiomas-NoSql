from fastapi import FastAPI
from routes.aluno import router as aluno_router
from routes.turma import router as turma_router
from routes.tutor import router as tutor_router

app = FastAPI()

# Incluindo as rotas de aluno, turma e tutor
app.include_router(aluno_router, prefix="/alunos", tags=["alunos"])
app.include_router(turma_router, prefix="/turmas", tags=["turmas"])
app.include_router(tutor_router, prefix="/tutors", tags=["tutors"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Tutor Idiomas NoSQL API"}