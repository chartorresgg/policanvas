import os
import time
import zipfile
import requests
import pandas as pd
from colorama import Fore, init
import re
import unicodedata
from colorama import Fore
import zipfile
import shutil

init(autoreset=True)

ACCESS_TOKEN = os.getenv('Access_Token')
API_URL = 'https://poli.instructure.com/api/v1/'
ACCOUNT_ID = 1

HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

# ---------------------- CONFIGURACIÓN DINÁMICA DEL ZIP ----------------------

print(Fore.YELLOW + "\nIngrese el NOMBRE del archivo .ZIP (sin extensión):")
nombre_zip = input("Nombre del archivo ZIP: ").strip()

base_path = r'C:\Users\Charlie\Documents'
zip_file_path = os.path.join(base_path, f"{nombre_zip}.zip")
temp_extract_folder = os.path.join(base_path, f"{nombre_zip}_temp")

if not os.path.isfile(zip_file_path):
    raise FileNotFoundError(Fore.RED + f"❌ No se encontró el archivo: {zip_file_path}")

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

def corregir_estructura_contenido(ruta_base):
    print(Fore.YELLOW + "\n🔧 Verificando y corrigiendo estructura de carpetas...")

    # 1. Renombrar carpeta '1. Archivos'
    carpeta_1archivos_real = None
    for carpeta in os.listdir(ruta_base):
        if carpeta.lower().startswith("1") and "archivo" in carpeta.lower():
            carpeta_1archivos_real = os.path.join(ruta_base, carpeta)
            break

    if not carpeta_1archivos_real:
        raise FileNotFoundError("❌ No se encontró la carpeta tipo '1. Archivos'.")

    ruta_1archivos = os.path.join(ruta_base, "1. Archivos")
    if carpeta_1archivos_real != ruta_1archivos:
        os.rename(carpeta_1archivos_real, ruta_1archivos)
        print(Fore.GREEN + f"✅ Carpeta renombrada a: {ruta_1archivos}")
    else:
        print(Fore.CYAN + "ℹ Carpeta '1. Archivos' ya tiene el nombre correcto.")

    # 2. Renombrar subcarpetas internas
    nombres_correctos = {
        "presentacion": "1. Presentación",
        "materialfundamental": "2. Material fundamental",
        "materialdetrabajo": "3. Material de trabajo",
        "complemento": "4. Complementos",
        "complementaria": "4. Complementos",
        "complementarias": "4. Complementos",
        "cierre": "5. Cierre",
        "presentación": "1. Presentación"
    }

    for subcarpeta in os.listdir(ruta_1archivos):
        ruta_actual = os.path.join(ruta_1archivos, subcarpeta)
        if not os.path.isdir(ruta_actual):
            continue

        nombre_limpio = subcarpeta.lower().replace(" ", "").replace("_", "").replace(".", "")
        for clave, nombre_correcto in nombres_correctos.items():
            if clave in nombre_limpio:
                ruta_nueva = os.path.join(ruta_1archivos, nombre_correcto)
                if ruta_actual != ruta_nueva:
                    os.rename(ruta_actual, ruta_nueva)
                    print(Fore.GREEN + f"🔄 Subcarpeta '{subcarpeta}' → '{nombre_correcto}'")
                break
        else:
            print(Fore.YELLOW + f"⚠ Subcarpeta no reconocida: {subcarpeta}")

    # 3. Renombrar archivos PDF en '2. Material fundamental'
    ruta_matfund = os.path.join(ruta_1archivos, "2. Material fundamental")
    if os.path.isdir(ruta_matfund):
        print(Fore.YELLOW + "\n📂 Renombrando archivos PDF en '2. Material fundamental'...")

        for archivo in os.listdir(ruta_matfund):
            if not archivo.lower().endswith(".pdf"):
                continue

            nombre_limpio = archivo.lower()

            # Detectar unidad
            match_unidad = re.search(r'u\s?(\d)', nombre_limpio) or re.search(r'unidad\s?(\d)', nombre_limpio)
            if not match_unidad:
                print(Fore.RED + f"❌ No se detectó unidad en: {archivo}")
                continue
            unidad = match_unidad.group(1)

            # Detectar tipo
            tipo = ""
            if "material" in nombre_limpio and "fundamental" in nombre_limpio:
                tipo = "Material_Fundamental"
            elif "lectura" in nombre_limpio:
                tipo = "Lectura_Fundamental"
            elif "formativa" in nombre_limpio:
                tipo = "Actividad_Formativa"
            elif "sumativa" in nombre_limpio:
                tipo = "Actividad_Sumativa"
            elif "actividad" in nombre_limpio:
                tipo = "Actividad"
            else:
                tipo = "Desconocido"

            if tipo == "Desconocido":
                print(Fore.YELLOW + f"⚠ Tipo no reconocido para archivo: {archivo}")
                continue

            nombre_nuevo = f"U{unidad}_{tipo}.pdf"
            ruta_actual = os.path.join(ruta_matfund, archivo)
            ruta_nueva = os.path.join(ruta_matfund, nombre_nuevo)

            if ruta_actual != ruta_nueva:
                os.rename(ruta_actual, ruta_nueva)
                print(Fore.GREEN + f"🔄 '{archivo}' → '{nombre_nuevo}'")
            else:
                print(Fore.CYAN + f"ℹ '{archivo}' ya tiene el nombre correcto.")
    else:
        print(Fore.YELLOW + "⚠ No existe carpeta '2. Material fundamental'. Omitiendo renombramiento de archivos.")

    # 4. Renombrar archivos PDF en '4. Complementos'
    ruta_complementos = os.path.join(ruta_1archivos, "4. Complementos")
    if os.path.isdir(ruta_complementos):
        print(Fore.YELLOW + "\n📂 Renombrando archivos PDF en '4. Complementos'...")

        for archivo in os.listdir(ruta_complementos):
            if not archivo.lower().endswith(".pdf"):
                continue

            nombre_limpio = archivo.lower()
            match_unidad = re.search(r'u\s?(\d)', nombre_limpio) or re.search(r'unidad\s?(\d)', nombre_limpio)
            if not match_unidad:
                print(Fore.RED + f"❌ No se detectó unidad en: {archivo}")
                continue
            unidad = match_unidad.group(1)

            nombre_nuevo = f"U{unidad}_Lectura_Complementaria.pdf"
            ruta_actual = os.path.join(ruta_complementos, archivo)
            ruta_nueva = os.path.join(ruta_complementos, nombre_nuevo)

            if ruta_actual != ruta_nueva:
                os.rename(ruta_actual, ruta_nueva)
                print(Fore.GREEN + f"🔄 '{archivo}' → '{nombre_nuevo}'")
            else:
                print(Fore.CYAN + f"ℹ '{archivo}' ya tiene el nombre correcto.")
    else:
        print(Fore.YELLOW + "⚠ No existe carpeta '4. Complementos'. Omitiendo renombramiento de archivos.")





