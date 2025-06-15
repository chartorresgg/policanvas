import os
import requests
import json
import pandas as pd
from colorama import Fore, Back, Style, init

init(autoreset=True)
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
api_url = f'https://poli.instructure.com/api/v1/'
account_id = 20
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def prin_status_response(r):
    if r.status_code == 200:
        color = Fore.GREEN
    else:
        color = Fore.RED
    print(color + f'{r.status_code} >> {r.reason}')

course_id = 65179
assignment_id = 418644

url = f'{api_url}courses/{course_id}/assignments/{assignment_id}/overrides'
payload = {
    "due_at": "2024-04-10T00:00:00Z",
    "unlock_at": "2024-04-10T00:00:00Z"
}

r = requests.post(url=url, headers=headers, data=payload)
print_status_response(r)
if r.status_code == 200:
    response = r.json()
