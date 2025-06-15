import os
import json
import sys
import csv
import pandas as pd
import requests
from colorama import Fore, Back, Style, init

init(autoreset=True)  # reset the previous color and style after each line
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
api_url = f'https://poli.instructure.com/api/v1/'

def settings_course(url='', payload={}, token=''):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.put(url, headers=headers, data=payload)
    if r.status_code == 200:
        color = Fore.GREEN
    else:
        color = Fore.RED
    print(color + f'{r.status_code} >> {r.reason}')
    if r.status_code == 200:
       return r
    else:
        return None

course_id = 7752

url = f'{api_url}courses/{course_id}/settings'
token = ACCESS_TOKEN
payload = {
    "filter_speed_grader_by_student_group": False,
}
r = settings_course(url, payload=payload, token=ACCESS_TOKEN)
response = r.json()
print(response)