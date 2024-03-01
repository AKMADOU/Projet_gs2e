# import json
# def questions_to_json(file_path):
#     json_structure = []

#     with open(file_path, "r", encoding="utf-8") as file:
#         question_text = ""
#         for line in file:
#             if line.strip():  # Vérifier si la ligne n'est pas vide
#                 question_text += line
#             else:
#                 # Si la ligne est vide, traiter la question actuelle
#                 if question_text:
#                     question_dict = parse_question(question_text)
#                     json_structure.append(question_dict)
#                     question_text = ""

#         # Traiter la dernière question si le fichier ne se termine pas par une ligne vide
#         if question_text:
#             question_dict = parse_question(question_text)
#             json_structure.append(question_dict)

#     return json.dumps(json_structure, indent=4, ensure_ascii=False)

# def parse_question(question_text):
#     # Séparer la question et les choix
#     parts = question_text.split("\n")
#     question = parts[0].strip()
#     choices = [part.strip() for part in parts[1:] if part.strip()]

#     # Extraire la réponse
#     if choices:
#         answer_part = choices.pop(-1).split(":")
#         if len(answer_part) > 1:
#             answer = answer_part[-1].strip()
#         else:
#             answer = "Pas de réponse fournie"
#     else:
#         answer = "Pas de réponse fournie"

#     # Formater les choix
#     formatted_choices = [choice.replace(answer, answer.strip(), 1) for choice in choices]

#     return {
#         "question": question,
#         "choices": formatted_choices,
#         "answer": answer
#     }


# # Chemin du fichier contenant les questions
# input_file_path = "quiz.txt"

# # Convertir les questions en format JSON
# json_result = questions_to_json(input_file_path)

# # Écriture du contenu JSON dans un fichier
# output_file_path = "questions100.json"
# with open(output_file_path, "w", encoding="utf-8") as json_file:
#     json_file.write(json_result)

# print("Le fichier JSON a été créé avec succès.")

# from fastapi import FastAPI

# # Créer une instance de l'application FastAPI
# app = FastAPI()

# # Définir une route avec un seul paramètre en tant que chaîne de caractères
# @app.get("/theme/{theme_name}")
# async def get_theme(theme_name: str):
#     return {"theme_name": theme_name}

# from fastapi import FastAPI
# import os

# # Créer une instance de l'application FastAPI
# app = FastAPI()

# # Chemin du fichier pour stocker theme_name
# file_path = "theme.txt"

# # Fonction pour stocker theme_name dans un fichier
# def store_theme_name(theme_name: str):
#     with open(file_path, "w") as file:
#         file.write(theme_name)

# # Fonction pour récupérer theme_name depuis un fichier
# def get_theme_name():
#     if os.path.exists(file_path):
#         with open(file_path, "r") as file:
#             return file.read()
#     else:
#         return None

# # Définir une route avec un seul paramètre en tant que chaîne de caractères
# @app.get("/theme/{theme_name}")
# async def get_theme(theme_name: str):
#     # Stocker le theme_name
#     store_theme_name(theme_name)
#     return {"theme_name": theme_name}

# # Route pour récupérer le theme_name stocké
# @app.get("/current_theme")
# async def current_theme():
#     theme_name = get_theme_name()
#     return {"current_theme": theme_name}



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
@app.get("/quiz/{code}")
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
