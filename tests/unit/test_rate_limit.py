"""
Tests unitarios exhaustivos para rate limiting
Tests con casos positivos, negativos, edge cases y concurrencia
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
import time
from app.main import check_rate_limit, rate_limit_storage


class TestRateLimitBasic:
    """Tests básicos de rate limiting"""
    
    @pytest.mark.unit
    def test_first_request_allowed(self):
        """El primer request debe ser permitido"""
        result = check_rate_limit("192.168.1.1")
        assert result is True
    
    @pytest.mark.unit
    def test_different_ips_independent(self):
        """Diferentes IPs deben tener límites independientes"""
        assert check_rate_limit("192.168.1.1") is True
        assert check_rate_limit("192.168.1.2") is True
        assert check_rate_limit("192.168.1.3") is True
    
    @pytest.mark.unit
    def test_same_ip_accumulates(self):
        """La misma IP debe acumular requests"""
        ip = "192.168.1.100"
        
        # Hacer varios requests
        for _ in range(5):
            check_rate_limit(ip)
        
        # Verificar que se hayan registrado
        assert len(rate_limit_storage[ip]) == 5


class TestRateLimitBlocking:
    """Tests de bloqueo por exceder límite"""
    
    @pytest.mark.unit
    def test_blocks_after_limit_reached(self, monkeypatch):
        """Debe bloquear después de alcanzar el límite"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_per_minute', 3)
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        ip = "192.168.1.200"
        
        # Hacer requests hasta el límite
        for i in range(3):
            result = check_rate_limit(ip)
            assert result is True, f"Request {i+1} debería ser aceptado"
        
        # El siguiente debe ser bloqueado
        result = check_rate_limit(ip)
        assert result is False
    
    @pytest.mark.unit
    def test_blocks_only_offending_ip(self, monkeypatch):
        """Solo debe bloquear la IP que excede el límite"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_per_minute', 2)
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        ip1 = "192.168.1.100"
        ip2 = "192.168.1.101"
        
        # IP1 excede el límite
        check_rate_limit(ip1)
        check_rate_limit(ip1)
        assert check_rate_limit(ip1) is False
        
        # IP2 aún debe poder hacer requests
        assert check_rate_limit(ip2) is True


class TestRateLimitTimeWindow:
    """Tests de ventana de tiempo del rate limit"""
    
    @pytest.mark.unit
    def test_requests_within_window(self, monkeypatch):
        """Requests dentro de la ventana de tiempo deben contarse"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_per_minute', 3)
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        ip = "192.168.1.300"
        
        # Hacer requests dentro de la ventana
        assert check_rate_limit(ip) is True
        assert check_rate_limit(ip) is True
        assert check_rate_limit(ip) is True
        # Cuarto request debe fallar
        assert check_rate_limit(ip) is False
    
    @pytest.mark.unit
    def test_recent_requests_counted(self, monkeypatch):
        """Requests recientes deben contarse"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_per_minute', 2)
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        ip = "192.168.1.400"
        
        # Hacer 2 requests (límite)
        check_rate_limit(ip)
        check_rate_limit(ip)
        
        # El tercero debe ser bloqueado (aún dentro de la ventana)
        assert check_rate_limit(ip) is False


class TestRateLimitDisabled:
    """Tests con rate limiting deshabilitado"""
    
    @pytest.mark.unit
    def test_unlimited_when_disabled(self, monkeypatch):
        """Debe permitir requests ilimitados cuando está deshabilitado"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', False)
        
        ip = "192.168.1.500"
        
        # Hacer muchos requests
        for _ in range(1000):
            result = check_rate_limit(ip)
            assert result is True
    
    @pytest.mark.unit
    def test_disabled_ignores_limit_setting(self, monkeypatch):
        """Cuando está deshabilitado, ignora el límite configurado"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', False)
        monkeypatch.setattr(config.settings, 'rate_limit_per_minute', 1)  # Límite muy bajo
        
        ip = "192.168.1.600"
        
        # Aún así debe permitir muchos requests
        for _ in range(100):
            assert check_rate_limit(ip) is True


class TestRateLimitEdgeCases:
    """Tests de casos edge del rate limiting"""
    
    @pytest.mark.unit
    def test_empty_ip_address(self, monkeypatch):
        """Debe manejar IP vacía"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        result = check_rate_limit("")
        assert isinstance(result, bool)
    
    @pytest.mark.unit
    def test_special_ip_addresses(self, monkeypatch):
        """Debe manejar IPs especiales"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        assert check_rate_limit("127.0.0.1") is True  # Localhost
        assert check_rate_limit("0.0.0.0") is True    # Any
        assert check_rate_limit("::1") is True         # IPv6 localhost
    
    @pytest.mark.unit
    def test_very_long_ip_string(self, monkeypatch):
        """Debe manejar strings de IP muy largos"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        long_ip = "192.168.1.1" * 100
        result = check_rate_limit(long_ip)
        assert isinstance(result, bool)
    
    @pytest.mark.unit
    def test_unicode_in_ip(self, monkeypatch):
        """Debe manejar unicode en IP"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        unicode_ip = "192.168.1.1用户"
        result = check_rate_limit(unicode_ip)
        assert isinstance(result, bool)


class TestRateLimitStorage:
    """Tests del almacenamiento de rate limiting"""
    
    @pytest.mark.unit
    def test_storage_cleanup(self, monkeypatch):
        """Debe limpiar requests antiguos del storage"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        ip = "192.168.1.700"
        
        # Agregar requests antiguos manualmente
        old_time = datetime.now() - timedelta(minutes=5)
        rate_limit_storage[ip] = [old_time, old_time, old_time]
        
        # Hacer un nuevo request
        check_rate_limit(ip)
        
        # El storage debería haber limpiado los antiguos
        # Solo debería quedar el request reciente
        assert len(rate_limit_storage[ip]) == 1
    
    @pytest.mark.unit
    def test_storage_mixed_old_new(self, monkeypatch):
        """Debe mantener requests recientes y limpiar antiguos"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        ip = "192.168.1.800"
        
        # Agregar mix de requests antiguos y recientes
        old_time = datetime.now() - timedelta(minutes=5)
        recent_time = datetime.now() - timedelta(seconds=30)
        rate_limit_storage[ip] = [old_time, old_time, recent_time]
        
        # Hacer un nuevo request
        check_rate_limit(ip)
        
        # Debería tener el reciente anterior + el nuevo
        assert len(rate_limit_storage[ip]) == 2


class TestRateLimitCustomLimits:
    """Tests con límites personalizados"""
    
    @pytest.mark.unit
    def test_very_low_limit(self, monkeypatch):
        """Debe funcionar con límite muy bajo (1 request)"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_per_minute', 1)
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        ip = "192.168.1.900"
        
        # Primer request OK
        assert check_rate_limit(ip) is True
        
        # Segundo request bloqueado
        assert check_rate_limit(ip) is False
    
    @pytest.mark.unit
    def test_very_high_limit(self, monkeypatch):
        """Debe funcionar con límite muy alto"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_per_minute', 10000)
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        ip = "192.168.1.1000"
        
        # Muchos requests deben pasar
        for _ in range(100):
            assert check_rate_limit(ip) is True
    
    @pytest.mark.unit
    def test_boundary_conditions(self, monkeypatch):
        """Debe manejar correctamente las condiciones de frontera"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_per_minute', 5)
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        ip = "192.168.1.1100"
        
        # Exactamente hasta el límite debe pasar
        for i in range(5):
            result = check_rate_limit(ip)
            assert result is True, f"Request {i+1}/5 debería pasar"
        
        # El request 6 debe ser bloqueado
        assert check_rate_limit(ip) is False


class TestRateLimitConcurrency:
    """Tests de comportamiento bajo concurrencia (simulado)"""
    
    @pytest.mark.unit
    def test_multiple_ips_simultaneously(self, monkeypatch):
        """Debe manejar múltiples IPs correctamente"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_per_minute', 5)
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        # Simular requests de múltiples IPs
        for i in range(10):
            ip = f"192.168.1.{i}"
            for _ in range(3):
                assert check_rate_limit(ip) is True
        
        # Cada IP debe tener su propio contador
        assert len(rate_limit_storage) >= 10
    
    @pytest.mark.unit
    def test_rapid_succession_same_ip(self, monkeypatch):
        """Debe contar requests rápidos de la misma IP"""
        from app import config
        monkeypatch.setattr(config.settings, 'rate_limit_per_minute', 10)
        monkeypatch.setattr(config.settings, 'rate_limit_enabled', True)
        
        ip = "192.168.1.1200"
        
        # Hacer requests rápidamente
        results = [check_rate_limit(ip) for _ in range(15)]
        
        # Los primeros 10 deben pasar, los restantes bloquearse
        assert sum(results) == 10
        assert results[:10] == [True] * 10
        assert results[10:] == [False] * 5
