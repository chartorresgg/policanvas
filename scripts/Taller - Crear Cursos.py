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

list(df.NOMBRE_CURSO)
lista_cursos = list(dict.fromkeys(list(df.NOMBRE_CURSO)))
print(len(lista_cursos))
#lista_cursos


source_course_id = 63645
for index, row in df.iterrows():
    curso = row['NOMBRE_CURSO']
    sis_course_id = row['ID SIS']

    url = f'{api_url}accounts/{account_id}/courses'
    payload = {
        "course[name]": curso,
        "course[course_code]": curso,
        "course[sis_course_id]": sis_course_id,
        "course[enroll_me]": "true",
        "course[term_id]": 818,
        "offer": "true",
        "enroll_me": "true"
    }

    r = requests.post(url=url, headers=headers, data=payload)  # Llamada realizada a Canvas(Get, Put, Post & Delete)
    prin_status_response(r)

    #Almacenar en el txt, el id y el nombre de los cursos creados
    if r.status_code == 200:
        response = r.json()
        course_id = response["id"]
        with open('archivo.txt', 'a') as archivo:
            archivo.write(f"{curso}, {course_id}" + '\n')
        print(f'Curso creado: {curso} - {course_id}')

    #Se define el curso a importar y el método de importación
    course_id= response["id"]
    url = f'{api_url}courses/{course_id}/content_migrations'
    payload = {
        "migration_type": "course_copy_importer",
        "settings[source_course_id]": str(source_course_id)
    }

    r= requests.post(url=url, headers=headers, data=payload)
    prin_status_response(r)
    if r.status_code == 200:
        response = r.json()
        print(json.dumps(response, indent=2))
