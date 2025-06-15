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

course_id = 55595 #ID del curso
url = api_url + f'courses/{course_id}/users?per_page=100'
payload = {
    'sort': 'email',
    # 'enrollment_type': 'student'
}
r = get_function(url, payload=payload, token=ACCESS_TOKEN, verbose=False)
response = r.json()
links = r.links

n = 2

while links.get('next') is not None:
    url = r.links['next']['url']
    r = get_function(url, payload=payload, token=ACCESS_TOKEN, verbose=False)
    response += r.json()
    links = r.links
    n += 1

print(f'Se exportaron {n - 1} páginas\n'
      f'total usuarios: {len(response)}')

# Crear DataFrame
df = pd.DataFrame(response)
df.to_excel(f'usuarios_{course_id}.xlsx', index=False)