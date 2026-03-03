"""
Tests de simulación de respuestas HTTP exitosas y errores
Verifica que la aplicación maneja correctamente diferentes escenarios
"""

import pytest
from unittest.mock import patch, MagicMock
import requests


# ============================================================================
# SERVICIOS SIMULADOS
# ============================================================================

class UserAPIClient:
    """Cliente para API de usuarios externa"""
    
    def get_user_profile(self, user_id: int):
        """Obtiene perfil de usuario desde API externa"""
        try:
            response = requests.get(
                f"https://api.example.com/users/{user_id}",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            return {"error": "timeout", "message": "Request timed out"}
        except requests.HTTPError as e:
            return {"error": "http_error", "status_code": e.response.status_code}
        except requests.RequestException:
            return {"error": "connection_error", "message": "Failed to connect"}
    
    def create_user(self, user_data: dict):
        """Crea usuario en API externa"""
        try:
            response = requests.post(
                "https://api.example.com/users",
                json=user_data,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            return {"error": "timeout"}
        except requests.HTTPError as e:
            return {"error": "http_error", "status_code": e.response.status_code}


class ProductCatalogService:
    """Servicio para catálogo de productos externo"""
    
    def search_products(self, query: str):
        """Busca productos en API externa"""
        try:
            response = requests.get(
                "https://api.example.com/products/search",
                params={"q": query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Manejar respuesta vacía
                if not data or not data.get("results"):
                    return {"results": [], "count": 0}
                return data
            elif response.status_code == 500:
                return {"error": "server_error", "message": "Internal server error"}
            elif response.status_code == 404:
                return {"error": "not_found", "message": "Endpoint not found"}
            else:
                return {"error": "unknown", "status_code": response.status_code}
                
        except requests.Timeout:
            return {"error": "timeout", "message": "Search request timed out"}
        except requests.ConnectionError:
            return {"error": "connection_error", "message": "Could not connect to catalog service"}
        except ValueError:  # JSON decode error
            return {"error": "invalid_json", "message": "Invalid response format"}


class NotificationService:
    """Servicio de notificaciones push"""
    
    def send_notification(self, user_id: int, message: str):
        """Envía notificación a usuario"""
        try:
            response = requests.post(
                "https://api.example.com/notifications",
                json={"user_id": user_id, "message": message},
                timeout=3
            )
            
            if response.status_code == 200:
                return {"success": True, "notification_id": response.json().get("id")}
            elif response.status_code == 503:
                return {"success": False, "error": "service_unavailable"}
            else:
                return {"success": False, "error": "failed"}
                
        except requests.Timeout:
            return {"success": False, "error": "timeout"}
        except Exception:
            return {"success": False, "error": "unknown"}


# ============================================================================
# TESTS: RESPUESTAS EXITOSAS
# ============================================================================

class TestSuccessfulResponses:
    """Tests de respuestas HTTP exitosas (200 OK)"""
    
    @patch('requests.get')
    def test_get_user_profile_success(self, mock_get):
        """Simula respuesta exitosa al obtener perfil de usuario"""
        # Configurar mock para respuesta exitosa
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 123,
            "name": "María García",
            "email": "maria@example.com",
            "role": "admin"
        }
        mock_get.return_value = mock_response
        
        # Ejecutar
        client = UserAPIClient()
        result = client.get_user_profile(123)
        
        # Verificar que la aplicación procesa correctamente
        assert result["id"] == 123
        assert result["name"] == "María García"
        assert result["email"] == "maria@example.com"
        assert "error" not in result
        
        # Verificar que se llamó correctamente
        mock_get.assert_called_once()
    
    @patch('requests.post')
    def test_create_user_success(self, mock_post):
        """Simula creación exitosa de usuario"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 456,
            "name": "Juan Pérez",
            "created": True
        }
        mock_post.return_value = mock_response
        
        client = UserAPIClient()
        result = client.create_user({"name": "Juan Pérez", "email": "juan@example.com"})
        
        assert result["id"] == 456
        assert result["created"] is True
        assert "error" not in result
    
    @patch('requests.get')
    def test_search_products_success_with_results(self, mock_get):
        """Simula búsqueda exitosa con resultados"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Producto A", "price": 29.99},
                {"id": 2, "name": "Producto B", "price": 39.99}
            ],
            "count": 2
        }
        mock_get.return_value = mock_response
        
        service = ProductCatalogService()
        result = service.search_products("laptop")
        
        assert result["count"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["name"] == "Producto A"
        assert "error" not in result
    
    @patch('requests.post')
    def test_send_notification_success(self, mock_post):
        """Simula envío exitoso de notificación"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "notif_789", "sent": True}
        mock_post.return_value = mock_response
        
        service = NotificationService()
        result = service.send_notification(123, "Hola!")
        
        assert result["success"] is True
        assert result["notification_id"] == "notif_789"


# ============================================================================
# TESTS: ERRORES HTTP (4xx, 5xx)
# ============================================================================

class TestHTTPErrors:
    """Tests de errores HTTP (400, 404, 500, 503)"""
    
    @patch('requests.get')
    def test_get_user_profile_404_not_found(self, mock_get):
        """Simula error 404 - Usuario no encontrado"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        client = UserAPIClient()
        result = client.get_user_profile(999)
        
        # Verificar que la aplicación maneja el error correctamente
        assert result["error"] == "http_error"
        assert result["status_code"] == 404
    
    @patch('requests.get')
    def test_search_products_500_server_error(self, mock_get):
        """Simula error 500 - Error interno del servidor"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        service = ProductCatalogService()
        result = service.search_products("laptop")
        
        # Verificar manejo de error 500
        assert result["error"] == "server_error"
        assert result["message"] == "Internal server error"
    
    @patch('requests.get')
    def test_search_products_404_endpoint_not_found(self, mock_get):
        """Simula error 404 - Endpoint no existe"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        service = ProductCatalogService()
        result = service.search_products("test")
        
        assert result["error"] == "not_found"
        assert result["message"] == "Endpoint not found"
    
    @patch('requests.post')
    def test_send_notification_503_service_unavailable(self, mock_post):
        """Simula error 503 - Servicio no disponible"""
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_post.return_value = mock_response
        
        service = NotificationService()
        result = service.send_notification(123, "Test")
        
        # Verificar que la aplicación detecta servicio no disponible
        assert result["success"] is False
        assert result["error"] == "service_unavailable"
    
    @patch('requests.post')
    def test_create_user_400_bad_request(self, mock_post):
        """Simula error 400 - Datos inválidos"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_post.return_value = mock_response
        
        client = UserAPIClient()
        result = client.create_user({"invalid": "data"})
        
        assert result["error"] == "http_error"
        assert result["status_code"] == 400


# ============================================================================
# TESTS: TIMEOUT Y ERRORES DE CONEXIÓN
# ============================================================================

class TestTimeoutAndConnectionErrors:
    """Tests de timeout y errores de conexión"""
    
    @patch('requests.get')
    def test_get_user_profile_timeout(self, mock_get):
        """Simula timeout en petición GET"""
        # Configurar mock para lanzar Timeout
        mock_get.side_effect = requests.Timeout("Connection timed out")
        
        client = UserAPIClient()
        result = client.get_user_profile(123)
        
        # Verificar que la aplicación maneja timeout correctamente
        assert result["error"] == "timeout"
        assert result["message"] == "Request timed out"
    
    @patch('requests.post')
    def test_create_user_timeout(self, mock_post):
        """Simula timeout en petición POST"""
        mock_post.side_effect = requests.Timeout("Timeout after 5s")
        
        client = UserAPIClient()
        result = client.create_user({"name": "Test"})
        
        assert result["error"] == "timeout"
    
    @patch('requests.get')
    def test_search_products_timeout(self, mock_get):
        """Simula timeout en búsqueda de productos"""
        mock_get.side_effect = requests.Timeout("Search timeout")
        
        service = ProductCatalogService()
        result = service.search_products("laptop")
        
        assert result["error"] == "timeout"
        assert "timed out" in result["message"].lower()
    
    @patch('requests.get')
    def test_search_products_connection_error(self, mock_get):
        """Simula error de conexión (servidor inalcanzable)"""
        mock_get.side_effect = requests.ConnectionError("Failed to establish connection")
        
        service = ProductCatalogService()
        result = service.search_products("test")
        
        # Verificar que la aplicación detecta error de conexión
        assert result["error"] == "connection_error"
        assert "Could not connect" in result["message"]
    
    @patch('requests.get')
    def test_get_user_general_request_exception(self, mock_get):
        """Simula excepción general de requests"""
        mock_get.side_effect = requests.RequestException("Unknown error")
        
        client = UserAPIClient()
        result = client.get_user_profile(123)
        
        assert result["error"] == "connection_error"
    
    @patch('requests.post')
    def test_send_notification_timeout(self, mock_post):
        """Simula timeout al enviar notificación"""
        mock_post.side_effect = requests.Timeout("Notification timeout")
        
        service = NotificationService()
        result = service.send_notification(123, "Test")
        
        assert result["success"] is False
        assert result["error"] == "timeout"


# ============================================================================
# TESTS: RESPUESTAS VACÍAS Y JSON INVÁLIDO
# ============================================================================

class TestEmptyAndInvalidResponses:
    """Tests de respuestas vacías y JSON malformado"""
    
    @patch('requests.get')
    def test_search_products_empty_response(self, mock_get):
        """Simula respuesta vacía (sin resultados)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [], "count": 0}
        mock_get.return_value = mock_response
        
        service = ProductCatalogService()
        result = service.search_products("nonexistent")
        
        # Verificar que la aplicación maneja respuesta vacía correctamente
        assert result["count"] == 0
        assert result["results"] == []
        assert "error" not in result
    
    @patch('requests.get')
    def test_search_products_null_results(self, mock_get):
        """Simula respuesta con results null"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": None}
        mock_get.return_value = mock_response
        
        service = ProductCatalogService()
        result = service.search_products("test")
        
        # Aplicación debe manejar null como vacío
        assert result["count"] == 0
        assert result["results"] == []
    
    @patch('requests.get')
    def test_search_products_invalid_json(self, mock_get):
        """Simula respuesta con JSON inválido"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        service = ProductCatalogService()
        result = service.search_products("test")
        
        # Verificar que la aplicación detecta JSON inválido
        assert result["error"] == "invalid_json"
        assert result["message"] == "Invalid response format"
    
    @patch('requests.get')
    def test_search_products_missing_fields(self, mock_get):
        """Simula respuesta con campos faltantes"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # Sin 'results' ni 'count'
        mock_get.return_value = mock_response
        
        service = ProductCatalogService()
        result = service.search_products("test")
        
        # Aplicación debe proporcionar valores por defecto
        assert result["count"] == 0
        assert result["results"] == []
    
    @patch('requests.post')
    def test_send_notification_empty_response(self, mock_post):
        """Simula respuesta exitosa pero vacía"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # Sin 'id'
        mock_post.return_value = mock_response
        
        service = NotificationService()
        result = service.send_notification(123, "Test")
        
        # Aplicación debe marcar como exitoso aunque no haya ID
        assert result["success"] is True
        assert result["notification_id"] is None