def encontrar_1_archivos(base_folder):
    for root, dirs, files in os.walk(base_folder):
        if "1. Archivos" in dirs:
            return os.path.join(root, "1. Archivos")
    raise FileNotFoundError("No se encontró la carpeta '1. Archivos'.")

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
    html = f"""
<p>
    <iframe style="width: 100%; height: 100vh; border: none;"
            src="https://poli.instructure.com/courses/{course_id}/files/{file_id}/download"
            data-api-endpoint="https://poli.instructure.com/api/v1/courses/{course_id}/files/{file_id}"
            data-api-returntype="File">
    </iframe>
</p>
"""
    data = {"wiki_page": {"body": html, "editing_roles": "teachers"}}
    endpoint = f"{API_URL}courses/{course_id}/pages/{page_url}"
    response = requests.put(endpoint, headers={**HEADERS, "Content-Type": "application/json"}, json=data)
    response.raise_for_status()
    print(Fore.GREEN + f"✅ Página '{page_url}' actualizada correctamente.")

def actualizar_pagina_complementaria(course_id, page_url, file_id, unidad):
    boton = f"00LC0{unidad}.png"
    html = f"""
<p><img id="22169" role="presentation"
        src="https://imgact.poligran.edu.co/dise_Instruc_v1/Bannermaterialcomplementario.png" alt=""
        data-api-endpoint="https://imgact.poligran.edu.co/dise_Instruc_v1/Bannermaterialcomplementario.png"
        data-api-returntype="File" /></p>
<p><a class="toModal" title="Lectura" href="https://poli.instructure.com/courses/{course_id}/files/{file_id}?wrap=1"
        target="_blank" rel="noopener"
        data-api-endpoint="https://poli.instructure.com/api/v1/courses/{course_id}/files/{file_id}"
        data-api-returntype="File"><span class="iconos"><img id="20594" style="width: 185px;"
            src="https://imgact.poligran.edu.co/dise_Instruc_v1/{boton}" alt="lectura"
            data-api-endpoint="https://imgact.poligran.edu.co/dise_Instruc_v1/{boton}"
            data-api-returntype="File" /></span></a></p>
"""
    data = {"wiki_page": {"body": html, "editing_roles": "teachers"}}
    endpoint = f"{API_URL}courses/{course_id}/pages/{page_url}"
    response = requests.put(endpoint, headers={**HEADERS, "Content-Type": "application/json"}, json=data)
    response.raise_for_status()
    print(Fore.GREEN + f"✅ Página '{page_url}' actualizada correctamente.")

