import pandas as pd
import requests
import os
from datetime import datetime

# ---------------------- CONFIGURACIÓN BASE ----------------------
Access_Token = os.getenv('Access_Token')
API_URL = 'https://poli.instructure.com/api/v1/'
HEADERS = {"Authorization": f"Bearer {Access_Token}"}
ACCOUNT_ID = 1  # ID principal de la cuenta Canvas


# ---------------------- CARGA AUTOMÁTICA DE ARCHIVO CSV ----------------------
def cargar_archivo_csv():
    ruta = r'C:\Users\Charlie\OneDrive - Politécnico Grancolombiano\1 - Engineer Sytems\Programmer\2 - Python\00_scripts_apicanvas\scripts\04_activities_dates\activitiesmaster.csv'

    print(f"\n📂 Cargando archivo CSV desde: {ruta}")

    if not os.path.exists(ruta):
        raise Exception("❌ La ruta especificada no existe.")

    df = pd.read_csv(ruta, sep=';', encoding='latin1')
    columnas_requeridas = {'tipo', 'nombre', 'fecha_inicio', 'fecha_fin'}
    if not columnas_requeridas.issubset(df.columns):
        raise Exception(f"❌ El archivo no contiene las columnas requeridas: {columnas_requeridas}")

    print("✅ Archivo cargado correctamente.")
    return df
# ---------------------- FUNCIÓN: OBTENER CURSOS ----------------------
def obtener_cursos_por_periodo(account_id, term_id):
    url = f"{API_URL}accounts/{account_id}/courses"
    params = {"enrollment_term_id": term_id, "per_page": 100}
    cursos = []
    while url:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        cursos.extend(response.json())
        url = response.links['next']['url'] if 'next' in response.links else None
        params = None
    return cursos

# ---------------------- FUNCIÓN: OBTENER ACTIVIDADES DEL CURSO ----------------------
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

# ---------------------- FUNCIÓN: ACTUALIZAR FECHAS ----------------------
def actualizar_fecha(course_id, actividad_canvas, fecha_inicio, fecha_fin):
    url_update = f"{API_URL}courses/{course_id}/assignments/{actividad_canvas['id']}"
    payload = {
        "assignment[unlock_at]": fecha_inicio,
        "assignment[due_at]": fecha_fin,
        "assignment[lock_at]": fecha_fin
    }
    response = requests.put(url_update, headers=HEADERS, data=payload)
    if response.status_code != 200:
        return False, f"Error {response.status_code}: {response.text}"
    return True, "Modificada"

# ---------------------- FUNCIÓN: APLICAR FECHAS A CURSO ----------------------
def aplicar_fechas_a_curso(course_id, actividades_df, nombre_curso=None, filtro=None):
    actividades_canvas = obtener_actividades_canvas(course_id)
    actividades_aplicadas = 0
    log_curso = []

    for _, act in actividades_df.iterrows():
        if filtro:
            if filtro['tipo'] == 'nombre' and filtro['valor'].lower() not in act['nombre'].lower():
                continue
            if filtro['tipo'] == 'tipo' and filtro['valor'].lower() != str(act.get('tipo', '')).lower():
                continue

        nombre = act['nombre'].strip().lower()
        actividad_canvas = next(
            (a for a in actividades_canvas if a.get('name') and a['name'].strip().lower() == nombre),
            None
        )

        if actividad_canvas:
            ok, mensaje = actualizar_fecha(
                course_id,
                actividad_canvas,
                act['fecha_inicio'],
                act['fecha_fin']
            )
            if ok:
                actividades_aplicadas += 1
                log_curso.append({
                    "curso_id": course_id,
                    "curso_nombre": nombre_curso,
                    "actividad": actividad_canvas['name'],
                    "fecha_inicio": act['fecha_inicio'],
                    "fecha_fin": act['fecha_fin']
                })

    if actividades_aplicadas > 0:
        print(f"\n📘 Curso: {course_id}" + (f" | {nombre_curso}" if nombre_curso else ""))
        for linea in log_curso:
            print(f"  ✅ {linea['actividad']} => {linea['fecha_inicio']} - {linea['fecha_fin']}")
        print(f"🔢 Total actividades ajustadas en curso {course_id}: {actividades_aplicadas}")

    return log_curso

# ---------------------- FUNCIÓN: CAMBIAR PERIODO ----------------------
def cambiar_periodo():
    term_id = input("\n🧾 Ingrese el ID del periodo (ej: 1163): ").strip()
    cursos = obtener_cursos_por_periodo(ACCOUNT_ID, term_id)
    print(f"📘 Cursos en el periodo {term_id}: {len(cursos)}")
    return term_id, cursos

# ---------------------- FUNCIÓN: DEFINIR FILTRO ----------------------
def definir_filtro():
    print("\n🎯 ¿Desea aplicar un filtro a las actividades?")
    print("1. Aplicar todas")
    print("2. Filtrar por nombre (palabra clave)")
    print("3. Filtrar por tipo")

    opcion = input("Seleccione una opción (1-3): ").strip()

    if opcion == "2":
        palabra = input("🔍 Ingrese palabra clave (ej: Unidad 1): ").strip()
        return {"tipo": "nombre", "valor": palabra}
    elif opcion == "3":
        tipo = input("🔍 Ingrese tipo de actividad (ej: foro, quiz, taller): ").strip()
        return {"tipo": "tipo", "valor": tipo}
    else:
        return None

# ---------------------- EJECUCIÓN PRINCIPAL ----------------------
actividades_df = cargar_archivo_csv()
TERM_ID, cursos_periodo = cambiar_periodo()
log_total = []

while True:
    print("\n🧭 MENÚ PRINCIPAL")
    print("1. Aplicar fechas a TODOS los cursos del periodo")
    print("2. Aplicar fechas a uno o más cursos (IDs separados por coma)")
    print("3. Cambiar de periodo académico")
    print("4. Exportar reporte a Excel")
    print("5. Salir")

    opcion = input("Seleccione una opción (1-5): ").strip()

    if opcion == "1":
        filtro = definir_filtro()
        for curso in cursos_periodo:
            log = aplicar_fechas_a_curso(curso['id'], actividades_df, curso['name'], filtro)
            log_total.extend(log)

    elif opcion == "2":
        ids_input = input("🔎 IDs de cursos separados por coma: ").strip()
        ids = [i.strip() for i in ids_input.split(",") if i.strip().isdigit()]
        filtro = definir_filtro()
        for cid in ids:
            curso = next((c for c in cursos_periodo if str(c['id']) == cid), None)
            if curso:
                log = aplicar_fechas_a_curso(cid, actividades_df, curso['name'], filtro)
                log_total.extend(log)
            else:
                print(f"⚠️ El curso {cid} no pertenece al periodo actual.")

    elif opcion == "3":
        TERM_ID, cursos_periodo = cambiar_periodo()

    elif opcion == "4":
        if not log_total:
            print("⚠️ No hay datos para exportar aún.")
        else:
            df_log = pd.DataFrame(log_total)
            nombre_archivo = f"log_actualizacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df_log.to_excel(nombre_archivo, index=False)
            print(f"📤 Log exportado a {nombre_archivo}")

    elif opcion == "5":
        print("👋 Saliendo de la aplicación...")
        break

    else:
        print("❌ Opción inválida. Intente de nuevo.")
