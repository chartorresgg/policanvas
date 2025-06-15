import os
import json
import sys
import csv
import pandas as pd
import requests
from colorama import Fore, Back, Style, init

init(autoreset=True)  # reset the previous color and style after each line
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN') # ID Token from Canvas and Local Variables
api_url = f'https://poli.instructure.com/api/v1/' #Encabezado de la página de API en Canvas.

def get_function(url='', payload={}, token='', verbose=True):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get(url, headers=headers, data=payload)
    if verbose:
        if r.status_code == 200:
            color = Fore.GREEN
        else:
            color = Fore.RED
        print(color + f'{r.status_code} >> {r.reason}')
    if r.status_code == 200:
       return r
    else:
        return None

# COURSE USERS
course_id = 55595

# OBTENER HISTORIAL
# url = api_url+f'courses/{course_id}/users?page=1&per_page=5'
url = api_url + f'courses/{course_id}/users?per_page=100'
payload = {
    'sort': 'email',
    'enrollment_type': 'teacher' #El rol de Operador también se cuenta como un docente.

}
r = get_function(url, payload=payload, token=ACCESS_TOKEN, verbose=False)
response = r.json()
print(json.dumps(response, indent=2)) #Imprimer los resultados encontrados
print(len(response)) #Imprime la cantidad de resultados encontrados en el response.

#Instrucción para visualizar los datos en una tabla
df = pd.DataFrame(response)
df
print(df)