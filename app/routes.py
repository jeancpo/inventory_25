from flask import render_template, request, redirect, url_for
from . import db
from .models import Producto, Movimiento
from datetime import datetime

def register_routes(app):
    @app.route('/')
    def index():
        productos = Producto.query.all()
        return render_template('index.html', productos=productos)

    @app.route('/productos', methods=['GET', 'POST'])
    def productos():
        if request.method == 'POST':
            nombre = request.form['nombre']
            cantidad = request.form['cantidad']
            nuevo_producto = Producto(nombre=nombre, cantidad=int(cantidad))
            db.session.add(nuevo_producto)
            db.session.commit()
            return redirect(url_for('productos'))
        productos = Producto.query.all()
        return render_template('productos.html', productos=productos)

    @app.route('/movimientos', methods=['GET', 'POST'])
    def movimientos():
        if request.method == 'POST':
            tipo = request.form['tipo']
            producto_id = request.form['producto_id']
            cantidad = int(request.form['cantidad'])
            location = request.form.get('location', '')  # Get location from the form
            producto = Producto.query.get(producto_id)

            if tipo == 'entrada':
                producto.cantidad += cantidad
            elif tipo == 'salida' and producto.cantidad >= cantidad:
                producto.cantidad -= cantidad
            else:
                return "Error: cantidad insuficiente", 400

            movimiento = Movimiento(
                producto_id=producto_id, tipo=tipo, cantidad=cantidad, location=location
            )
            db.session.add(movimiento)
            db.session.commit()
            return redirect(url_for('movimientos'))

        productos = Producto.query.all()
        movimientos = Movimiento.query.all()
        return render_template('movimientos.html', productos=productos, movimientos=movimientos)

    @app.route('/reportes')
    def reportes():
        filtro = request.args.get('filtro', 'dia')
        today = datetime.utcnow()

        if filtro == 'rango':
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            
            if not fecha_inicio or not fecha_fin:
                return "Error: Se requieren ambas fechas para el rango", 400
                
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
                
                if fecha_inicio > fecha_fin:
                    return "Error: La fecha inicial no puede ser mayor que la fecha final", 400
                    
                movimientos = Movimiento.query.filter(
                    db.func.date(Movimiento.fecha) >= fecha_inicio.date(),
                    db.func.date(Movimiento.fecha) <= fecha_fin.date()
                ).all()
            except ValueError:
                return "Error: Formato de fecha inválido", 400
                
        elif filtro == 'dia':
            movimientos = Movimiento.query.filter(
                db.func.date(Movimiento.fecha) == today.date()
            ).all()
        elif filtro == 'mes':
            movimientos = Movimiento.query.filter(
                db.extract('month', Movimiento.fecha) == today.month
            ).all()
        else:
            movimientos = Movimiento.query.all()
        
        return render_template('reportes.html', movimientos=movimientos)