"""
Archivo principal de la aplicación de inventario.

Este archivo inicializa y ejecuta la aplicación Flask.
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    """
    Punto de entrada principal de la aplicación.
    
    Ejecuta la aplicación Flask en modo desarrollo.
    """
    app.run(host='0.0.0.0', port=5000, debug=True)