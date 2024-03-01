# import openai

# # Remplacer "YOUR_API_KEY" par votre clé API OpenAI
# # openai.api_key ="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"
# openai.api_key ="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"

# # Définir la thématique du quiz
# theme = "Data Science,Economie"

# # Envoyer une requête à OpenAI pour générer un texte de type quiz
# response = openai.Completion.create(
#     engine="gpt-3.5-turbo-instruct",
#     prompt=f"Rédigez un quiz de 10 questions de 3 niveaux de difficulté, à savoir facile (1), moyen (2), et difficile (3), sur le thème {theme}. Chaque question doit avoir 4 choix de réponse et une seule bonne réponse.",
#     temperature=0.7,
#     max_tokens=1000,
# )

# # Extraire le texte du quiz de la réponse
# quiz_text = response["choices"][0]["text"]

# # Définir le chemin du fichier où vous souhaitez enregistrer le texte du quiz
# file_path = "quiz_text4.txt"

# # Écrire le contenu du quiz dans le fichier texte
# with open(file_path, "w") as file:
#     file.write(quiz_text)

# print("Le texte du quiz a été enregistré avec succès dans", file_path)


import openai
import json

# Remplacer "YOUR_API_KEY" par votre clé API OpenAI
# openai.api_key ="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"
openai.api_key ="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"

# Définir la thématique du quiz
theme = "Data Science,Economie"

# Envoyer une requête à OpenAI pour générer un texte de type quiz
response = openai.Completion.create(
    engine="gpt-3.5-turbo-instruct",
    prompt=f"Rédigez un quiz de 10 questions de 3 niveaux de difficulté, à savoir facile (1), moyen (2), et difficile (3), sur le thème {theme}. Chaque question doit avoir 4 choix de réponse et une seule bonne réponse.",
    temperature=0.7,
    max_tokens=1000,
)

# Extraire le texte du quiz de la réponse
quiz_text = response["choices"][0]["text"]

# Initialiser la structure JSON
quiz_json = {
    "sujet": theme,
    "questions": []
}

# Diviser le texte du quiz en questions
questions = quiz_text.split("\n\n")

# Parcourir chaque question et extraire les informations nécessaires
for question in questions:
    # Diviser la question en question, options et réponse
    parts = question.split("\n")
    question_text = parts[0].strip()
    options = [option.strip() for option in parts[1:5]]
    # Vérifier si la question contient une réponse avant d'essayer d'accéder à parts[5]
    answer = parts[5].strip() if len(parts) > 5 else ""
    
    # Déterminer le niveau de difficulté de la question
    level = "1" if "facile" in question else ("2" if "moyen" in question else "3")
    
    # Ajouter les informations extraites à la structure JSON
    quiz_json["questions"].append({
        "question": question_text,
        "options": options,
        "answer": answer,
        "level": level
    })

# Enregistrer la structure JSON dans un fichier
with open("quiz_json.json", "w") as json_file:
    json.dump(quiz_json, json_file, indent=4)

print("Le fichier JSON a été créé avec succès.")



# import openai
# import fitz  # PyMuPDF pour traiter les fichiers PDF

# # Remplacer "YOUR_API_KEY" par votre clé API OpenAI
# openai.api_key = "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"

# # Fonction pour identifier le thème à partir du texte
# def identify_theme_from_text(text):
#     keywords = ["data", "science", "machine learning", "analytics", "statistics", "big data"]
#     theme_scores = {keyword: text.lower().count(keyword) for keyword in keywords}
#     identified_theme = max(theme_scores, key=theme_scores.get)
#     return identified_theme

# # Fonction pour extraire le texte d'un fichier PDF
# def extract_text_from_pdf(file_path):
#     text = ""
#     with fitz.open(file_path) as doc:
#         for page in doc:
#             text += page.get_text()
#     return text

# # Fonction pour générer un quiz en fonction du contenu du document
# def generate_quiz_from_pdf(file_path):
#     # Extraire le texte du fichier PDF
#     pdf_text = extract_text_from_pdf(file_path)
    
#     # Identifier le thème à partir du texte
#     theme = identify_theme_from_text(pdf_text)

#     # Envoyer une requête à OpenAI pour générer un texte de type quiz
#     response = openai.Completion.create(
#         engine="gpt-3.5-turbo-instruct",
#         prompt=f"Rédigez un quiz de 10 questions de 3 niveaux de difficulté, à savoir facile (1), moyen (2), et difficile (3), sur le thème {theme}, basé sur le contenu du document suivant :\n{pdf_text}\nChaque question doit avoir 4 choix de réponse et une seule bonne réponse.",
#         temperature=0.7,
#         max_tokens=1000,
#     )

#     # Extraire le texte du quiz de la réponse
#     quiz_text = response["choices"][0]["text"]
#     return quiz_text

# # Exemple : chemin du fichier PDF
# file_path = "/Users/akmadou/Desktop/Quiz/CV_avec_seuil_Inf%/ADOU_Kouame_Mathurin_CV.pdf"

# # Générer le quiz à partir du contenu du fichier PDF
# quiz_text = generate_quiz_from_pdf(file_path)

# # Définir le chemin du fichier où vous souhaitez enregistrer le texte du quiz
# output_file_path = "quiz_from_pdf.txt"

# # Écrire le contenu du quiz dans le fichier texte
# with open(output_file_path, "w", encoding="utf-8") as file:
#     file.write(quiz_text)

# print("Le texte du quiz a été enregistré avec succès dans", output_file_path)
