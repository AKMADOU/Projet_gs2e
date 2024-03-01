import json

def questions_to_json(file_path):
    json_structure = []

    with open(file_path, "r", encoding="utf-8") as file:
        question_text = ""
        for line in file:
            if line.strip():  # Vérifier si la ligne n'est pas vide
                question_text += line
            else:
                # Si la ligne est vide, traiter la question actuelle
                if question_text:
                    question_dict = parse_question(question_text)
                    json_structure.append(question_dict)
                    question_text = ""

        # Traiter la dernière question si le fichier ne se termine pas par une ligne vide
        if question_text:
            question_dict = parse_question(question_text)
            json_structure.append(question_dict)

    return json.dumps(json_structure, indent=4, ensure_ascii=False)

def parse_question(question_text):
    # Séparer la question et les choix
    parts = question_text.split("\n")
    question = parts[0].strip()
    choices = [part.strip() for part in parts[1:] if part.strip()]

    # Extraire la réponse
    if choices:
        answer_part = choices.pop(-1).split(":")
        if len(answer_part) > 1:
            answer = answer_part[-1].strip("\n")
        else:
            answer = "Pas de réponse fournie"
    else:
        answer = "Pas de réponse fournie"

    # Formater les choix
    formatted_choices = [choice.replace(answer, answer.strip(), 1) for choice in choices]

    return {
        "question": question,
        "options": formatted_choices,
        "answer": answer
    }


# Chemin du fichier contenant les questions
input_file_path = "quiz.txt"

# Convertir les questions en format JSON
json_result = questions_to_json(input_file_path)

# Écriture du contenu JSON dans un fichier
output_file_path = "quiz.json"
with open(output_file_path, "w", encoding="utf-8") as json_file:
    json_file.write(json_result)

print("Le fichier JSON a été créé avec succès.",output_file_path)
