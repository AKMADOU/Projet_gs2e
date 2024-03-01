import sqlite3
import json
import random
import string
# Charger les données depuis le fichier JSON
liste_python=[]
#dict_options={}
file='/Users/akmadou/Desktop/Quiz/data/data_science.json'
theme=file.split("/")[-1].split(".")[0]



def generate_random_string(length):
    """Génère une chaîne aléatoire de longueur spécifiée."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Exemple d'utilisation
random_string = generate_random_string(10)
with open(file, 'r') as f:
    data = json.load(f)

# Créer une connexion à la base de données SQLite (si le fichier n'existe pas, il sera créé)
conn = sqlite3.connect('quiz.db')
cursor = conn.cursor()

# Créer une table pour stocker les questions et les réponses
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

# Insérer les données dans la table
for question in data['questions']:
    string_list=json.dumps(question['options'],ensure_ascii=False)
    #dict_options={liste_python[0].strip():"option1",liste_python[1].strip():"option2",liste_python[2].strip():"option3",liste_python[3].strip():"option4"}
    liste_python = string_list.strip('[]').replace('"', '').replace('/','').split(', ')
    cursor.execute('''INSERT INTO quiz (question, option1,option2,option3,option4, answer, level,code_quiz,theme)
                      VALUES (?, ?, ?, ?,?,?,?,?,? )''',
                   (question['question'],
                    liste_python[0],
                    liste_python[1],
                    liste_python[2],
                    liste_python[3],
                    question['answer'].strip(),
                    question['level'],
                    random_string,
                    theme,
                    
                    )),

# Valider les modifications et fermer la connexion
conn.commit()
conn.close()