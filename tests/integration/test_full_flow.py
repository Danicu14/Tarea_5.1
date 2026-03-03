"""
Tests de integración - Flujo completo de datos entre capas
Verifica interacción entre controladores, servicios y middlewares
"""
import pytest
from fastapi import status


class TestDataFlowIntegration:
    """Tests de flujo de datos entre capas"""
    
    @pytest.mark.integration
    def test_items_endpoint_data_flow(self, client):
        """Test flujo: Request → Controlador → Datos → Response"""
        response = client.get("/api/items")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        #Verificar que los datos fluyen correctamente por las capas
        assert "items" in data
        assert isinstance(data["items"], list)
        assert len(data["items"]) > 0
        assert "id" in data["items"][0]
        assert "name" in data["items"][0]
    
    @pytest.mark.integration
    def test_single_item_data_flow(self, client):
        """Test flujo: Request con parámetro → Procesamiento → Response"""
        response = client.get("/api/items/1")
        
        assert response.status_code == status.HTTP_200_OK
        item = response.json()
        
        # Verificar estructura de datos entre capas
        assert item["id"] == 1
        assert "name" in item
        assert "description" in item


class TestServiceLayerIntegration:
    """Tests de integración entre servicios"""
    
    @pytest.mark.integration
    def test_config_service_communication(self, client):
        """Test comunicación: Endpoint → Servicio de Config → Response"""
        response = client.get("/api/info")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verificar que el servicio de config se integra correctamente
        assert "environment" in data
        assert data["environment"] in ["development", "production", "testing"]
        assert "name" in data
        assert "version" in data
    
    @pytest.mark.integration
    def test_health_service_integration(self, client):
        """Test comunicación: Endpoint → Servicio Health → Response"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verificar integración del servicio de health
        assert data["status"] == "healthy"
        assert "environment" in data


class TestMiddlewareIntegration:
    """Tests de integración de middlewares"""
    
    @pytest.mark.integration
    @pytest.mark.security
    def test_security_middleware_integration(self, client):
        """Test: Request → Security Middleware → Response"""
        response = client.get("/health")
        
        # Verificar que el middleware de seguridad se aplica
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
    
    @pytest.mark.integration
    def test_cors_middleware_integration(self, client):
        """Test: Request → CORS Middleware → Response"""
        response = client.options("/api/items", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        
        # Verificar integración de CORS
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.integration
    def test_rate_limit_middleware_integration(self, client, reset_rate_limit):
        """Test: Request → Rate Limit Middleware → Response"""
        # Hacer requests normales (dentro del límite)
        responses = []
        for _ in range(10):
            response = client.get("/health")
            responses.append(response.status_code)
        
        # El middleware debe permitir tráfico normal
        assert all(code == 200 for code in responses)


class TestCompleteFlowIntegration:
    """Tests de flujos completos extremo a extremo"""
    
    @pytest.mark.integration
    def test_full_request_response_cycle(self, client):
        """Test flujo completo: Request → Todas las capas → Response"""
        # PASO 1: Request pasa por middlewares
        response = client.get("/api/items")
        
        # PASO 2: Verifica que pasó por security middleware
        assert "X-Content-Type-Options" in response.headers
        
        # PASO 3: Verifica que el controlador procesó la request
        assert response.status_code == status.HTTP_200_OK
        
        # PASO 4: Verifica que los datos se serializaron correctamente
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
    
    @pytest.mark.integration
    def test_error_propagation_through_layers(self, client):
        """Test propagación de errores: Error → Capas → Response"""
        # Intentar acceder a endpoint inexistente
        response = client.get("/api/nonexistent")
        
        # El error debe propagarse correctamente
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error = response.json()
        
        # Verificar estructura de error
        assert "error" in error or "message" in error


class TestDatabaseInteraction:
    """Tests de interacción con capa de datos"""
    
    @pytest.mark.integration
    def test_data_retrieval_integration(self, client):
        """Test: Controlador → Data Layer → Serialización"""
        response = client.get("/api/items")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verificar que los datos se recuperan y serializan correctamente
        assert "items" in data
        items = data["items"]
        assert len(items) > 0
        
        # Verificar estructura de cada item
        for item in items:
            assert "id" in item
            assert "name" in item
    
    @pytest.mark.integration
    def test_parameterized_data_query(self, client):
        """Test: Query params → Data Layer → Filtered Response"""
        # Request con parámetros
        response = client.get("/api/items?limit=5&offset=0")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verificar que los parámetros fluyen correctamente
        assert "items" in data
