"""
Tests unitarios para utilidades y funciones individuales
Los tests unitarios verifican componentes aislados sin dependencias externas
"""
import pytest
from datetime import datetime, timedelta
from app.main import check_rate_limit


class TestRateLimiting:
    """Tests unitarios del sistema de rate limiting"""
    
    def test_rate_limit_allows_initial_request(self):
        """El primer request debe ser permitido"""
        result = check_rate_limit("192.168.1.1")
        assert result is True
    
    def test_rate_limit_blocks_after_limit(self, monkeypatch):
        """Debe bloquear después de exceder el límite"""
        # Configurar límite bajo para el test
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_per_minute', 3)
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        client_ip = "192.168.1.100"
        
        # Hacer requests hasta el límite
        for _ in range(3):
            assert check_rate_limit(client_ip) is True
        
        # El siguiente debe ser bloqueado
        assert check_rate_limit(client_ip) is False
    
    def test_rate_limit_disabled(self, monkeypatch):
        """Cuando está deshabilitado, permite todos los requests"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', False)
        
        # Muchos requests deben pasar
        for _ in range(100):
            assert check_rate_limit("192.168.1.1") is True


class TestConfiguration:
    """Tests unitarios de configuración"""
    
    def test_settings_loaded(self):
        """La configuración debe cargarse correctamente"""
        from app.config import settings
        
        assert settings.api_title is not None
        assert settings.api_version is not None
        assert settings.environment is not None
    
    def test_cors_origins_parsed(self):
        """Los orígenes CORS deben parsearse como lista"""
        from app.config import settings
        
        assert isinstance(settings.cors_origins_list, list)
