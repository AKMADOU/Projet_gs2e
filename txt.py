

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
# Définir la base de données SQLite et créer une session
SQLALCHEMY_DATABASE_URL = "sqlite:///./quiz.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Définition de la table Quiz
class Quiz(Base):
    __tablename__ = "quiz"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    option1 = Column(Text)
    option2 = Column(Text)
    option3 = Column(Text)
    option4 = Column(Text)
    answer = Column(String)
    level = Column(String)
    code_quiz = Column(String)
    theme = Column(String)

# Création de la base de données
Base.metadata.create_all(bind=engine)

# Création de la classe Pydantic pour la validation des données de sortie
class QuizOut(BaseModel):
    question: str
    option1: str
    option2: str
    option3: str
    option4: str
    answer: str
    level: str
    code_quiz: str
    theme: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vous pouvez remplacer "*" par la liste des domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Définition de la route pour obtenir un quiz par son code
@app.post("/quiz/{code}")
def get_quiz_by_code(code: str):
    db = SessionLocal()
    quiz = db.query(Quiz).filter(Quiz.code_quiz == code).all()
    db.close()
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_dicts = [{"question": q.question, "option1": q.option1, "option2": q.option2, "option3": q.option3,
                   "option4": q.option4, "answer": q.answer, "level": q.level, "code_quiz": q.code_quiz,
                   "theme": q.theme} for q in quiz]    
    return quiz_dicts 
# @app.get("/quiz/{code}", response_model=List[QuizOut])
# def get_quiz_by_code(code: str):
#     db = SessionLocal()
#     quiz = db.query(Quiz).filter(Quiz.code_quiz == code).all()
#     db.close()
#     if not quiz:
#         raise HTTPException(status_code=404, detail="Quiz not found")
#     # Convertir les objets Quiz en dictionnaires JSON
#     quiz_dicts = [{"question": q.question, "option1": q.option1, "option2": q.option2, "option3": q.option3,
#                    "option4": q.option4, "answer": q.answer, "level": q.level, "code_quiz": q.code_quiz,
#                    "theme": q.theme} for q in quiz]
#     return quiz_dicts
@app.get("/quiz_theme/{theme}")
def get_quiz_by_code(theme: str):
    db = SessionLocal()
    quiz = db.query(Quiz).filter(Quiz.theme == theme).all()
    db.close()
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz    

# Définition de la route pour créer un nouveau quiz
@app.post("/quiz/")
def create_quiz(quiz: QuizOut):
    db = SessionLocal()
    db_quiz = Quiz(**quiz.dict())
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    db.close()
    return {"detail": "Quiz created successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
