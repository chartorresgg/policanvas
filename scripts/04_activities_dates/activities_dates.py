import pandas as pd
import requests
import os

# ---------------------- CONFIGURACIÓN BASE ----------------------
Access_Token = os.getenv('Access_Token')  # Asegúrate de definirlo en variables de entorno
API_URL = 'https://poli.instructure.com/api/v1/'
HEADERS = {
    "Authorization": f"Bearer {Access_Token}"
}

# ---------------------- CARGA DE ARCHIVOS ----------------------
ruta_actividades = r'C:\Users\Charlie\OneDrive - Politécnico Grancolombiano\1 - Engineer Sytems\Programmer\2 - Python\00_scripts_apicanvas\scripts\04_activities_dates\activitiesmaster.csv'
ruta_cursos = r'C:\Users\Charlie\OneDrive - Politécnico Grancolombiano\1 - Engineer Sytems\Programmer\2 - Python\00_scripts_apicanvas\scripts\04_activities_dates\aulasmaster.csv'

# Cargar archivos
actividades_df = pd.read_csv(ruta_actividades, sep=';')
cursos_df = pd.read_csv(ruta_cursos)

# Verificar columnas requeridas
columnas_requeridas = {'tipo', 'nombre', 'fecha_inicio', 'fecha_fin'}
if not columnas_requeridas.issubset(set(actividades_df.columns)):
    raise Exception(f"❌ El archivo de actividades no contiene todas las columnas requeridas: {columnas_requeridas}")

print("✅ Actividades cargadas:")
print(actividades_df.head())

# ---------------------- FUNCIONES DE API ----------------------

def actualizar_fechas(course_id, actividad, tipo, fecha_inicio, fecha_fin):
    tipo_endpoint = {
        'Quiz': 'quizzes',
        'Tarea': 'assignments',
        'Evaluacion': 'quizzes',  # Ajusta según tu estructura real
    }

    endpoint = tipo_endpoint.get(tipo, 'assignments')  # Default a 'assignments'
    url_listar = f"{API_URL}courses/{course_id}/{endpoint}"

    response = requests.get(url_listar, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ Error al obtener actividades del curso {course_id}: {response.status_code}")
        return None

    actividades = response.json()
    for act in actividades:
        if act['name'].strip().lower() == actividad.strip().lower():
            activity_id = act['id']
            url_update = f"{API_URL}courses/{course_id}/{endpoint}/{activity_id}"
            payload = {
                f"{endpoint[:-1]}[unlock_at]": fecha_inicio,
                f"{endpoint[:-1]}[due_at]": fecha_fin
            }
            put_resp = requests.put(url_update, headers=HEADERS, data=payload)
            if put_resp.status_code == 200:
                return act['name']
            else:
                return None
    return None

# ---------------------- PROCESO PRINCIPAL ----------------------

total_actividades = 0
total_cursos = 0

for _, row in cursos_df.iterrows():
    course_id = row['ID_URL']
    actividades_aplicadas = 0
    actividades_modificadas = []

    for _, act_row in actividades_df.iterrows():
        nombre = act_row['nombre']
        tipo = act_row['tipo']
        fecha_inicio = act_row['fecha_inicio']
        fecha_fin = act_row['fecha_fin']

        resultado = actualizar_fechas(course_id, nombre, tipo, fecha_inicio, fecha_fin)
        if resultado:
            actividades_aplicadas += 1
            actividades_modificadas.append(f"  ✅ {resultado} => {fecha_inicio} - {fecha_fin}")

    if actividades_aplicadas > 0:
        print(f"\n📘 Curso: {course_id}")
        for act in actividades_modificadas:
            print(act)
        print(f"🔢 Total actividades aplicadas: {actividades_aplicadas}")
        total_actividades += actividades_aplicadas
        total_cursos += 1

# ---------------------- RESUMEN FINAL ----------------------
print("\n----------------------")
print(f"✅ Total cursos procesados: {total_cursos}")
print(f"✅ Total actividades modificadas: {total_actividades}")