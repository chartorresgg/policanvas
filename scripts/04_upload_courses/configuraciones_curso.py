import os
import requests
from colorama import Fore, init

# Configuración
init(autoreset=True)
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
api_url = 'https://poli.instructure.com/api/v1/'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

def publicar_curso(course_id):
    url = f"{api_url}courses/{course_id}"
    payload = {
        "offer": "true"  # CLAVE: fuera de "course"
    }
    response = requests.put(url, headers=HEADERS, data=payload)  # usar 'data' para parámetros planos
    if response.status_code == 200:
        print(Fore.GREEN + "✅ Curso publicado exitosamente.")
    else:
        print(Fore.RED + "❌ Error al publicar el curso:")
        print(response.text)

def mover_curso_a_subcuenta(course_id, term_id, account_id):
    url = f"{api_url}courses/{course_id}"
    payload = {
        "course": {
            "enrollment_term_id": term_id,
            "account_id": account_id
        }
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(Fore.GREEN + f"✅ Término actualizado a ID {term_id} y subcuenta movida a ID {account_id}.")
        publicar_curso(course_id)
    else:
        print(Fore.RED + "❌ No se pudo actualizar el término o subcuenta:")
        print(response.text)

def diagnostico_y_ajuste(course_id):
    url = f"{api_url}courses/{course_id}?include[]=term&include[]=permissions"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(Fore.RED + "❌ No se pudo obtener el curso.")
        print(response.text)
        return

    data = response.json()
    estado = data.get("workflow_state")
    offer = data.get("offer")
    start = data.get("start_at")
    term = data.get("term", {})
    term_start = term.get("start_at")
    term_id = data.get("enrollment_term_id")

    if estado != "unpublished":
        print(Fore.GREEN + "✅ El curso ya está publicado.")
        return

    print(Fore.YELLOW + f"\n📌 El curso está sin publicar y con term_id = {term_id}.")
    if not start and not term_start:
        print(Fore.RED + "⛔ El curso NO tiene fechas (ni propias ni en el término).")
        tipo = input("¿Este curso es de Pregrado o Posgrado? (pre/pos): ").strip().lower()
        if tipo == "pre":
            mover_curso_a_subcuenta(course_id, term_id=105, account_id=10)
        elif tipo == "pos":
            mover_curso_a_subcuenta(course_id, term_id=106, account_id=15)
        else:
            print(Fore.RED + "❌ Respuesta inválida.")
    else:
        publicar = input(Fore.YELLOW + "¿Deseas publicar el curso ahora? (s/n): ").strip().lower()
        if publicar == "s":
            publicar_curso(course_id)
        else:
            print(Fore.BLUE + "ℹ️ Publicación cancelada.")

if __name__ == "__main__":
    course_id = input("🆔 Ingrese el ID del curso: ").strip()
    diagnostico_y_ajuste(course_id)
