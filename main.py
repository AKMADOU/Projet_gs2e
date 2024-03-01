from fastapi import FastAPI, Query, UploadFile, File, Form
from typing import List
from pydantic import BaseModel
import fitz
import os
import glob
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import shutil
from fastapi.middleware.cors import CORSMiddleware

# Define Pydantic models for API inputs and outputs
class CVMatch(BaseModel):
    resume_path: str
    nom:str
    nom_cv:str
    match_percentage: float

# Initialize FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vous pouvez remplacer "*" par la liste des domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to read the contents of a PDF file
def read_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf_document:
        num_pages = pdf_document.page_count
        for page_num in range(num_pages):
            page = pdf_document[page_num]
            text += page.get_text()
    return text

# Function to calculate similarity between CVs and job description
def cv_similarity(resume_folder: str, job_path: str, keywords: str, threshold: float = 45.0) -> List[CVMatch]:
    resume_paths = glob.glob(os.path.join(resume_folder, "*.pdf"))
    job_text = read_pdf(job_path.strip())

    matches_above_threshold = []

    for resume_path in resume_paths:
        resume_text = read_pdf(resume_path.strip())

        contains_keywords = any(keyword.lower() in resume_text.lower() for keyword in keywords.split(','))
        if not contains_keywords:
            continue

        text = [resume_text, job_text]

        cv = CountVectorizer()
        count_matrix = cv.fit_transform(text)

        match_percentage = cosine_similarity(count_matrix[0], count_matrix[1])[0][0] * 100
        match_percentage = round(float(match_percentage), 2)

        if match_percentage > threshold:
            matches_above_threshold.append(CVMatch(resume_path=resume_path,nom=resume_path.split('/')[-1].split('.')[0],nom_cv=resume_path.split('/')[-1], match_percentage=match_percentage))

    return matches_above_threshold

# Function to move files based on similarity threshold
def move_files(matches: List[CVMatch], target_directory: str, threshold: float):
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    for match in matches:
        resume_path, match_percentage = match.resume_path, match.match_percentage
        filename = os.path.basename(resume_path)
        destination_directory = target_directory

        destination_path = os.path.join(destination_directory, filename)
        shutil.copy(resume_path, destination_path)
        print(f"CV '{filename}' with similarity of {match_percentage}% copied to '{destination_directory}'")

# Endpoint to get similarity matches
@app.post("/cv/match/")
def get_cv_matches(resume_folder: str = Query(..., description="Chemin du dossier contenant les CV"),
                   job_path: str = Query(..., description="Chemin du fichier de description du poste"),
                   keywords: str = Query(..., description="Liste de mots-clés pour le filtrage initial (séparés par des virgules)"),
                   threshold: float = Query(45.0, description="Seuil de similarité en pourcentage")) -> List[CVMatch]:
    matches_above_threshold = cv_similarity(resume_folder, job_path, keywords, threshold)
    
    # Définir le répertoire de destination sur le répertoire 'tri_cv' créé dans le répertoire principal
    tri_cv_folder = os.path.join(os.path.dirname(resume_folder), 'tri_cv')
    
    move_files(matches_above_threshold, tri_cv_folder, threshold)
    
    return matches_above_threshold

# Function to save uploaded file
def save_file(file, upload_folder):
    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return file_path

# Endpoint to upload file
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), title: str = Form(...)):
    base_folder = "/Users/akmadou/Desktop/Quiz/uploads"
    upload_folder = os.path.join(base_folder, title)
    
    # Create the main directory
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Create description, cv, and tri_cv directories in the main directory
    description_folder = os.path.join(upload_folder, "description")
    cv_folder = os.path.join(upload_folder, "cv")
    tri_cv_folder = os.path.join(upload_folder, "tri_cv")
    
    # Check if directories exist before creating them
    try:
        os.makedirs(description_folder)
        os.makedirs(cv_folder)
        os.makedirs(tri_cv_folder)
    except FileExistsError:
        pass
    
    # Save the file in the cv directory
    file_path = save_file(file, cv_folder)
    
    return {"filename": file.filename, "title": title, "path": file_path}

# Run the API with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

