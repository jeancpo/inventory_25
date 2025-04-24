"""
Este módulo inicializa la aplicación Flask y configura sus componentes principales.

Contiene la configuración básica de la aplicación, incluyendo:
- Configuración de la base de datos
- Inicialización de extensiones
- Registro de rutas
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    """
    Crea y configura la aplicación Flask.
    
    Returns:
        Flask: La aplicación Flask configurada
    """
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar la base de datos
    db.init_app(app)

    with app.app_context():
        # Importar rutas y modelos
        from . import routes, models
        # Crear todas las tablas en la base de datos
        db.create_all()

    # Registrar el blueprint de rutas
    app.register_blueprint(routes.bp)
    
    return app