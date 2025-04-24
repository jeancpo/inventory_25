"""
Este módulo contiene los modelos de datos para la aplicación de inventario.

Los modelos representan las entidades principales del sistema:
- Producto: Representa un producto en el inventario
- Movimiento: Representa movimientos de entrada/salida de productos
"""
from . import db
from datetime import datetime

class Producto(db.Model):
    """
    Modelo que representa un producto en el inventario.

    Atributos:
        id (int): Identificador único del producto
        nombre (str): Nombre del producto (requerido)
        cantidad (int): Cantidad actual en stock (requerido)
        alerta_activa (bool): Indica si el producto tiene alerta activa
        umbral_alerta (int): Umbral de cantidad que activa la alerta
        movimientos (relationship): Relación con los movimientos del producto
    """
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    alerta_activa = db.Column(db.Boolean, default=False)  # New field for alert activation
    umbral_alerta = db.Column(db.Integer, default=5000)  # New field for alert threshold
    movimientos = db.relationship('Movimiento', backref='producto', lazy=True)

class Movimiento(db.Model):
    """
    Modelo que representa un movimiento de inventario.

    Atributos:
        id (int): Identificador único del movimiento
        producto_id (int): Referencia al producto involucrado
        tipo (str): Tipo de movimiento ('entrada' o 'salida')
        cantidad (int): Cantidad movida
        fecha (datetime): Fecha y hora del movimiento
        location (str): Ubicación física del movimiento
        producto (relationship): Relación inversa con el producto
    """
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'entrada' o 'salida'
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(100), nullable=True)  # New location field