def actualizar_pagina_material_trabajo(course_id, page_url, archivos_ids):
    encabezado = """
<p><span class="iconos"><img id="20600" src="https://imgact.poligran.edu.co/dise_Instruc_v1/Bannermaterialtrabajo.png"
                        alt="Bannermaterialtrabajo.png"
                        data-api-endpoint="https://imgact.poligran.edu.co/dise_Instruc_v1/Bannermaterialtrabajo.png"
                        data-api-returntype="File" /></span></p>
"""

    contenido_botones = "<p>"

    # Botones dinámicos de los archivos
    for path, file_id in archivos_ids.items():
        if path.startswith("3. Material de trabajo/"):
            try:
                nombre_archivo = os.path.basename(path)
                if nombre_archivo.startswith("U") and nombre_archivo[1].isdigit():
                    unidad = nombre_archivo[1]
                    boton = f"05MT0{unidad}.png"
                    boton_html = f"""
<a class="toModal" title="Lectura" href="https://poli.instructure.com/courses/{course_id}/files/{file_id}?wrap=1"
    target="_blank" rel="noopener"
    data-api-endpoint="https://poli.instructure.com/api/v1/courses/{course_id}/files/{file_id}"
    data-api-returntype="File">
    <span class="iconos">
        <img id="20594" style="width: 185px;"
             src="https://imgact.poligran.edu.co/dise_Instruc_v1/{boton}"
             alt="lectura"
             data-api-endpoint="https://imgact.poligran.edu.co/dise_Instruc_v1/{boton}"
             data-api-returntype="File" />
    </span>
</a>"""
                    contenido_botones += boton_html
            except Exception as e:
                print(Fore.YELLOW + f"⚠ Error procesando archivo '{path}': {e}")

    # Botones fijos de CREA y Caja de Herramientas
    contenido_botones += """
<a title="CREA" href="https://www.poli.edu.co/crea" target="_blank" rel="noopener"
   data-api-endpoint="https://www.poli.edu.co/crea" data-api-returntype="File">
    <span class="iconos">
        <img id="20594" style="width: 185px;"
             src="https://imgact.poligran.edu.co/dise_Instruc_v1/btn_crea.png"
             alt="lectura"
             data-api-endpoint="https://imgact.poligran.edu.co/dise_Instruc_v1/btn_crea.png"
             data-api-returntype="File" />
    </span>
</a>
<a title="Caja de Herramientas" href="https://www.poli.edu.co/crea/caja-de-herramientas" target="_blank" rel="noopener"
   data-api-endpoint="https://www.poli.edu.co/crea/caja-de-herramientas" data-api-returntype="File">
    <span class="iconos">
        <img id="20594" style="width: 185px;"
             src="https://imgact.poligran.edu.co/dise_Instruc_v1/btn_herramientas.png"
             alt="lectura"
             data-api-endpoint="https://imgact.poligran.edu.co/dise_Instruc_v1/btn_herramientas.png"
             data-api-returntype="File" />
    </span>
</a>"""

    contenido_botones += "</p>"

    html_final = encabezado + contenido_botones

    data = {"wiki_page": {"body": html_final, "editing_roles": "teachers"}}
    endpoint = f"{API_URL}courses/{course_id}/pages/{page_url}"
    response = requests.put(endpoint, headers={**HEADERS, "Content-Type": "application/json"}, json=data)
    response.raise_for_status()
    print(Fore.GREEN + f"✅ Página '{page_url}' actualizada correctamente.")


