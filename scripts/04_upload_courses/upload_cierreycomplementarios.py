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
            "source_course_id": int(origen_id)
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

    file_info = upload_response.json()
    print(Fore.CYAN + f'Subido: {relative_path}')
    return file_info['id']

def actualizar_pagina_con_iframe(course_id, page_url, file_id):
    page_endpoint = f"{API_URL}courses/{course_id}/pages/{page_url}"
    nuevo_html = f"""
    <p>
        <iframe style=\"width: 100%; height: 100vh; border: none;\"
                src=\"https://poli.instructure.com/courses/{course_id}/files/{file_id}/download\"
                data-api-endpoint=\"https://poli.instructure.com/api/v1/courses/{course_id}/files/{file_id}\"
                data-api-returntype=\"File\">
        </iframe>
    <p>
    """
    data = {"wiki_page": {"body": nuevo_html, "editing_roles": "teachers"}}
    response = requests.put(page_endpoint, headers={**HEADERS, "Content-Type": "application/json"}, json=data)
    response.raise_for_status()
    print(Fore.GREEN + f"✅ Página '{page_url}' actualizada correctamente.")

def actualizar_pagina_complementaria(course_id, page_url, file_id, unidad):
    boton = f"00LC0{unidad}.png"
    html = f"""
<p><img id=\"22169\" role=\"presentation\"
        src=\"https://imgact.poligran.edu.co/dise_Instruc_v1/Bannermaterialcomplementario.png\" alt=\"\"
        data-api-endpoint=\"https://imgact.poligran.edu.co/dise_Instruc_v1/Bannermaterialcomplementario.png\"
        data-api-returntype=\"File\" /></p>
<p><a class=\"toModal\" title=\"Lectura\" href=\"https://poli.instructure.com/courses/{course_id}/files/{file_id}?wrap=1\"
        target=\"_blank\" rel=\"noopener\"
        data-api-endpoint=\"https://poli.instructure.com/api/v1/courses/{course_id}/files/{file_id}\"
        data-api-returntype=\"File\"><span class=\"iconos\"><img id=\"20594\" style=\"width: 185px;\"
            src=\"https://imgact.poligran.edu.co/dise_Instruc_v1/{boton}\" alt=\"lectura\"
            data-api-endpoint=\"https://imgact.poligran.edu.co/dise_Instruc_v1/{boton}\"
            data-api-returntype=\"File\" /></span></a></p>
    """
    data = {"wiki_page": {"body": html, "editing_roles": "teachers"}}
    endpoint = f"{API_URL}courses/{course_id}/pages/{page_url}"
    response = requests.put(endpoint, headers={**HEADERS, "Content-Type": "application/json"}, json=data)
    response.raise_for_status()
    print(Fore.GREEN + f"✅ Página '{page_url}' actualizada correctamente.")

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

        archivos_ids = {}
        for root, _, files in os.walk(ruta_contenido):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, ruta_contenido).replace("\\", "/")
                file_id = subir_archivo(nuevo_course_id, full_path, relative_path)
                archivos_ids[relative_path] = file_id

        # Página de presentación
        if "1_Presentación/index.html" in archivos_ids:
            actualizar_pagina_con_iframe(nuevo_course_id, "inicio-presentacion", archivos_ids["1_Presentación/index.html"])

        # Página de cierre
        if "6_Cierre/index.html" in archivos_ids:
            actualizar_pagina_con_iframe(nuevo_course_id, "cierre-retroalimentacion", archivos_ids["6_Cierre/index.html"])

        # Páginas complementarias
        for unidad in range(1, 5):
            ruta_pdf = f"4_Complementos/U{unidad}_Lectura_Complementaria.pdf"
            if ruta_pdf in archivos_ids:
                actualizar_pagina_complementaria(nuevo_course_id, f"unidad-{unidad}-complementario", archivos_ids[ruta_pdf], unidad)

        print(Fore.GREEN + f"\n✔ Contenidos subidos correctamente al curso (ID: {nuevo_course_id}).")

    except Exception as e:
        print(Fore.RED + f'❌ Error: {e}')