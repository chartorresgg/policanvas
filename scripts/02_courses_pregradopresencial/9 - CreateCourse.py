import os
import requests
import json
from colorama import Fore, init

init(autoreset=True)  # reset the previous color and style after each line
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
api_url = f'https://poli.instructure.com/api/v1/'

def prin_status_response(r):
    if r.status_code == 200:
        color = Fore.GREEN
    else:
        color = Fore.RED
    print(color + f'{r.status_code} >> {r.reason}')

api_url = f'https://poli.instructure.com/api/v1/'
account_id = 1
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

source_course_id = 6275
for n in range(4):
    url = f'{api_url}accounts/{account_id}/courses'
    payload = {
        "course[name]": f"MODULO DE INDUCCION VIRTUAL-[GRUPO {n+1}]",
        "course[course_code]": f"MODULO DE INDUCCION VIRTUAL-[GRUPO {n+1}]",
        #"course[sis_course_id]": ,
        #"course[term_id]": 818,
        #"workflow_state": "available",
        #"course[is_public]": "true",
        #"course[is_public_to_auth_users]": "true",
        "course[enroll_me]": "true",
        "offer": "true",
        "enroll_me": "true"
    }

    r = requests.post(url=url, headers=headers, data=payload) #Llamada realizada a Canvas(Get, Put, Post & Delete)
    prin_status_response(r)

    if r.status_code == 200:
        response = r.json()
        course_id = response["id"]
        print(f'Curso creado, id: {response["id"]}')

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