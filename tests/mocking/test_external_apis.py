"""
Tests de Mocking - Simulación de APIs Externas
===============================================

Simula llamadas a APIs de terceros para aislar dependencias externas
y evitar dependencia de servicios reales durante las pruebas.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


# ============================================================================
# MOCK DE API EXTERNA - Servicio de Clima
# ============================================================================

class WeatherAPIClient:
    """Cliente simulado para API de clima externa"""
    
    def get_current_weather(self, city: str):
        """Simula llamada a API externa de clima"""
        # En producción, esto haría una llamada HTTP real
        import requests
        response = requests.get(f"https://api.weather.com/v1/current?city={city}")
        return response.json()
    
    def get_forecast(self, city: str, days: int = 5):
        """Obtiene pronóstico del clima"""
        import requests
        response = requests.get(f"https://api.weather.com/v1/forecast?city={city}&days={days}")
        return response.json()


class TestWeatherApiMocking:
    """Tests con mocking de API externa de clima"""
    
    @patch('requests.get')
    def test_get_current_weather_success(self, mock_get):
        """
        Mock de API externa: Simulamos respuesta exitosa de API de clima
        
        ¿Por qué es necesario?
        - No dependemos de servicio externo (puede estar caído)
        - Tests rápidos (sin latencia de red)
        - No consumimos cuota de API
        - Tests predecibles (misma respuesta siempre)
        """
        # ARRANGE: Configurar el mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "city": "Madrid",
            "temperature": 22.5,
            "condition": "Sunny",
            "humidity": 45
        }
        mock_get.return_value = mock_response
        
        # ACT: Ejecutar código que usa la API
        client = WeatherAPIClient()
        result = client.get_current_weather("Madrid")
        
        # ASSERT: Verificar que se usó correctamente el mock
        assert result["city"] == "Madrid"
        assert result["temperature"] == 22.5
        assert result["condition"] == "Sunny"
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_weather_api_failure(self, mock_get):
        """
        Mock de fallo de API: Simulamos error de servicio externo
        
        Beneficio: Podemos probar manejo de errores sin que la API falle realmente
        """
        # ARRANGE: Simular error de API
        mock_get.side_effect = Exception("API Unavailable")
        
        # ACT & ASSERT: Verificar manejo de error
        client = WeatherAPIClient()
        with pytest.raises(Exception, match="API Unavailable"):
            client.get_current_weather("Madrid")
    
    @patch('requests.get')
    def test_get_forecast_with_days(self, mock_get):
        """Mock de API con parámetros específicos"""
        # ARRANGE
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "city": "Barcelona",
            "forecast": [
                {"day": 1, "temp": 20, "condition": "Cloudy"},
                {"day": 2, "temp": 22, "condition": "Sunny"},
                {"day": 3, "temp": 19, "condition": "Rainy"}
            ]
        }
        mock_get.return_value = mock_response
        
        # ACT
        client = WeatherAPIClient()
        result = client.get_forecast("Barcelona", days=3)
        
        # ASSERT
        assert len(result["forecast"]) == 3
        assert result["city"] == "Barcelona"
        mock_get.assert_called_with("https://api.weather.com/v1/forecast?city=Barcelona&days=3")


# ============================================================================
# MOCK DE API DE PAGOS - Stripe/PayPal Simulado
# ============================================================================

class PaymentGateway:
    """Gateway de pagos simulado"""
    
    def process_payment(self, amount: float, card_token: str):
        """Procesa un pago (simulación)"""
        # En producción, esto llamaría a Stripe/PayPal
        import requests
        response = requests.post(
            "https://api.stripe.com/v1/charges",
            json={"amount": amount, "token": card_token}
        )
        return response.json()
    
    def refund_payment(self, charge_id: str):
        """Reembolsa un pago"""
        import requests
        response = requests.post(
            f"https://api.stripe.com/v1/refunds",
            json={"charge": charge_id}
        )
        return response.json()


class TestPaymentGatewayMocking:
    """Tests con mocking de gateway de pagos"""
    
    @patch('requests.post')
    def test_process_payment_success(self, mock_post):
        """
        Mock de procesamiento de pago exitoso
        
        ¿Por qué mockear pagos?
        - NO queremos hacer cargos reales en tests
        - NO queremos exponer tarjetas de prueba
        - Tests seguros y sin costo
        """
        # ARRANGE
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "ch_test123",
            "status": "succeeded",
            "amount": 5000,
            "currency": "eur"
        }
        mock_post.return_value = mock_response
        
        # ACT
        gateway = PaymentGateway()
        result = gateway.process_payment(50.00, "tok_visa")
        
        # ASSERT
        assert result["status"] == "succeeded"
        assert result["amount"] == 5000
        assert result["id"] == "ch_test123"
    
    @patch('requests.post')
    def test_process_payment_declined(self, mock_post):
        """Mock de pago rechazado"""
        # ARRANGE: Simular rechazo de tarjeta
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": {
                "type": "card_error",
                "code": "card_declined",
                "message": "Your card was declined"
            }
        }
        mock_post.return_value = mock_response
        
        # ACT
        gateway = PaymentGateway()
        result = gateway.process_payment(100.00, "tok_declined")
        
        # ASSERT
        assert "error" in result
        assert result["error"]["code"] == "card_declined"
    
    @patch('requests.post')
    def test_refund_payment(self, mock_post):
        """Mock de reembolso de pago"""
        # ARRANGE
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "re_test456",
            "status": "succeeded",
            "amount": 5000
        }
        mock_post.return_value = mock_response
        
        # ACT
        gateway = PaymentGateway()
        result = gateway.refund_payment("ch_test123")
        
        # ASSERT
        assert result["status"] == "succeeded"
        assert result["id"] == "re_test456"


# ============================================================================
# MOCK DE API DE EMAIL - SendGrid/Mailgun Simulado
# ============================================================================

class EmailService:
    """Servicio de email simulado"""
    
    def send_email(self, to: str, subject: str, body: str):
        """Envía un email (simulación)"""
        import requests
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            json={"to": to, "subject": subject, "body": body}
        )
        return response.json()


class TestEmailServiceMocking:
    """Tests con mocking de servicio de email"""
    
    @patch('requests.post')
    def test_send_email_success(self, mock_post):
        """
        Mock de envío de email
        
        Beneficio: NO enviamos emails reales en tests
        """
        # ARRANGE
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message_id": "msg_test789",
            "status": "sent"
        }
        mock_post.return_value = mock_response
        
        # ACT
        service = EmailService()
        result = service.send_email(
            "user@example.com",
            "Test Subject",
            "Test Body"
        )
        
        # ASSERT
        assert result["status"] == "sent"
        assert "message_id" in result
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_send_email_invalid_recipient(self, mock_post):
        """Mock de email con destinatario inválido"""
        # ARRANGE
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": "Invalid email address"
        }
        mock_post.return_value = mock_response
        
        # ACT
        service = EmailService()
        result = service.send_email("invalid-email", "Subject", "Body")
        
        # ASSERT
        assert "error" in result
