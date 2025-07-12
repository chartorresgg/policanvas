import os
import zipfile
import requests
from colorama import Fore, init

init(autoreset=True)

ACCESS_TOKEN = os.getenv('Access_Token')
API_URL = 'https://poli.instructure.com/api/v1/'


course_id = input("Ingrese el ID del curso: ").strip()
zip_file_path = r'C:\Users\Charlie\Documents\DRE41925.zip'
temp_extract_folder = r'C:\Users\Charlie\Documents\DRE41925_temp'

HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

def extraer_zip(local_zip, destino):
    with zipfile.ZipFile(local_zip, 'r') as zip_ref:
        zip_ref.extractall(destino)
    print(Fore.GREEN + f'ZIP extraído en: {destino}')

def encontrar_1_archivos(base_folder):
    for root, dirs, files in os.walk(base_folder):
        if "1_Archivos" in dirs:
            return os.path.join(root, "1_Archivos")
    raise FileNotFoundError("No se encontró la carpeta '1_Archivos'.")

def subir_archivo(course_id, full_path, relative_path):
    file_name = os.path.basename(full_path)
    parent_folder_path = os.path.dirname(relative_path).replace("\\", "/")

    params = {
        'name': file_name,
        'parent_folder_path': f'/{parent_folder_path}',
        'size': os.path.getsize(full_path),
        'on_duplicate': 'rename'
    }

    init_upload_url = f'{API_URL}courses/{course_id}/files'
    response = requests.post(init_upload_url, headers=HEADERS, data=params)
    response.raise_for_status()
    upload_info = response.json()

    upload_url = upload_info['upload_url']
    upload_params = upload_info['upload_params']

    with open(full_path, 'rb') as f:
        files = {'file': (file_name, f)}
        upload_response = requests.post(upload_url, data=upload_params, files=files)
        upload_response.raise_for_status()

    print(Fore.CYAN + f'Subido: {relative_path}')

def recorrer_y_subir_contenido(course_id, base_folder):
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, base_folder)  # Ignora "1_Archivos"
            subir_archivo(course_id, full_path, relative_path)

# Ejecución
if __name__ == '__main__':
    try:
        extraer_zip(zip_file_path, temp_extract_folder)
        ruta_contenido = encontrar_1_archivos(temp_extract_folder)
        recorrer_y_subir_contenido(course_id, ruta_contenido)
        print(Fore.GREEN + "Archivos de '1_Archivos' subidos con éxito.")
    except Exception as e:
        print(Fore.RED + f'Error: {e}')
