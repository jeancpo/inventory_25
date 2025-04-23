from . import db
from datetime import datetime

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    alerta_activa = db.Column(db.Boolean, default=False)  # New field for alert activation
    umbral_alerta = db.Column(db.Integer, default=5000)  # New field for alert threshold
    movimientos = db.relationship('Movimiento', backref='producto', lazy=True)

class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'entrada' o 'salida'
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(100), nullable=True)  # New location field

    #producto = db.relationship('Producto', backref=db.backref('movimientos', lazy=True))