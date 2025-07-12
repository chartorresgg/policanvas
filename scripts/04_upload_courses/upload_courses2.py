import os
import time
import zipfile
import requests
import pandas as pd
from colorama import Fore, init

init(autoreset=True)

ACCESS_TOKEN = os.getenv('Access_Token')
API_URL = 'https://poli.instructure.com/api/v1/'
ACCOUNT_ID = 1

HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

zip_file_path = r'C:\Users\Charlie\Documents\DRE41925.zip'
temp_extract_folder = r'C:\Users\Charlie\Documents\DRE41925_temp'
plantilla_excel_path = r'C:\Users\Charlie\OneDrive - Politécnico Grancolombiano\1 - Engineer Sytems\Programmer\2 - Python\00_scripts_apicanvas\scripts\04_upload_courses\templates_aulasmaster.xlsx'

# ---------------------- FUNCIONES ----------------------

def cargar_plantillas(path_excel):
    df = pd.read_excel(path_excel)
    df.columns = [col.strip().upper() for col in df.columns]
    return df

def solicitar_seleccion(df):
    print(Fore.YELLOW + "\nSeleccione el DISEÑO INSTRUCCIONAL:")
    disenos = df['DISEÑO INSTRUCCIONAL'].unique()
    for i, d in enumerate(disenos, 1):
        print(f"{i}. {d}")
    diseno = disenos[int(input("Opción: ")) - 1]

    print(Fore.YELLOW + "\nSeleccione el NIVEL DE FORMACIÓN:")
    niveles = df['NIVEL DE FORMACIÓN'].unique()
    for i, n in enumerate(niveles, 1):
        print(f"{i}. {n}")
    nivel = niveles[int(input("Opción: ")) - 1]

    print(Fore.YELLOW + "\nSeleccione la TIPOLOGÍA:")
    tipologias = df[(df['DISEÑO INSTRUCCIONAL'] == diseno)]['TIPOLOGÍA'].unique()
    for i, t in enumerate(tipologias, 1):
        print(f"{i}. {t}")
    tipologia = tipologias[int(input("Opción: ")) - 1]

    plantilla = df[
        (df['DISEÑO INSTRUCCIONAL'] == diseno) &
        (df['NIVEL DE FORMACIÓN'] == nivel) &
        (df['TIPOLOGÍA'] == tipologia)
    ].iloc[0]

    print(Fore.GREEN + f"\nPlantilla seleccionada: {plantilla['NOMBRE DE LA PLANTILLA']} (ID: {plantilla['ID URL DE LA PLANTILLA']})")
    return plantilla['ID URL DE LA PLANTILLA']

def crear_curso(nombre_curso):
    url = f"{API_URL}accounts/{ACCOUNT_ID}/courses"
    data = {
        "course[name]": nombre_curso,
        "course[course_code]": nombre_curso,
        "course[is_public]": False,
        "course[license]": "private",
        "enroll_me": True
    }
    response = requests.post(url, headers=HEADERS, data=data)
    response.raise_for_status()
    nuevo_curso = response.json()
    print(Fore.GREEN + f"✅ Curso creado: {nuevo_curso['name']} (ID: {nuevo_curso['id']})")
    return nuevo_curso['id']

def copiar_contenido_plantilla(origen_id, destino_id):
    url = f"{API_URL}courses/{destino_id}/content_migrations"
    json_data = {
        "migration_type": "course_copy_importer",
        "settings": {
            "source_course_id": int(origen_id)  # 👈 Conversión clave
        }
    }
    response = requests.post(url, headers={**HEADERS, "Content-Type": "application/json"}, json=json_data)
    response.raise_for_status()
    migration = response.json()
    print(Fore.YELLOW + f"📦 Copiando contenido desde plantilla (Migration ID: {migration['id']})")
    return migration['id']


def esperar_migracion(course_id, migration_id):
    url = f"{API_URL}courses/{course_id}/content_migrations/{migration_id}"
    while True:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        estado = response.json()
        if estado['workflow_state'] == 'completed':
            print(Fore.GREEN + "✅ Migración completada.")
            break
        elif estado['workflow_state'] == 'failed':
            raise Exception("❌ La migración falló.")
        print(Fore.YELLOW + "⌛ Esperando que termine la migración...")
        time.sleep(5)

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

# ---------------------- EJECUCIÓN ----------------------

if __name__ == '__main__':
    try:
        df_plantillas = cargar_plantillas(plantilla_excel_path)
        id_plantilla = solicitar_seleccion(df_plantillas)

        print(Fore.YELLOW + "\nIngrese el NOMBRE del nuevo curso:")
        nombre_curso = input("Nombre del curso: ").strip()

        nuevo_course_id = crear_curso(nombre_curso)
        migration_id = copiar_contenido_plantilla(id_plantilla, nuevo_course_id)
        esperar_migracion(nuevo_course_id, migration_id)

        extraer_zip(zip_file_path, temp_extract_folder)
        ruta_contenido = encontrar_1_archivos(temp_extract_folder)
        recorrer_y_subir_contenido(nuevo_course_id, ruta_contenido)

        print(Fore.GREEN + f"\n✔ Contenidos subidos correctamente al curso (ID: {nuevo_course_id}).")

    except Exception as e:
        print(Fore.RED + f'❌ Error: {e}')
