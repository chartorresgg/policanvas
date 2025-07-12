import pandas as pd
import requests
import os

# ---------------------- CONFIGURACIÓN BASE ----------------------
ACCESS_TOKEN = os.getenv('Access_Token')
API_URL = f'https://poli.instructure.com/api/v1/'
account_id = 1

HEADERS = {
    "Authorization": ACCESS_TOKEN
}

# ---------------------- CARGA DE ARCHIVOS ----------------------

# Ruta base local
BASE_DIR = r"/scripts/03_clear_activities_dates"

# Leer Aulas Máster
aulasmaster_df = pd.read_csv(os.path.join(BASE_DIR, "aulasmaster.csv"))
# Leer formato de actividades
activities_format_df = pd.read_csv(os.path.join(BASE_DIR, "activitiesmaster.csv"))

# ---------------------- FUNCIONES ----------------------

def obtener_tareas(curso_id):
    url = f"{API_URL}/courses/{curso_id}/assignments"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.ok else []

def obtener_quices(curso_id):
    url = f"{API_URL}/courses/{curso_id}/quizzes"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.ok else []

def limpiar_fechas_actividad(curso_id, actividad_id, tipo='assignment'):
    """
    Elimina fechas de disponibilidad, entrega y cierre de una actividad.
    """
    if tipo == 'assignment':
        url = f"{API_URL}/courses/{curso_id}/assignments/{actividad_id}"
    else:
        url = f"{API_URL}/courses/{curso_id}/quizzes/{actividad_id}"

    data = {
        "assignment": {
            "due_at": None,
            "unlock_at": None,
            "lock_at": None
        } if tipo == 'assignment' else {
            "due_at": None,
            "unlock_at": None,
            "lock_at": None
        }
    }

    response = requests.put(url, headers=HEADERS, json=data)
    return response.ok

def limpiar_actividades_del_curso(curso_id, actividades_formato):
    tareas = obtener_tareas(curso_id)
    quices = obtener_quices(curso_id)

    actividades_actualizadas = []

    for tarea in tareas:
        for formato in actividades_formato:
            if formato in tarea['name']:
                exito = limpiar_fechas_actividad(curso_id, tarea['id'], tipo='assignment')
                if exito:
                    actividades_actualizadas.append({
                        'curso_id': curso_id,
                        'tipo': 'Tarea',
                        'nombre': tarea['name'],
                        'id': tarea['id']
                    })

    for quiz in quices:
        for formato in actividades_formato:
            if formato in quiz['title']:
                exito = limpiar_fechas_actividad(curso_id, quiz['id'], tipo='quiz')
                if exito:
                    actividades_actualizadas.append({
                        'curso_id': curso_id,
                        'tipo': 'Quiz',
                        'nombre': quiz['title'],
                        'id': quiz['id']
                    })

    return actividades_actualizadas

# ---------------------- EJECUCIÓN PRINCIPAL ----------------------

def main():
    actividades_formato = [x.split("|")[1].strip() for x in activities_format_df['SCRIPT']]

    log_actividades = []

    for _, row in aulasmaster_df.iterrows():
        curso_id = row['ID_URL']
        print(f"Limpieza de fechas para curso: {curso_id}...")
        actualizadas = limpiar_actividades_del_curso(curso_id, actividades_formato)
        log_actividades.extend(actualizadas)

    # Guardar log
    log_df = pd.DataFrame(log_actividades)
    log_df.to_csv(os.path.join(BASE_DIR, "log_actividades_limpias.csv"), index=False)
    print("Proceso finalizado. Log guardado.")

if __name__ == "__main__":
    main()
