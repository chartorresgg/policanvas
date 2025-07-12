import requests
from colorama import Fore

def vincular_pdfs_a_actividades(course_id, API_URL, HEADERS):
    # Mapeo archivo > nombre de tarea
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

    # Obtener archivos del curso
    print(Fore.YELLOW + "📂 Obteniendo archivos del curso para vincular PDFs...")
    files = []
    url = f"{API_URL}courses/{course_id}/files?per_page=100"
    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        files.extend(response.json())
        url = response.links.get('next', {}).get('url')

    # Filtrar archivos PDF de la carpeta 2. Material fundamental
    pdf_files = {
        f["display_name"]: f
        for f in files
        if f["display_name"].endswith(".pdf") and "2. Material fundamental" in f.get("folder", {}).get("full_name", "")
    }

    # Obtener todas las tareas del curso
    print(Fore.YELLOW + "📝 Obteniendo tareas del curso...")
    response = requests.get(f"{API_URL}courses/{course_id}/assignments?per_page=100", headers=HEADERS)
    response.raise_for_status()
    assignments = response.json()
    assignment_map = {a["name"]: a for a in assignments}

    for pdf_name, tareas in vinculos_pdf_actividad.items():
        file = pdf_files.get(pdf_name)
        if not file:
            print(Fore.RED + f"❌ Archivo no encontrado: {pdf_name}")
            continue

        file_url = file["url"]
        file_embed_code = (
            f'<a class="instructure_file_link inline_disabled" '
            f'title="{pdf_name}" href="{file_url}" '
            f'data-canvas-previewable="true" data-canvas-expanded="true" '
            f'target="_blank">{pdf_name}</a>'
        )

        for tarea in tareas:
            actividad = assignment_map.get(tarea)
            if not actividad:
                print(Fore.YELLOW + f"⚠ Tarea no encontrada: {tarea}")
                continue

            nueva_descripcion = f"{file_embed_code}<br><br>{actividad['description']}"
            url_update = f"{API_URL}courses/{course_id}/assignments/{actividad['id']}"
            response = requests.put(url_update, headers=HEADERS, json={
                "assignment": {"description": nueva_descripcion}
            })
            response.raise_for_status()
            print(Fore.GREEN + f"✅ PDF '{pdf_name}' vinculado a tarea: {tarea}")