# ============================================================================
# TESTS: ESCENARIOS COMPLEJOS
# ============================================================================

class TestComplexScenarios:
    """Tests de escenarios complejos combinando múltiples condiciones"""
    
    @patch('requests.get')
    def test_retry_after_timeout(self, mock_get):
        """Simula timeout en primer intento, éxito en segundo"""
        # Primera llamada: timeout, segunda: éxito
        mock_get.side_effect = [
            requests.Timeout("First attempt timeout"),
            MagicMock(
                status_code=200,
                json=lambda: {"id": 123, "name": "Test"}
            )
        ]
        
        client = UserAPIClient()
        
        # Primer intento: timeout
        result1 = client.get_user_profile(123)
        assert result1["error"] == "timeout"
        
        # Segundo intento: éxito
        result2 = client.get_user_profile(123)
        assert result2["id"] == 123
        assert "error" not in result2
    
    @patch('requests.get')
    def test_different_status_codes_handling(self, mock_get):
        """Verifica que la aplicación maneja múltiples códigos HTTP"""
        service = ProductCatalogService()
        
        # Caso 1: 200 OK
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"results": [{"id": 1}], "count": 1}
        )
        result = service.search_products("test")
        assert result["count"] == 1
        
        # Caso 2: 404
        mock_get.return_value = MagicMock(status_code=404)
        result = service.search_products("test")
        assert result["error"] == "not_found"
        
        # Caso 3: 500
        mock_get.return_value = MagicMock(status_code=500)
        result = service.search_products("test")
        assert result["error"] == "server_error"
    
    @patch('requests.post')
    def test_notification_service_resilience(self, mock_post):
        """Verifica resiliencia del servicio de notificaciones"""
        service = NotificationService()
        
        # Caso 1: Éxito
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"id": "123"}
        )
        result = service.send_notification(1, "Test")
        assert result["success"] is True
        
        # Caso 2: Timeout
        mock_post.side_effect = requests.Timeout()
        result = service.send_notification(1, "Test")
        assert result["success"] is False
        assert result["error"] == "timeout"
        
        # Caso 3: 503 Service Unavailable
        mock_post.side_effect = None
        mock_post.return_value = MagicMock(status_code=503)
        result = service.send_notification(1, "Test")
        assert result["success"] is False
        assert result["error"] == "service_unavailable"
