import requests
import os
import pandas as pd
from datetime import datetime, timedelta

# ---------------------- CONFIGURACIÓN BASE ----------------------
Access_Token = os.getenv('Access_Token')
API_URL = 'https://poli.instructure.com/api/v1/'
HEADERS = {"Authorization": f"Bearer {Access_Token}"}

log_ampliaciones = []

# ---------------------- FUNCIÓN: OBTENER ACTIVIDADES ----------------------
def obtener_actividades_canvas(course_id):
    url = f"{API_URL}courses/{course_id}/assignments"
    actividades = []
    while url:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Error al obtener actividades del curso {course_id}")
            return []
        actividades.extend(response.json())
        url = response.links['next']['url'] if 'next' in response.links else None
    return actividades

# ---------------------- FUNCIÓN: OBTENER ESTUDIANTES ----------------------
def obtener_estudiantes_del_curso(course_id):
    url = f"{API_URL}courses/{course_id}/users"
    params = {"enrollment_type": "student", "per_page": 100}
    estudiantes = []
    while url:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"❌ Error al obtener estudiantes del curso {course_id}")
            return []
        estudiantes.extend(response.json())
        url = response.links['next']['url'] if 'next' in response.links else None
        params = None
    return estudiantes

# ---------------------- FUNCIÓN: EXTENDER ACTIVIDAD ----------------------
def extender_actividad_estudiante(course_id, assignment_id, user_id, fecha_inicio, fecha_fin, actividad_nombre):
    url = f"{API_URL}courses/{course_id}/assignments/{assignment_id}/overrides"
    payload = {
        "assignment_override[student_ids][]": user_id,
        "assignment_override[unlock_at]": fecha_inicio,
        "assignment_override[due_at]": fecha_fin,
        "assignment_override[lock_at]": fecha_fin
    }
    response = requests.post(url, headers=HEADERS, data=payload)
    if response.status_code in [200, 201]:
        print(f"✅ Estudiante {user_id} - Actividad {actividad_nombre} extendida hasta {fecha_fin}")
        log_ampliaciones.append({
            "curso_id": course_id,
            "estudiante_id": user_id,
            "actividad": actividad_nombre,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        })
    else:
        print(f"❌ Error al extender actividad {assignment_id} para estudiante {user_id}: {response.status_code}")
        print(f"   ▶️ Detalles: {response.text}")

# ---------------------- ENTRADA MANUAL ----------------------
def entrada_lista_vertical(mensaje):
    print(mensaje)
    valores = []
    while True:
        linea = input()
        if linea.strip() == "":
            break
        valores.append(linea.strip())
    return valores

# ---------------------- PROCESO COMPLETO ----------------------
def flujo_extensiones():
    curso_ids = entrada_lista_vertical("📘 Ingrese IDs de cursos (uno por línea, ENTER para terminar):")
    actividades_nombre = entrada_lista_vertical("✏️ Ingrese nombres o fragmentos de las actividades (uno por línea, ENTER para terminar):")
    estudiantes_ids = entrada_lista_vertical("👤 Ingrese IDs de estudiantes (uno por línea, ENTER para terminar):")

    fecha_inicio_raw = input("📅 Fecha de INICIO (formato ISO 8601): ").strip()
    fecha_fin_raw = input("📅 Fecha de FIN (formato ISO 8601): ").strip()

    # ✅ Ajustar sumando un día
    fecha_inicio_dt = datetime.strptime(fecha_inicio_raw, "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=1)
    fecha_fin_dt = datetime.strptime(fecha_fin_raw, "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=1)

    fecha_inicio = fecha_inicio_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    fecha_fin = fecha_fin_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    for curso_id in curso_ids:
        actividades = obtener_actividades_canvas(curso_id)
        estudiantes = obtener_estudiantes_del_curso(curso_id)
        ids_estudiantes_en_curso = {str(est['id']) for est in estudiantes}

        actividades_seleccionadas = [
            a for a in actividades if any(nombre.lower() in a['name'].lower() for nombre in actividades_nombre)
        ]

        if not actividades_seleccionadas:
            print(f"⚠️ No se encontraron actividades coincidentes en el curso {curso_id}.")
            continue

        for act in actividades_seleccionadas:
            for estudiante_id in estudiantes_ids:
                if estudiante_id not in ids_estudiantes_en_curso:
                    print(f"🚫 Estudiante {estudiante_id} no está inscrito en el curso {curso_id}.")
                    continue
                extender_actividad_estudiante(
                    curso_id, act['id'], estudiante_id, fecha_inicio, fecha_fin, act['name']
                )

    # ✅ Exportar log si hubo registros
    if log_ampliaciones:
        df = pd.DataFrame(log_ampliaciones)
        nombre_archivo = f"log_ampliaciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(nombre_archivo, index=False)
        print(f"📤 Log exportado en: {nombre_archivo}")
    else:
        print("⚠️ No se realizaron ampliaciones.")

# ---------------------- EJECUCIÓN ----------------------
if __name__ == "__main__":
    flujo_extensiones()
