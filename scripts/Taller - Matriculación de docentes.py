import pandas as pd
import os
import requests
import json
from colorama import Fore, Back, Style, init

#Definición del Access Token
init(autoreset=True)
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
api_url = f'https://poli.instructure.com/api/v1/'

#Se define la cuenta en la que se crean los cursos (20 = Z-Histórico)
api_url = f'https://poli.instructure.com/api/v1/'
account_id = 20
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}" #Autorización en Canvas del Access Token
}

#Impresión en color de los códigos de Status de las llamadas
def prin_status_response(r):
    if r.status_code == 200:
        color = Fore.GREEN
    else:
        color = Fore.RED
    print(color + f'{r.status_code} >> {r.reason}')

#Lectura del archivo Grupos por Franja
df = pd.read_excel('GruposPorFranja.xlsx')
df.head()

#Matriculación de los usuarios (Docentes)
for id_curso, id_usuario in df.iterrows():
    payload = {
        "enrollment[user_id]": id_usuario,
        "enrollment[role_id]": 4,
        "enrollment[enrollment_state]": "active"
    }

    url = f'{api_url}/courses/{id_curso}/enrollments'
    r = requests.post(url, headers=headers, data=payload)

    if r.status_code == 200:
        response = r.json()
        mat_id = response["id"]
        with open('log_matriculas.txt', 'a') as archivo:
            archivo.write(f"1, {id_usuario} -matriculado en- {id_curso}, codigo {mat_id}" + '\n')
        print(f'Usuario {id_usuario} matriculado {id_curso}')
    else:
        with open('log_matriculas.txt', 'a') as archivo:
            archivo.write(f"0, {id_usuario} - NO matriculado en - {id_curso}" + '\n')