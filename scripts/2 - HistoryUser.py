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

# USER HISTORY
# OBTENER ID DEL USUARIO
url = api_url+f'users/self/profile'
r = get_function(url, token=ACCESS_TOKEN, verbose=False)
response = r.json()
user_id = 149814

# OBTENER HISTORIAL DEL ID USUARIO ANTERIOR
url = api_url+f'users/{user_id}/history'
r = get_function(url, token=ACCESS_TOKEN, verbose=False)
response = r.json()
print(json.dumps(response, indent=2))