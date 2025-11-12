# Sistema de Gestión de Inventario

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.0-green.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.40-red.svg)](https://www.sqlalchemy.org/)

Una aplicación web para la gestión de inventario desarrollada con Flask y SQLAlchemy. Este sistema permite realizar un seguimiento de productos, gestionar movimientos de entrada y salida, y configurar alertas de inventario bajo.

## Características Principales

- 📦 Gestión completa de productos
- 🔄 Control de movimientos de entrada y salida
- 🚨 Alertas de inventario bajo
- 📍 Seguimiento de ubicaciones
- 📊 Visualización de historial de movimientos
- 🔍 Búsqueda y filtrado de productos

## Requisitos del Sistema

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clona el repositorio:
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd inventory_25
   ```

2. Crea y activa un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # En Windows
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración

1. Configura la base de datos:
   - La aplicación utiliza SQLite por defecto, que se creará automáticamente al iniciar la aplicación.
   - El archivo de base de datos se guardará en la carpeta `instance`.

2. Variables de entorno:
   - `FLASK_APP=main.py`
   - `FLASK_ENV=development` (opcional, para modo desarrollo)

## Uso

### Iniciar la aplicación

```bash
python main.py
```

O usa el script de inicio en Windows:
```bash
.\run_app.bat
```

La aplicación estará disponible en `http://localhost:5000`

### Importar datos

Para importar datos desde un archivo CSV:

1. Coloca tu archivo CSV en la carpeta `data/`
2. Ejecuta el script de importación:
   ```bash
   python -m extras.import_data
   ```

## Estructura del Proyecto

```
inventory_25/
├── app/                     # Código fuente de la aplicación
│   ├── __init__.py          # Configuración de la aplicación
│   ├── models.py            # Modelos de datos
│   ├── routes.py            # Rutas de la aplicación
│   ├── static/              # Archivos estáticos (CSS, JS, imágenes)
│   └── templates/           # Plantillas HTML
├── data/                    # Archivos de datos (CSV, etc.)
├── extras/                  # Scripts adicionales
├── instance/                # Base de datos y archivos de instancia
├── tests/                   # Pruebas unitarias
├── .gitignore               # Archivos ignorados por Git
├── main.py                  # Punto de entrada de la aplicación
├── README.md                # Este archivo
├── requirements.txt         # Dependencias del proyecto
└── run_app.bat              # Script para iniciar la aplicación en Windows
```

## Despliegue

Para producción, se recomienda usar un servidor WSGI como Waitress (ya incluido en los requisitos).

```bash
waitress-serve --port=5000 main:app
```

## Licencia

Este proyecto está bajo la licencia MIT.

## Contacto

Si tienes preguntas o sugerencias, por favor abre un issue en el repositorio.
