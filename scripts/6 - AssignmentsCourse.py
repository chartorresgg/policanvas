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

#List of assignments in the course
id_course = 67954
url = f"{api_url}courses/{id_course}/assignments?per_page=80"
r = get_function(url=url, token=ACCESS_TOKEN, verbose=True)
response = r.json()
print(json.dumps(response, indent=2))
print(f"Total de actividades: {len(response)}")

df = pd.DataFrame(response)
df.to_excel(f'assignments{id_course}.xlsx', index=False, columns=["id","name","unlock_at","lock_at"])