import os
from fastapi import FastAPI, UploadFile, File
import sqlite3
import json
import random
import string

app = FastAPI()

# Function to generate a random string
def generate_random_string(length):
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to save uploaded file
def save_file(file, upload_folder):
    file_path = os.path.join(upload_folder, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return file_path

# Function to transform JSON file to SQLite database
def json_to_sqlite(file_path, conn, theme):
    random_string = generate_random_string(10)
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    cursor = conn.cursor()

    for question in data['questions']:
        string_list=json.dumps(question['options'],ensure_ascii=False)
        #dict_options={liste_python[0].strip():"option1",liste_python[1].strip():"option2",liste_python[2].strip():"option3",liste_python[3].strip():"option4"}
        lliste_python = string_list.strip('[]').replace('/','').split('", ')
        cursor.execute('''INSERT INTO quiz (question, option1,option2,option3,option4, answer, level,code_quiz,theme)
                        VALUES (?, ?, ?, ?,?,?,?,?,? )''',
                    (question['question'],
                        liste_python[0].replace('"', ''),
                        liste_python[1].replace('"', ''),
                        liste_python[2].replace('"', ''),
                        liste_python[3].replace('"', ''),
                        question['answer'].strip(),
                        question['level'],
                        random_string,
                        theme,
                        
                        )),



    conn.commit()

@app.post("/prompt/")
async def upload_file(file: UploadFile = File(...)):
    base_folder = "/Users/akmadou/Desktop/Quiz/data"
    
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    
    file_path = save_file(file, base_folder)  # Save the file directly to the base folder
    
    # Preprocess theme
    filename = file.filename
    theme = os.path.splitext(filename)[0]  # Get the theme from the filename
    
    # Transform JSON file to SQLite database
    conn = sqlite3.connect('/Users/akmadou/Desktop/Quiz/data/quiz.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS quiz (
                        id INTEGER PRIMARY KEY,
                        question TEXT,
                        option1 TEXT,
                        option2 TEXT,
                        option3 TEXT,
                        option4 TEXT,
                        answer TEXT,
                        level TEXT,
                        code_quiz TEXT,
                        theme TEXT
                    )''')
    
    json_to_sqlite(file_path, conn, theme)  # Pass the theme as an argument
    
    conn.close()
    
    return {"filename": filename, "path": file_path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
