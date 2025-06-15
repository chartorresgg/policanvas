import os, sys
import requests
import pandas as pd
from colorama import Fore, init

init(autoreset=True)
ACCESS_TOKEN = os.getenv('Access_Token')
API_URL = f'https://poli.instructure.com/api/v1/'
account_id = 1

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# Leer archivo Excel
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(base_path, 'Ciencias_Basicas.xlsx')
df_cursos = pd.read_excel(file_path, sheet_name='Foros')
df_cursos = df_cursos.dropna(subset=['canvas_course_id'])
course_ids = df_cursos['canvas_course_id'].astype(int).tolist()

# Resultados
resultados = []

# Función para obtener los conjuntos de grupos de un curso
def get_all_group_categories(course_id):
    url = f"{API_URL}/courses/{course_id}/group_categories"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return {cat["id"]: cat["name"] for cat in response.json()}
    return {}

# Función para obtener los detalles de la tarea asociada
def get_assignment_details(course_id, assignment_id):
    url = f"{API_URL}/courses/{course_id}/assignments/{assignment_id}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        return {
            'points_possible': data.get("points_possible", None),
            'unlock_at': data.get("unlock_at", None),
            'due_at': data.get("due_at", None),
            'lock_at': data.get("lock_at", None)
        }
    return {
        'points_possible': None,
        'unlock_at': None,
        'due_at': None,
        'lock_at': None
    }

# Función para verificar la configuración de los foros
def check_discussion_group_settings(course_ids):
    for course_id in course_ids:
        course_name = df_cursos[df_cursos['canvas_course_id'] == course_id]['course_name'].values[0]
        group_categories = get_all_group_categories(course_id)
        url = f"{API_URL}/courses/{course_id}/discussion_topics?per_page=100"
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            discussions = response.json()
            for discussion in discussions:
                title = discussion.get('title', 'Sin título')
                group_cat_id = discussion.get('group_category_id')
                assignment_id = discussion.get('assignment_id')
                pinned = discussion.get('pinned', False)
                graded = discussion.get('require_initial_post') is not None or assignment_id is not None
                published = discussion.get('published', None)

                # Obtener detalles de la tarea si existe
                assignment_details = get_assignment_details(course_id, assignment_id) if assignment_id else {}
                points_possible = assignment_details.get('points_possible')
                fecha_inicio = assignment_details.get('unlock_at') or discussion.get('delayed_post_at')
                fecha_fin = assignment_details.get('lock_at') or discussion.get('lock_at')

                estado = ''
                group_name = ''
                if group_cat_id:
                    group_name = group_categories.get(group_cat_id, 'Desconocido')
                    estado = 'Correcto' if group_name == "SUBGRUPOS" else 'Asociado a otro grupo'
                else:
                    estado = 'No es grupal'

                resultados.append({
                    'course_id': course_id,
                    'course_name': course_name,
                    'discussion_title': title,
                    'group_category_id': group_cat_id,
                    'group_category_name': group_name,
                    'estado_configuracion': estado,
                    'assignment_id': assignment_id,
                    'points_possible': points_possible,
                    'pinned': pinned,
                    'graded': graded,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'published': published
                })

            print(Fore.GREEN + f"✅ Se leyó la configuración de foros del curso {course_id} - {course_name}")
        else:
            print(Fore.RED + f"❌ Error al obtener foros del curso {course_id}. Código: {response.status_code}")
            resultados.append({
                'course_id': course_id,
                'course_name': course_name,
                'discussion_title': None,
                'group_category_id': None,
                'group_category_name': None,
                'estado_configuracion': 'Error',
                'assignment_id': None,
                'points_possible': None,
                'pinned': None,
                'graded': None,
                'fecha_inicio': None,
                'fecha_fin': None,
                'published': None
            })

# Ejecutar función
check_discussion_group_settings(course_ids)

# Exportar resultados
df_resultados = pd.DataFrame(resultados)

# Filtrar actividades específicas (opcional)
actividades_deseadas = [
    'Foro: Desarrollo del trabajo - Escenarios 3, 4 y 5',
    'Unidad 2 - Actividad de entrega'
]
df_resultados = df_resultados[df_resultados['discussion_title'].isin(actividades_deseadas)]

# Exportar a CSV
df_resultados.to_csv('reporte_configuracion_foros.csv', index=False, encoding='utf-8-sig')
print(Fore.CYAN + "\n✅ Resultados guardados en 'reporte_configuracion_foros.csv'")

# Función para actualizar la configuración del foro
def update_discussion_settings(course_id, discussion_id, settings):
    url = f"{API_URL}/courses/{course_id}/discussion_topics/{discussion_id}"
    response = requests.put(url, headers=HEADERS, json=settings)
    if response.status_code == 200:
        print(Fore.YELLOW + f"📌 Foro actualizado (course_id={course_id}, id={discussion_id}): {settings}")
    else:
        print(Fore.RED + f"❌ Error al actualizar foro (course_id={course_id}, id={discussion_id}). Código: {response.status_code}")

# Confirmar si se desean aplicar los cambios
aplicar_cambios = input(Fore.MAGENTA + "\n¿Deseas fijar (pinned = True) los foros filtrados? (sí/no): ").strip().lower()

if aplicar_cambios in ['sí', 'si', 's']:
    for _, row in df_resultados.iterrows():
        if not row['pinned']:
            course_id = row['course_id']
            title = row['discussion_title']
            # Buscar ID del foro
            url = f"{API_URL}/courses/{course_id}/discussion_topics?per_page=100"
            r = requests.get(url, headers=HEADERS)
            if r.status_code == 200:
                for foro in r.json():
                    if foro.get('title') == title:
                        update_discussion_settings(course_id, foro['id'], {'pinned': True})
                        break
            else:
                print(Fore.RED + f"❌ Error al consultar foros del curso {course_id} para actualizar.")
else:
    print(Fore.CYAN + "\n🚫 No se aplicaron cambios a los foros.")