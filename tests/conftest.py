"""
Fixtures compartidas para todos los tests de pytest
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """
    Cliente de test de FastAPI
    Fixture reutilizable para todos los tests
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def api_headers():
    """
    Headers comunes para las peticiones API
    """
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


@pytest.fixture
def sample_item():
    """
    Item de ejemplo para tests
    """
    return {
        "id": 1,
        "name": "Test Item",
        "description": "Item de prueba"
    }


@pytest.fixture(autouse=True)
def reset_rate_limit():
    """
    Resetear el rate limit entre tests
    """
    from app.main import rate_limit_storage
    rate_limit_storage.clear()
    yield
    rate_limit_storage.clear()
