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

# Show information about the ID User in Canvas.
user_id = 149814 #ID del perfil en Canvas.
url = api_url+f'users/{user_id}/profile' #Concatenación de la URL que se usará para extraer la información
r = get_function(url, token=ACCESS_TOKEN) #Accede a la función get_function con la URL y el Token, y recupere la información.
response = r.json() #Al recuperar la información, se almacena en la variable r y se convierte en formato JSon
print(json.dumps(response, indent=2)) #Se imrprime la información

df = pd.DataFrame(response)
df.to_excel(f'profile_{user_id}.xlsx', index=False)