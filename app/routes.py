"""
Este módulo contiene las rutas principales de la aplicación de inventario.

Rutas disponibles:
- /: Página principal con estadísticas y gráficos
- /productos: Gestión de productos
- /movimientos: Registro y gestión de movimientos
- /reportes: Generación de reportes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta, time
from .models import db, Producto, Movimiento
from sqlalchemy import func
import pytz

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """
    Muestra la página principal con estadísticas y gráficos.
    
    Genera datos para:
    1. Movimientos totales por día (últimos 5 días)
    2. Localidad con más salidas por día
    3. Producto con más movimientos en la última semana
    4. Productos con stock crítico
    
    Returns:
        render_template: Template con los datos calculados
    """
    caracas = pytz.timezone("America/Caracas")
    today_caracas = datetime.now(caracas).date()
    dias = [today_caracas - timedelta(days=i) for i in range(4, -1, -1)]
    movimientos_por_dia = []

    for dia in dias:
        # Get the UTC range for this local day
        start_local = caracas.localize(datetime.combine(dia, time.min))
        end_local = caracas.localize(datetime.combine(dia, time.max))
        start_utc = start_local.astimezone(pytz.utc)
        end_utc = end_local.astimezone(pytz.utc)
        count = db.session.query(func.count(Movimiento.id)).filter(
            Movimiento.fecha >= start_utc,
            Movimiento.fecha <= end_utc
        ).scalar()
        movimientos_por_dia.append({'fecha': dia.strftime('%Y-%m-%d'), 'total': count})

    # 2. Localidad con más salidas por día (últimos 5 días)
    localidad_top_salidas = []
    for dia in dias:
        result = db.session.query(
            Movimiento.location,
            func.sum(Movimiento.cantidad).label('total_salidas')
        ).filter(
            func.date(Movimiento.fecha) == dia,
            Movimiento.tipo == 'salida'
        ).group_by(Movimiento.location).order_by(func.sum(Movimiento.cantidad).desc()).first()
        if result:
            localidad_top_salidas.append({'fecha': dia.strftime('%Y-%m-%d'), 'localidad': result[0], 'salidas': result[1]})
        else:
            localidad_top_salidas.append({'fecha': dia.strftime('%Y-%m-%d'), 'localidad': None, 'salidas': 0})

    # 3. Producto con más movimientos en la última semana
    semana_inicio = today_caracas - timedelta(days=6)
    producto_mas_mov = db.session.query(
        Producto.nombre,
        func.sum(Movimiento.cantidad).label('total_mov')
    ).join(Movimiento).filter(
        Movimiento.fecha >= semana_inicio,
        Movimiento.fecha <= today_caracas + timedelta(days=1)
    ).group_by(Producto.id).order_by(func.sum(Movimiento.cantidad).desc()).first()
    if producto_mas_mov:
        producto_mas_mov = {'nombre': producto_mas_mov[0], 'total': producto_mas_mov[1]}
    else:
        producto_mas_mov = {'nombre': None, 'total': 0}

    # 4. Productos con stock crítico (cantidad < 5)
    productos_alerta = db.session.query(Producto).filter(
    Producto.alerta_activa == True,
    Producto.cantidad < Producto.umbral_alerta
).all()

    # 5. Productos agregados por semana (requiere campo fecha_creacion)
    # Si tienes fecha_creacion en Producto, descomenta y usa este bloque:
    # semanas = []
    # productos_por_semana = []
    # for i in range(7, -1, -1):
    #     semana_inicio = today_caracas - timedelta(days=today_caracas.weekday() + i*7)
    #     semana_fin = semana_inicio + timedelta(days=6)
    #     count = db.session.query(func.count(Producto.id)).filter(
    #         Producto.fecha_creacion >= semana_inicio,
    #         Producto.fecha_creacion <= semana_fin
    #     ).scalar()
    #     semanas.append(f"{semana_inicio.strftime('%Y-%m-%d')} a {semana_fin.strftime('%Y-%m-%d')}")
    #     productos_por_semana.append(count)
    # Como no hay campo fecha_creacion, se omite este gráfico.

    return render_template(
        'index.html',
        movimientos_por_dia=movimientos_por_dia,
        localidad_top_salidas=localidad_top_salidas,
        producto_mas_mov=producto_mas_mov,
        productos_alerta=productos_alerta,
        today=today_caracas
        # productos_por_semana=productos_por_semana, semanas=semanas  # solo si tienes fecha_creacion
    )

@bp.route('/productos', methods=['GET', 'POST'])
def productos():
    """
    Gestión de productos.
    
    GET: Muestra la lista de productos
    POST: Agrega un nuevo producto
    
    Returns:
        GET: render_template con la lista de productos
        POST: redirección a la lista de productos
    """
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        
        # Validar que la cantidad no sea negativa
        if cantidad < 0:
            flash('La cantidad no puede ser negativa', 'error')
            return redirect(url_for('main.productos'))
            
        nuevo_producto = Producto(nombre=nombre, cantidad=cantidad)
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('main.productos'))
    
    # Get all products with alert status
    productos = db.session.query(Producto).all()
    return render_template('productos.html', productos=productos)

@bp.route('/actualizar_alerta/<int:producto_id>', methods=['POST'])
def actualizar_alerta(producto_id):
    """
    Actualiza el estado de alerta de un producto.
    
    Args:
        producto_id (int): ID del producto a actualizar
    
    Returns:
        redirect: Redirección a la lista de productos
    """
    producto = Producto.query.get_or_404(producto_id)
    producto.alerta_activa = request.form.get('alerta_activa') == 'true'
    producto.umbral_alerta = int(request.form.get('umbral_alerta', 5000))
    db.session.commit()
    return redirect(url_for('main.productos'))

@bp.route('/actualizar_producto', methods=['POST'])
def actualizar_producto():
    """
    Actualiza los datos de un producto existente.
    
    Returns:
        redirect: Redirección a la lista de productos
    """
    producto_id = request.form.get('producto_id')
    cantidad = int(request.form.get('cantidad'))
    alerta_activa = request.form.get('alerta_activa') == 'on'
    umbral_alerta = int(request.form.get('umbral_alerta'))
    
    producto = Producto.query.get_or_404(producto_id)
    producto.cantidad = cantidad
    producto.alerta_activa = alerta_activa
    producto.umbral_alerta = umbral_alerta
    db.session.commit()
    
    return redirect(url_for('main.productos'))

@bp.route('/movimientos', methods=['GET', 'POST'])
def movimientos():
    """
    Gestión de movimientos de inventario.
    
    GET: Muestra la lista de movimientos
    POST: Registra un nuevo movimiento
    
    Returns:
        GET: render_template con la lista de movimientos
        POST: redirección a la lista de movimientos
    """
    if request.method == "POST":
        producto_id = request.form.get('producto_id', '').strip()
        tipo = request.form.get('tipo', '').strip()
        cantidad = request.form.get('cantidad', '').strip()
        location = request.form.get('location', '').strip()
        if not producto_id or not producto_id.isdigit():
            return "Error: Seleccione un producto válido.", 400
        if tipo not in ("entrada", "salida"):
            return "Error: Tipo de movimiento inválido.", 400
        if not cantidad or not cantidad.isdigit() or int(cantidad) <= 0:
            return "Error: La cantidad debe ser un número entero positivo y mayor a cero.", 400
        if not location:
            return "Error: La ubicación es obligatoria.", 400
        producto = db.session.get(Producto, int(producto_id))
        if not producto:
            return "Error: Producto no encontrado.", 404
        cantidad = int(cantidad)
        if tipo == "salida" and producto.cantidad < cantidad:
            return "Error: Stock insuficiente.", 400
        if tipo == "salida":
            producto.cantidad -= cantidad
        else:  # tipo == "entrada"
            producto.cantidad += cantidad
        movimiento = Movimiento(
            producto_id=producto.id,
            tipo=tipo,
            cantidad=cantidad,
            fecha=datetime.now(),
            location=location
        )
        db.session.add(movimiento)
        db.session.commit()
        return redirect(url_for('main.movimientos'))
    productos = db.session.execute(db.select(Producto)).scalars().all()
    movimientos = db.session.execute(db.select(Movimiento)).scalars().all()
    return render_template('movimientos.html', productos=productos, movimientos=movimientos)

@bp.route('/actualizar_movimiento', methods=['POST'])
def actualizar_movimiento():
    """
    Actualiza los datos de un movimiento existente.
    
    Returns:
        redirect: Redirección a la lista de movimientos
    """
    movimiento_id = request.form.get('movimiento_id')
    producto_id = int(request.form.get('producto_id'))
    tipo = request.form.get('tipo')
    cantidad = int(request.form.get('cantidad'))
    location = request.form.get('location')
    
    movimiento = Movimiento.query.get_or_404(movimiento_id)
    
    # Update movement details
    movimiento.producto_id = producto_id
    movimiento.tipo = tipo
    movimiento.cantidad = cantidad
    movimiento.location = location
    
    # Update product quantity
    producto = Producto.query.get_or_404(producto_id)
    if tipo == 'entrada':
        producto.cantidad += cantidad
    else:  # salida
        producto.cantidad -= cantidad
    
    db.session.commit()
    
    return redirect(url_for('main.movimientos'))

@bp.route('/reportes')
def reportes():
    """
    Genera reportes de inventario.
    
    Returns:
        render_template: Template con los reportes generados
    """
    filtro = request.args.get('filtro', 'dia')
    today = datetime.now()
    movimientos = []
    error = None

    if filtro == 'rango':
        fecha_inicio = request.args.get('fecha_inicio', '').strip()
        fecha_fin = request.args.get('fecha_fin', '').strip()
        if not fecha_inicio or not fecha_fin:
            error = "Se requieren ambas fechas para el rango"
        else:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
                if fecha_inicio_dt > fecha_fin_dt:
                    error = "La fecha inicial no puede ser mayor que la fecha final"
                else:
                    stmt = db.select(Movimiento).where(
                        db.func.date(Movimiento.fecha) >= fecha_inicio_dt.date(),
                        db.func.date(Movimiento.fecha) <= fecha_fin_dt.date()
                    )
                    movimientos = db.session.execute(stmt).scalars().all()
            except ValueError:
                error = "Formato de fecha inválido"
    elif filtro == 'dia':
        stmt = db.select(Movimiento).where(
            db.func.date(Movimiento.fecha) == today.date()
        )
        movimientos = db.session.execute(stmt).scalars().all()
    elif filtro == 'mes':
        stmt = db.select(Movimiento).where(
            db.extract('month', Movimiento.fecha) == today.month
        )
        movimientos = db.session.execute(stmt).scalars().all()
    else:
        movimientos = db.session.execute(db.select(Movimiento)).scalars().all()

    return render_template(
        'reportes.html',
        movimientos=movimientos,
        filtro=filtro,
        fecha=today,
        error=error
    ), (400 if error else 200)