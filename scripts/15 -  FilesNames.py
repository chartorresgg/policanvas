import os
import pandas as pd

# Ruta de la carpeta
ruta = "C:/Users/ceguzman\OneDrive - Poli\OneDrive - Politécnico Grancolombiano\Planes de estudio\FNGS\Escuela de administración y competitividad\Pregrado\Virtual"

# Obtener los nombres de los archivos
archivos = os.listdir(ruta)

# Crear un DataFrame
df = pd.DataFrame(archivos, columns=["Nombre del Archivo"])

# Guardar en Excel
df.to_excel("lista_archivos.xlsx", index=False)

print("Tabla generada y guardada en lista_archivos.xlsx")