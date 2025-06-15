import os
import requests
import json
import pandas as pd
from colorama import Fore, Back, Style, init

# Configuración
init(autoreset=True)  # reset the previous color and style after each line
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
api_url = f'https://poli.instructure.com/api/v1/'

account_id = 208
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def prin_status_response(r):
    if r.status_code == 200:
        color = Fore.GREEN
    else:
        color = Fore.RED
    print(color + f'{r.status_code} >> {r.reason}')


df = pd.read_excel('GruposPorFranja.xlsx') # Leer el archivo de excel
df.head() # Mostrar las primeras 5 filas del archivo

list(df.NOMBRE_CURSO) # Mostrar la columna de los cursos
lista_cursos = list(dict.fromkeys(list(df.NOMBRE_CURSO))) # Eliminar duplicados
print(len(lista_cursos))
lista_cursos

source_course_id = 65022
for index, row in df.iterrows():
    curso = row['NOMBRE_CURSO']
    sis_course_id = row['ID SIS'][:25]
    print(sis_course_id)

    url = f'{api_url}accounts/{account_id}/courses'
    print(url)
    payload = {
        "course[name]": curso,
        "course[course_code]": curso,
        "course[sis_course_id]": sis_course_id,
        "course[enroll_me]": "false",
        "course[term_id]": 1138,
        "offer": "true",
        #"enroll_me": "true"
    }

    r = requests.post(url=url, headers=headers, data=payload)  # Llamada realizada a Canvas(Get, Put, Post & Delete)
    prin_status_response(r)

    # Almacenar en el txt, el id y el nombre de los cursos creados
    if r.status_code == 200:
        response = r.json()
        course_id = response["id"]
        with open('../archivo.txt', 'a') as archivo:
            archivo.write(f"{curso}, {course_id}" + '\n')
        print(f'Curso creado: {curso} - {course_id}')


    url = f'{api_url}courses/{course_id}/content_migrations'
    payload = {
        "migration_type": "course_copy_importer",
        "settings[source_course_id]": str(source_course_id)
    }

    r = requests.post(url=url, headers=headers, data=payload)
    prin_status_response(r)
    if r.status_code == 200:
        response = r.json()
        print(json.dumps(response, indent=2))