import re

def actualizar_front_del_curso(course_id, nombre_curso):
    ruta_excel = r'C:\Users\Charlie\OneDrive - Politécnico Grancolombiano\1 - Engineer Sytems\Programmer\2 - Python\00_scripts_apicanvas\scripts\04_upload_courses\GM_ESC562.xlsx'
    ruta_html = r'C:\Users\Charlie\OneDrive - Politécnico Grancolombiano\1 - Engineer Sytems\Programmer\2 - Python\00_scripts_apicanvas\scripts\04_upload_courses\course_front.html'

    with open(ruta_html, 'r', encoding='utf-8') as f:
        template_html = f.read()

    df = pd.read_excel(ruta_excel, sheet_name="Cargar", header=None)
    contenido = {str(df.iloc[i, 0]).strip().lower(): str(df.iloc[i, 1]).strip() for i in range(len(df))}

    url_video = contenido.get("url video inicial", "")
    texto_inicio = contenido.get("párrafo de inicio", "")
    texto_u1 = contenido.get("párrafo de introducción 1", "")
    texto_u2 = contenido.get("párrafo de introducción 2", "")
    texto_u3 = contenido.get("párrafo de introducción 3", "")
    texto_u4 = contenido.get("párrafo de introducción 4", "")
    texto_cierre = contenido.get("párrafo de cierre", "")

    if not url_video:
        raise ValueError("❌ No se encontró la URL del video en el archivo Excel.")

    html = template_html
    html = html.replace('<h2 class="course_title">INSERTAR NOMBRE DEL CURSO</h2>', f'<h2 class="course_title">{nombre_curso}</h2>')
    html = html.replace('src="INSERTAR URL DEL VÍDEO"', f'src="{url_video}"')
    html = html.replace("courses/81673", f"courses/{course_id}")

    # Función auxiliar para reemplazo de cada módulo
    def reemplazar_modulo(html, modulo, nuevo_texto):
        pattern = rf'(<p class="modulo-title-2">\s*{modulo}\s*</p>[\s\S]*?<div class="modulo-desc">)([\s\S]*?)(</div>)'
        return re.sub(pattern, rf'\1{nuevo_texto}\3', html, flags=re.IGNORECASE)

    html = reemplazar_modulo(html, "INICIO", texto_inicio)
    html = reemplazar_modulo(html, "UNIDAD 1", texto_u1)
    html = reemplazar_modulo(html, "UNIDAD 2", texto_u2)
    html = reemplazar_modulo(html, "UNIDAD 3", texto_u3)
    html = reemplazar_modulo(html, "UNIDAD 4", texto_u4)
    html = reemplazar_modulo(html, "CIERRE", texto_cierre)

    data = {"wiki_page": {"body": html, "editing_roles": "teachers"}}
    endpoint = f"{API_URL}courses/{course_id}/pages/front-del-curso"
    response = requests.put(endpoint, headers={**HEADERS, "Content-Type": "application/json"}, json=data)
    response.raise_for_status()
    print(Fore.GREEN + "✅ Página 'front-del-curso' actualizada correctamente.")


