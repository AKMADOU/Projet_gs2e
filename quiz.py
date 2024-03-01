import openai

def generatetext(cle):
    openai.api_key = cle

    # Lecture du thème à partir du fichier theme.txt
    with open("theme.txt", "r") as theme_file:
        theme = theme_file.read().strip()

    # Envoyer une requête à OpenAI pour générer un texte de type quiz
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=f"Rédigez un quiz de 10 questions sur les thèmes suivants: {theme}. Chaque question doit avoir 4 choix de réponse et une seule bonne réponse.",
        temperature=0.7,
        max_tokens=1000,
    )

    # Extraction du texte du quiz de la réponse
    quiz_text = response["choices"][0]["text"]

    # Split du texte du quiz par ligne
    lines = quiz_text.split('\n')
    formatted_lines = []

    # Parcourir les lignes du texte du quiz pour ajouter chaque bonne réponse à côté du choix de réponse correspondant
    for i in range(len(lines)):
        if lines[i].startswith('Réponse:'):
            # Formater la ligne avec la bonne réponse collée au choix de réponse correspondant
            formatted_lines[-1] = formatted_lines[-1].rstrip() + f' (Bonne réponse: {lines[i].split(":")[-1].strip()})'
        else:
            formatted_lines.append(lines[i])

    # Joindre les lignes formatées pour former le texte final du quiz
    formatted_quiz_text = '\n'.join(formatted_lines)

    # Chemin du fichier dans lequel vous voulez enregistrer le quiz
    file_path = "quiz.txt"

    # Écriture du contenu du quiz dans le fichier texte
    with open(file_path, "w") as file:
        file.write(formatted_quiz_text)
        
    return "ok"

# Appel de la fonction en fournissant la clé d'API OpenAI
generatetext("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")
