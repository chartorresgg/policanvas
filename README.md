# Canvas LMS Automation Project

Este proyecto tiene como objetivo automatizar acciones y procesos dentro del entorno Canvas LMS utilizando su API oficial. A través de scripts desarrollados en Python, se busca optimizar tareas como la gestión de cursos, usuarios, actividades, configuraciones y análisis de datos.
La automatización de estos procesos permitirá a los usuarios ahorrar tiempo y reducir errores manuales, mejorando la eficiencia en la ejecución de 
estos procesos y permitiendo pensar de manera más estratégica en otros proyectos de alto valor.
---

## ✨ Objetivos del Proyecto

- Automatizar tareas, optimizar tiempos y reducir errores en la gestión de Canvas LMS.
- Invertir menos tiempo en tareas manuales y más, en proyectos estratégicos de alto valor.
- Hacer uso de la API de Canvas LMS para gestionar los recursos de manera eficiente.
- Facilitar la consulta y modificación de cursos, actividades, usuarios y configuraciones.
- Generar reportes y análisis de datos académicos.
- Establecer una arquitectura modular escalable y reutilizable.

---

## 📁 Estructura del Proyecto

```
canvas_automation_project/
│
├── controllers/              # Lógica de negocio
├── data/                     # Almacenamiento temporal de archivos
├── docs/                     # Documentación del proyecto
├── models/                   # Conexiones API y representación de datos
├── scripts/                  # Scripts automáticos para tareas específicas
├── tests/                    # Pruebas unitarias
├── utils/                    # Funciones auxiliares (auth, config, fechas)
├── requirements.txt          # Dependencias del proyecto
├── README.md                 # Descripción del proyecto
```

---

## 🚀 Tecnologías usadas

- **Python 3.9+**
- **Canvas LMS API REST**
- **VS Code** y **PyCharm** como IDE's recomendados
- **Git** para control de versiones
- **Postman** (opcional para pruebas de API)
- **Bibliotecas recomendadas**:

  - `requests` (consumo de API)
  - `pandas` (análisis de datos)
  - `logging` (gestión de logs)
  - `argparse` (opcional para CLI)

---

## 📚 Casos de Uso

### 1. Gestión de Cursos y BluePrint
- ***Creación de cursos:*** Automatizar la creación de cursos en Canvas LMS con configuraciones predefinidas.
- ***Actualización de cursos:*** Modificar configuraciones de cursos existentes, como fechas, funcionalidades y permisos.
- ***Creación de cursos BluePrint:*** Creación de cursos Máster o BluePrint con contenidos específicos para ser replicados en otros cursos.
- ***Renombrar cursos:*** Cambiar el nombre de los cursos según las definiciones de la institución.
- ***Actualización de contenidos:*** Actualizar contenidos de cursos, como archivos, páginas y actividades.
- ***Gestión de configuraciones:*** Modificar configuraciones de cursos, como permisos, visibilidad y funcionalidades.

### 2. Gestión de usuarios
- ***Matriculación de usuarios:*** Automatizar la matriculación de usuarios en diferentes cursos con roles específicos.
- ***Modificación de roles:*** Cambiar roles de usuarios en cursos, como estudiante, profesor o administrador.
- ***Desmatriculación de usuarios:*** Eliminar usuarios de cursos específicos.
- ***Consulta de usuarios:*** Consultar información de usuarios, como roles, cursos y actividades.
- ***Exportación de usuarios:*** Exportar información de usuarios a archivos CSV o Excel para análisis posterior.
- ***Creación de subgrupos:*** Crear subgrupos de usuarios dentro de un curso para facilitar la gestión de actividades colaborativas.

### 3. Gestión de actividades
- ***Actualización de actividades:*** Modificar configuraciones de actividades, como fechas, permisos, configuraciones e intentos.
- ***Ampliación de actividades:*** Ampliar actividades existentes con nuevas configuraciones o contenidos, para diferentes cursos y usuarios.
- ***Renombrar actividades:*** Cambiar el nombre de las actividades según las definiciones de la institución.
- ***Cargue de rúbricas:*** Cargar rúbricas para actividades específicas, facilitando la evaluación de los estudiantes.
- ***Asignación de subgrupos:*** Asignar subgrupos de estudiantes a actividades específicas, para facilitar la gestión de grupos en actividades colaborativas.
- ***Fechas de actividades:*** Actualizar fechas de actividades, como fechas de entrega, inicio y cierre.
- ***Actividades de Ciencias Básicas:*** Crear y gestionar actividades específicas para cursos de Ciencias Básicas, como Física, Química y Biología.

### 4. Consultas y reportes
- ***Generación de reportes:*** Generación de reportes detallados de ejecución de cada script.
---

## ⚙️ Próximos Pasos

- [ ] Documentar cada script y función.
- [ ] Implementar cliente de autenticación con token.
- [ ] Desarrollar controladores por tipo de entidad (curso, actividad, usuario).
- [ ] Crear scripts reutilizables.
- [ ] Configurar pruebas unitarias.
- 

---

## 🌟 Autor

**Carlos Eduardo Guzmán Torres**
Ingeniero de Sistemas y Analista de Datos.

---

## 📝 Licencia

Este proyecto es de uso interno y educativo. Su distribución externa debe ser autorizada.