# ... [Las demás funciones permanecen igual]

def limpiar_texto(texto):
    texto = str(texto).lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')  # elimina tildes
    texto = texto.replace("_", "").replace("-", "").replace(" ", "")
    return texto

def actualizar_material_fundamental(course_id):
    encabezado_html = """
<p><img id="22169" role="banner de página" src="https://imgact.poligran.edu.co/dise_Instruc_v1/cabezote_mat_fund.png" alt=""
        data-api-endpoint="https://imgact.poligran.edu.co/dise_Instruc_v1/cabezote_mat_fund.png"
        data-api-returntype="File" /></p>
"""

    for unidad in range(1, 5):
        botones_lectura = []
        botones_actividad = []

        for ruta_archivo, file_id in archivos_ids.items():
            if not ruta_archivo.startswith("2. Material fundamental/"):
                continue

            nombre = os.path.basename(ruta_archivo)
            nombre_sin_ext = os.path.splitext(nombre)[0]

            if not nombre.startswith(f"U{unidad}_"):
                continue

            nombre_limpio = limpiar_texto(nombre_sin_ext)

            # Determinar tipo y código de imagen
            if "materialfundamental" in nombre_limpio:
                tipo = "material"
                codigo_img = "013INF00"
            elif "lectura" in nombre_limpio:
                tipo = "lectura"
                codigo_img = f"02LF0{unidad}"
            elif "formativa" in nombre_limpio:
                tipo = "actividad"
                codigo_img = f"04AF0{unidad}"
            elif "sumativa" in nombre_limpio:
                tipo = "actividad"
                if unidad == 2:
                    codigo_img = "03AE01"
                elif unidad == 4:
                    codigo_img = "03AE02"
                else:
                    print(Fore.RED + f"❌ Unidad {unidad} con actividad sumativa no tiene imagen definida.")
                    continue
            else:
                print(Fore.YELLOW + f"⚠ Archivo desconocido: {nombre_sin_ext}")
                continue

            # Botón HTML
            boton_html = f"""
<a class="toModal" title="{nombre_sin_ext}" href="https://poli.instructure.com/courses/{course_id}/files/{file_id}?wrap=1" target="_blank" rel="noopener"
    data-api-endpoint="https://poli.instructure.com/api/v1/courses/{course_id}/files/{file_id}" data-api-returntype="File">
    <span class="iconos"><img id="20594" style="width: 185px;"
        src="https://imgact.poligran.edu.co/dise_Instruc_v1/{codigo_img}.png" alt="{tipo}"
        data-api-endpoint="https://imgact.poligran.edu.co/dise_Instruc_v1/{codigo_img}.png"
        data-api-returntype="File" /></span></a>"""

            # Clasificación visual
            if tipo == "lectura":
                botones_lectura.append(boton_html)
            else:
                botones_actividad.append(boton_html)

        # Orden de contenido: Banner > Lecturas > Actividades (formativas, sumativas, material)
        cuerpo_html = encabezado_html + "\n<p>\n" + "\n".join(botones_lectura) + "\n" + "\n".join(botones_actividad) + "\n</p>"

        # Actualizar en Canvas
        endpoint = f"{API_URL}courses/{course_id}/pages/unidad-{unidad}-material-fundamental"
        data = {"wiki_page": {"body": cuerpo_html, "editing_roles": "teachers"}}
        response = requests.put(endpoint, headers={**HEADERS, "Content-Type": "application/json"}, json=data)
        response.raise_for_status()
        print(Fore.GREEN + f"✅ Página unidad-{unidad}-material-fundamental actualizada correctamente.")

