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

# Validar columnas necesarias
columnas_requeridas = {'tipo', 'nombre', 'fecha_inicio', 'fecha_fin'}
if not columnas_requeridas.issubset(actividades_df.columns):
    raise Exception(f"❌ El archivo de actividades no contiene todas las columnas requeridas: {columnas_requeridas}")

# ---------------------- FUNCIÓN PARA OBTENER ACTIVIDADES ----------------------
def obtener_actividades_canvas(course_id):
    url = f"{API_URL}courses/{course_id}/assignments"
    actividades = []

    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Error al obtener actividades del curso {course_id}: {response.status_code}")
            return []

        actividades.extend(response.json())
        url = response.links['next']['url'] if 'next' in response.links else None

    return actividades

# ---------------------- FUNCIÓN PARA ACTUALIZAR FECHAS ----------------------
def actualizar_fecha(course_id, endpoint, actividad_canvas, fecha_inicio, fecha_fin):
    activity_id = actividad_canvas['id']
    url_update = f"{API_URL}courses/{course_id}/{endpoint}/{activity_id}"
    payload = {
        f"{endpoint[:-1]}[unlock_at]": fecha_inicio,
        f"{endpoint[:-1]}[due_at]": fecha_fin
    }
    response = requests.put(url_update, headers=HEADERS, data=payload)
    return response.status_code == 200

# ---------------------- PROCESO PRINCIPAL ----------------------
total_actividades = 0
total_cursos = 0

for _, curso in cursos_df.iterrows():
    course_id = curso['ID_URL']
    print(f"\n📘 Curso: {course_id}")

    actividades_canvas = obtener_actividades_canvas(course_id)
    actividades_aplicadas = 0

    for _, act in actividades_df.iterrows():
        nombre = act['nombre'].strip().lower()

        actividad_canvas = next(
            (a for a in actividades_canvas if a.get('name') and a['name'].strip().lower() == nombre),
            None
        )

        if actividad_canvas:
            ok = actualizar_fecha(
                course_id,
                'assignments',
                actividad_canvas,
                act['fecha_inicio'],
                act['fecha_fin']
            )
            if ok:
                print(f"  ✅ {actividad_canvas['name']} => {act['fecha_inicio']} - {act['fecha_fin']}")
                actividades_aplicadas += 1
            else:
                print(f"  ❌ Error al actualizar '{act['nombre']}'")
        # else:
        #     print(f"  ⚠️ Actividad '{act['nombre']}' no encontrada en curso {course_id}")

    if actividades_aplicadas > 0:
        print(f"🔢 Total actividades ajustadas en curso {course_id}: {actividades_aplicadas}")
        total_cursos += 1
        total_actividades += actividades_aplicadas
    else:
        print(f"⚠️ No se aplicaron actividades para el curso {course_id}")

# ---------------------- RESUMEN FINAL ----------------------
print("\n📊 RESUMEN")
print(f"✅ Total cursos modificados: {total_cursos}")
print(f"✅ Total actividades modificadas: {total_actividades}")