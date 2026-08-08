import pytest
from run import app

@pytest.fixture
def client():
    """Cliente de pruebas con contexto de aplicación activo."""
    app.config['TESTING'] = True
    with app.app_context():  
        with app.test_client() as client:
            yield client