def vincular_pdfs_a_actividades(course_id, API_URL, HEADERS):
    from colorama import Fore
    import requests
    import unicodedata
    import re

    # 🔗 Mapeo archivo > nombre de tarea o foro
    vinculos_pdf_actividad = {
        "U1_Actividad_Formativa.pdf": [
            "Unidad 1 - Actividad formativa",
            "Unidad 1 - Actividad formativa - Semana 2 a 7"
        ],
        "U2_Actividad_Sumativa.pdf": [
            "Unidad 2 - Actividad de entrega 1"
        ],
        "U3_Actividad_Formativa.pdf": [
            "Unidad 3 - Actividad formativa"
        ],
        "U3_Actividad_Sumativa.pdf": [
            "Unidad 3 - Actividad de entrega 1"
        ],
        "U4_Actividad_Sumativa.pdf": [
            "Unidad 4 - Actividad de entrega 2",
            "Unidad 4 - Actividad de entrega final"
        ]
    }

    def limpiar_texto(texto):
        texto = str(texto).lower().strip()
        texto = texto.replace("\\", "/")
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
        texto = texto.replace(" ", "").replace(".", "")
        return texto

    def encontrar_tarea(nombre_objetivo, mapa):
        nombre_limpio = limpiar_texto(nombre_objetivo)
        for nombre, elemento in mapa.items():
            if limpiar_texto(nombre) == nombre_limpio:
                return elemento
        return None

    print(Fore.YELLOW + "📂 Obteniendo archivos del curso...")
    files = []
    url = f"{API_URL}courses/{course_id}/files?per_page=100"
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        files.extend(response.json())
        url = response.links.get('next', {}).get('url')

    print(Fore.MAGENTA + "\n📋 Archivos PDF detectados con sus carpetas:")
    for f in files:
        if f["display_name"].endswith(".pdf"):
            nombre = f["display_name"]
            carpeta = f.get("folder", {}).get("full_name", "Sin carpeta")
            print(f" - {nombre} | 📂 {carpeta}")

    print(Fore.LIGHTBLUE_EX + "\n📁 Carpetas detectadas en los archivos:")
    carpetas_detectadas = set()
    for f in files:
        full_name = f.get("folder", {}).get("full_name", "")
        if full_name:
            carpetas_detectadas.add(limpiar_texto(full_name))
    for c in sorted(carpetas_detectadas):
        print(f"   - {c}")

    pdf_files = {
        f["display_name"]: f
        for f in files
        if f["display_name"].endswith(".pdf")
    }

    print(Fore.CYAN + f"\n🔍 Se encontraron {len(pdf_files)} PDF(s).")

    print(Fore.YELLOW + "📝 Obteniendo tareas del curso...")
    response = requests.get(f"{API_URL}courses/{course_id}/assignments?per_page=100", headers=HEADERS)
    response.raise_for_status()
    assignments = response.json()
    assignment_map = {a["name"]: a for a in assignments}

    print(Fore.YELLOW + "💬 Obteniendo foros del curso...")
    response = requests.get(f"{API_URL}courses/{course_id}/discussion_topics?per_page=100", headers=HEADERS)
    response.raise_for_status()
    foros = response.json()
    foros_map = {f["title"]: f for f in foros}

    # Fragmento HTML decorativo
    img_html = '<div><img src="https://moodin.mipoli.co/imgmooact/entregas.jpg" alt="" width="auto" height="auto" /></div>'

    for pdf_name, actividades in vinculos_pdf_actividad.items():
        file = pdf_files.get(pdf_name)
        if not file:
            print(Fore.RED + f"❌ No se encontró el archivo '{pdf_name}'.")
            continue

        file_id = file["id"]
        file_url = f"https://poli.instructure.com/courses/{course_id}/files/{file_id}/download"
        api_endpoint = f"https://poli.instructure.com/api/v1/courses/{course_id}/files/{file_id}"

        embed_code = (
            f'<a class="instructure_file_link instructure_scribd_file auto_open" '
            f'title="{pdf_name}" href="{file_url}" target="_blank" rel="noopener" '
            f'data-canvas-previewable="true" data-canvas-expanded="true" '
            f'data-api-endpoint="{api_endpoint}" data-api-returntype="File">'
            f'{pdf_name}</a><br><br>'
        )

        for actividad_nombre in actividades:
            actividad = encontrar_tarea(actividad_nombre, assignment_map)
            es_foro = False

            if not actividad:
                actividad = encontrar_tarea(actividad_nombre, foros_map)
                es_foro = True if actividad else False

            if not actividad:
                print(Fore.YELLOW + f"⚠ Actividad no encontrada: {actividad_nombre}")
                continue

            if es_foro:
                nueva_descripcion = f"{embed_code}<br><br>{actividad.get('message', '')}"
                url_update = f"{API_URL}courses/{course_id}/discussion_topics/{actividad['id']}"
                response = requests.put(url_update, headers=HEADERS, json={
                    "message": nueva_descripcion
                })
            else:
                descripcion_actual = actividad.get('description') or ''

                # Eliminar cualquier imagen previa
                descripcion_sin_img = re.sub(
                    r'<div><img\s+src="https://moodin\.mipoli\.co/imgmooact/entregas\.jpg".*?</div>',
                    '', descripcion_actual, flags=re.IGNORECASE | re.DOTALL
                ).strip()

                # Nueva descripción con imagen al inicio
                nueva_descripcion = f"{img_html}\n<p>{embed_code}</p>\n<br>{descripcion_sin_img}"
                url_update = f"{API_URL}courses/{course_id}/assignments/{actividad['id']}"
                response = requests.put(url_update, headers=HEADERS, json={
                    "assignment": {"description": nueva_descripcion}
                })

            if response.ok:
                tipo = "foro" if es_foro else "tarea"
                print(Fore.GREEN + f"✅ PDF '{pdf_name}' vinculado correctamente a la {tipo}: {actividad_nombre}")
            else:
                print(Fore.RED + f"❌ Error al actualizar '{actividad_nombre}': {response.status_code}")







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
        corregir_estructura_contenido(temp_extract_folder)  # ✅ Corrección de estructura agregada
        ruta_contenido = encontrar_1_archivos(temp_extract_folder)

        archivos_ids = {}
        for root, _, files in os.walk(ruta_contenido):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, ruta_contenido).replace("\\", "/")
                file_id = subir_archivo(nuevo_course_id, full_path, relative_path)
                archivos_ids[relative_path] = file_id

        if "1. Presentación/index.html" in archivos_ids:
            actualizar_pagina_con_iframe(nuevo_course_id, "inicio-presentacion",
                                         archivos_ids["1. Presentación/index.html"])

        if "5. Cierre/index.html" in archivos_ids:
            actualizar_pagina_con_iframe(nuevo_course_id, "cierre-retroalimentacion",
                                         archivos_ids["5. Cierre/index.html"])

        for unidad in range(1, 5):
            ruta_pdf = f"4. Complementos/U{unidad}_Lectura_Complementaria.pdf"
            if ruta_pdf in archivos_ids:
                actualizar_pagina_complementaria(nuevo_course_id, f"unidad-{unidad}-complementario",
                                                 archivos_ids[ruta_pdf], unidad)

        actualizar_pagina_material_trabajo(nuevo_course_id, "material-de-trabajo", archivos_ids)

        # 👉 Actualiza la página principal 'front-del-curso'
        actualizar_front_del_curso(nuevo_course_id, nombre_curso)

        # 👉 Actualiza las páginas de 'material fundamental' por unidad
        actualizar_material_fundamental(nuevo_course_id)

        # 👉 Vincula los PDFs de la carpeta 2. Material fundamental a las tareas del curso
        vincular_pdfs_a_actividades(nuevo_course_id, API_URL, HEADERS)

        print(Fore.GREEN + f"\n✔ Contenidos subidos correctamente al curso (ID: {nuevo_course_id}).")

    except Exception as e:
        print(Fore.RED + f'❌ Error: {e}')