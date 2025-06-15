import os
import requests
import json
import pandas as pd
from colorama import Fore, Back, Style, init

init(autoreset=True)  # reset the previous color and style after each line
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

api_url = f'https://poli.instructure.com/api/v1/'
course_id = '63898'             # Reemplaza con el ID del curso
quiz_id = '140512'
url = f'{api_url}courses/{course_id}/quizzes/{quiz_id}/questions'

account_id = 1
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def prin_status_response(r):
    if r.status_code == 200:
        color = Fore.GREEN
    else:
        color = Fore.RED
    print(color + f'{r.status_code} >> {r.reason}')

# Hacer la solicitud GET
response = requests.get(url, headers=headers)

# Verificar la respuesta
if response.status_code == 200:
    questions = response.json()
    for question in questions:
        print(f"Pregunta: {question['question_text']}")
        print("Opciones:")
        for answer in question.get('answers', []):
            print(f"- {answer['text']}")
else:
    print(f"Error: {response.status_code} - {response.text}")

    