"""
Tests de integración para endpoints de la API
Los tests de integración verifican que múltiples componentes funcionen juntos
"""
import pytest
from fastapi import status


class TestHealthEndpoint:
    """Tests de integración del endpoint /health"""
    
    @pytest.mark.integration
    def test_health_check_integration(self, client):
        """El health check debe responder correctamente"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data
        assert "version" in data
    
    @pytest.mark.smoke
    def test_health_check_response_time(self, client):
        """El health check debe responder rápidamente"""
        response = client.get("/health")
        
        # Verificar header de tiempo de procesamiento
        assert "X-Process-Time" in response.headers
        process_time = float(response.headers["X-Process-Time"])
        assert process_time < 1.0  # Menos de 1 segundo


class TestAPIInfoEndpoint:
    """Tests de integración del endpoint /api/info"""
    
    @pytest.mark.integration
    def test_api_info_complete(self, client):
        """El endpoint de info debe retornar toda la información"""
        response = client.get("/api/info")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "environment" in data


class TestItemsEndpoint:
    """Tests de integración de endpoints de items"""
    
    @pytest.mark.integration
    def test_get_all_items(self, client):
        """Debe retornar lista de items"""
        response = client.get("/api/items")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
    
    @pytest.mark.integration
    def test_get_single_item(self, client):
        """Debe retornar un item específico"""
        item_id = 1
        response = client.get(f"/api/items/{item_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == item_id
        assert "name" in data


class TestSecurityHeaders:
    """Tests de integración de headers de seguridad"""
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_security_headers_present(self, client):
        """Debe incluir headers de seguridad"""
        response = client.get("/health")
        
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
    
    @pytest.mark.security
    @pytest.mark.integration
    def test_rate_limit_headers(self, client):
        """Debe incluir headers de rate limiting"""
        response = client.get("/health")
        
        assert "X-RateLimit-Limit" in response.headers


class TestErrorHandling:
    """Tests de manejo de errores"""
    
    @pytest.mark.integration
    def test_404_handling(self, client):
        """Debe manejar correctamente rutas no existentes"""
        response = client.get("/ruta/inexistente")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data
        assert "message" in data
    
    @pytest.mark.integration
    def test_rate_limit_error(self, client, monkeypatch):
        """Debe retornar 429 cuando se excede el rate limit"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_per_minute', 2)
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        # Hacer múltiples requests
        for _ in range(2):
            client.get("/health")
        
        # El siguiente debe fallar
        response = client.get("/health")
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
