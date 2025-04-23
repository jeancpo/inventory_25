import os
import sys
import pytest
from datetime import datetime, timedelta, timezone

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Producto, Movimiento

# Fixtures
@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def session(app):
    """Creates a new database session for a test."""
    with app.app_context():
        yield db.session

@pytest.fixture
def sample_product(app, session):
    """Create a sample product for testing."""
    with app.app_context():
        product = Producto(nombre='Test Product', cantidad=100)
        session.add(product)
        session.commit()
        return product.id  # <-- retorna el ID

@pytest.fixture
def sample_movement(app, session, sample_product):
    """Create a sample movement for testing."""
    with app.app_context():
        movement = Movimiento(
            producto_id=sample_product,
            tipo='entrada',
            cantidad=50,
            fecha=datetime.now(timezone.utc),
            location='Warehouse A'
        )
        session.add(movement)
        session.commit()
        return movement.id  # <-- retorna el ID

# Test Classes
class TestProductOperations:
    """Tests for product-related operations."""
    
    def test_create_product(self, client, session):
        # Test valid product creation
        response = client.post('/productos', data={
            'nombre': 'New Product',
            'cantidad': '50'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Verify product was created
        product = session.execute(db.select(Producto)).scalar_one()
        assert product.nombre == 'New Product'
        assert product.cantidad == 50

    def test_create_product_edge_cases(self, client):
        # Test max length name
        long_name = 'A' * 100
        response = client.post('/productos', data={
            'nombre': long_name,
            'cantidad': '10'
        })
        assert response.status_code == 302
        
        # Test special characters in name
        response = client.post('/productos', data={
            'nombre': 'Product @#$%',
            'cantidad': '10'
        })
        assert response.status_code == 302

    def test_invalid_product_creation(self, client, session):
        # Test negative quantity
        response = client.post('/productos', data={
            'nombre': 'Invalid',
            'cantidad': '-10'
        }, follow_redirects=False)
        assert response.status_code == 400  # Should redirect with flash message
        
        # Test empty name
        response = client.post('/productos', data={
            'nombre': '',
            'cantidad': '10'
        }, follow_redirects=False)
        assert response.status_code == 400
        
        # Test non-numeric quantity
        response = client.post('/productos', data={
            'nombre': 'Test',
            'cantidad': 'abc'
        }, follow_redirects=False)
        assert response.status_code == 400

class TestMovementOperations:
    """Tests for movement-related operations."""
    
    def test_create_entrada(self, client, session, sample_product):
        with client.application.app_context():
            product = session.get(Producto, sample_product)
            initial_quantity = product.cantidad
            response = client.post('/movimientos', data={
                'producto_id': product.id,
                'tipo': 'entrada',
                'cantidad': '20',
                'location': 'Warehouse A'
            }, follow_redirects=True)
            assert response.status_code == 200
            session.refresh(product)
            assert product.cantidad == initial_quantity + 20

    def test_create_salida(self, client, session, sample_product):
        with client.application.app_context():
            product = session.get(Producto, sample_product)
            initial_quantity = product.cantidad
            
            response = client.post('/movimientos', data={
                'producto_id': product.id,
                'tipo': 'salida',
                'cantidad': '30',
                'location': 'Store B'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            session.refresh(product)
            assert product.cantidad == initial_quantity - 30

    def test_insufficient_stock(self, client, session, sample_product):
        with client.application.app_context():
            response = client.post('/movimientos', data={
                'producto_id': sample_product,
                'tipo': 'salida',
                'cantidad': '150',
                'location': 'Store C'
            })
            assert response.status_code == 400

    def test_movement_validation(self, client, session, sample_product):
        with client.application.app_context():
            # Test invalid quantity
            response = client.post('/movimientos', data={
                'producto_id': sample_product,
                'tipo': 'entrada',
                'cantidad': '-10',
                'location': 'Warehouse D'
            })
            assert response.status_code == 400
            
            # Test missing location
            response = client.post('/movimientos', data={
                'producto_id': sample_product,
                'tipo': 'entrada',
                'cantidad': '50',
                'location': ''
            })
            assert response.status_code == 400
            
            # Test invalid movement type
            response = client.post('/movimientos', data={
                'producto_id': sample_product,
                'tipo': 'invalid',
                'cantidad': '50',
                'location': 'Warehouse E'
            })
            assert response.status_code == 400

class TestReportGeneration:
    """Tests for report generation functionality."""
    
    def test_daily_report(self, client, sample_movement):
        response = client.get('/reportes?filtro=dia')
        assert response.status_code == 200
        assert b"Test Product" in response.data
        
    def test_monthly_report(self, client, sample_movement):
        response = client.get('/reportes?filtro=mes')
        assert response.status_code == 200
        
    def test_date_range_report(self, client, sample_movement):
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)
        
        response = client.get(f'/reportes?filtro=rango&fecha_inicio={yesterday}&fecha_fin={today}')
        assert response.status_code == 200
        
    def test_invalid_date_range(self, client):
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)
        
        # Test reversed dates
        response = client.get(f'/reportes?filtro=rango&fecha_inicio={today}&fecha_fin={yesterday}')
        assert response.status_code == 400
        
        # Test invalid date format
        response = client.get('/reportes?filtro=rango&fecha_inicio=invalid&fecha_fin=dates')
        assert response.status_code == 400

class TestUIEndpoints:
    """Tests for basic UI endpoints."""
    
    def test_index_page(self, client):
        response = client.get('/')
        assert response.status_code == 200
        
    def test_productos_page(self, client):
        response = client.get('/productos')
        assert response.status_code == 200
        
    def test_movimientos_page(self, client):
        response = client.get('/movimientos')
        assert response.status_code == 200
        
    def test_reportes_page(self, client):
        response = client.get('/reportes')
        assert response.status_code == 200