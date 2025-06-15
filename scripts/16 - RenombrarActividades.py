import requests
import os
import json
import pandas as pd
from colorama import Fore, Back, Style, init

# Configuración
init(autoreset=True)
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
API_URL = f'https://poli.instructure.com/api/v1/'
account_id = 1# Reemplaza con la URL de tu instancia de Canvas
COURSE_ID = "43255"  # Reemplaza con el ID del curso
ASSIGNMENT_ID = "489759"  # Reemplaza con el ID de la actividad
NEW_NAME = "Actividad renombrada"  # Nuevo nombre de la actividad

# Encabezados de autenticación
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# URL de la API para actualizar la asignación
url = f"{API_URL}/courses/{COURSE_ID}/assignments/{ASSIGNMENT_ID}"

# Datos para actualizar la actividad
data = {
    "assignment": {
        "name": NEW_NAME
    }
}

# Realizar la solicitud PUT
response = requests.put(url, headers=headers, json=data)

# Verificar respuesta
if response.status_code == 200:
    print("Actividad renombrada exitosamente.")
else:
    print(f"Error al renombrar la actividad: {response.status_code}")
    print(response.json())  # Mostrar detalles del error si ocurre
