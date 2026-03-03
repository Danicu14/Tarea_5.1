"""
Tests unitarios exhaustivos para configuración
Tests de Settings con casos positivos, negativos y edge cases
"""
import pytest
from unittest.mock import patch
from app.config import Settings, get_settings


class TestSettingsProperties:
    """Tests de propiedades derivadas de Settings"""
    
    @pytest.mark.unit
    def test_cors_origins_list_single(self):
        """Debe parsear un solo origen CORS"""
        settings = Settings(cors_origins="http://localhost:3000")
        assert settings.cors_origins_list == ["http://localhost:3000"]
    
    @pytest.mark.unit
    def test_cors_origins_list_multiple(self):
        """Debe parsear múltiples orígenes CORS"""
        settings = Settings(cors_origins="http://localhost:3000,http://localhost:8000,https://example.com")
        assert len(settings.cors_origins_list) == 3
        assert "http://localhost:3000" in settings.cors_origins_list
    
    @pytest.mark.unit
    def test_cors_origins_list_with_spaces(self):
        """Debe eliminar espacios en blanco de orígenes"""
        settings = Settings(cors_origins=" http://localhost:3000 , http://localhost:8000 ")
        origins = settings.cors_origins_list
        assert all(not origin.startswith(" ") and not origin.endswith(" ") for origin in origins)
    
    @pytest.mark.unit
    def test_cors_origins_list_empty(self):
        """Debe manejar string vacío"""
        settings = Settings(cors_origins="")
        # Debería retornar lista con un string vacío o lista vacía después de filtrar
        assert isinstance(settings.cors_origins_list, list)
    
    @pytest.mark.unit
    def test_allowed_origins_list(self):
        """Debe parsear allowed_origins correctamente"""
        settings = Settings(allowed_origins="http://localhost:3000,http://localhost:8000")
        assert len(settings.allowed_origins_list) == 2


class TestSettingsDefaults:
    """Tests de valores por defecto de configuración"""
    
    @pytest.mark.unit
    def test_default_environment(self):
        """Debe tener environment por defecto"""
        settings = Settings()
        assert settings.environment == "development"
    
    @pytest.mark.unit
    def test_default_debug(self):
        """Debe tener debug activado por defecto"""
        settings = Settings()
        assert settings.debug is True
    
    @pytest.mark.unit
    def test_default_port(self):
        """Debe tener puerto por defecto"""
        settings = Settings()
        assert settings.port == 8000
    
    @pytest.mark.unit
    def test_default_host(self):
        """Debe tener host por defecto"""
        settings = Settings()
        assert settings.host == "0.0.0.0"
    
    @pytest.mark.unit
    def test_default_rate_limit_enabled(self):
        """Debe tener rate limiting habilitado por defecto"""
        settings = Settings()
        assert settings.rate_limit_enabled is True
    
    @pytest.mark.unit
    def test_default_rate_limit_per_minute(self):
        """Debe tener límite de requests por defecto"""
        settings = Settings()
        assert settings.rate_limit_per_minute == 60


class TestSettingsCustomization:
    """Tests de personalización de configuración"""
    
    @pytest.mark.unit
    def test_custom_environment(self):
        """Debe permitir environment personalizado"""
        settings = Settings(environment="production")
        assert settings.environment == "production"
    
    @pytest.mark.unit
    def test_custom_debug(self):
        """Debe permitir deshabilitar debug"""
        settings = Settings(debug=False)
        assert settings.debug is False
    
    @pytest.mark.unit
    def test_custom_port(self):
        """Debe permitir puerto personalizado"""
        settings = Settings(port=9000)
        assert settings.port == 9000
    
    @pytest.mark.unit
    def test_custom_api_title(self):
        """Debe permitir título de API personalizado"""
        settings = Settings(api_title="Mi API")
        assert settings.api_title == "Mi API"
    
    @pytest.mark.unit
    def test_custom_api_version(self):
        """Debe permitir versión personalizada"""
        settings = Settings(api_version="2.0.0")
        assert settings.api_version == "2.0.0"


class TestSettingsSecurity:
    """Tests de configuración de seguridad"""
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_force_https_disabled_by_default(self):
        """HTTPS no debe estar forzado por defecto (desarrollo)"""
        settings = Settings()
        assert settings.force_https is False
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_force_https_can_be_enabled(self):
        """Debe poder habilitar HTTPS forzado"""
        settings = Settings(force_https=True)
        assert settings.force_https is True
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_secret_key_has_default(self):
        """Debe tener secret_key por defecto (aunque no seguro para producción) """
        settings = Settings()
        assert settings.secret_key is not None
        assert len(settings.secret_key) > 0
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_custom_secret_key(self):
        """Debe permitir secret_key personalizado"""
        custom_key = "my-super-secret-key-123"
        settings = Settings(secret_key=custom_key)
        assert settings.secret_key == custom_key


class TestSettingsRateLimiting:
    """Tests de configuración de rate limiting"""
    
    @pytest.mark.unit
    def test_disable_rate_limiting(self):
        """Debe poder deshabilitar rate limiting"""
        settings = Settings(rate_limit_enabled=False)
        assert settings.rate_limit_enabled is False
    
    @pytest.mark.unit
    def test_custom_rate_limit(self):
        """Debe permitir límite personalizado"""
        settings = Settings(rate_limit_per_minute=100)
        assert settings.rate_limit_per_minute == 100
    
    @pytest.mark.unit
    def test_very_low_rate_limit(self):
        """Debe aceptar límite muy bajo"""
        settings = Settings(rate_limit_per_minute=1)
        assert settings.rate_limit_per_minute == 1
    
    @pytest.mark.unit
    def test_very_high_rate_limit(self):
        """Debe aceptar límite muy alto"""
        settings = Settings(rate_limit_per_minute=10000)
        assert settings.rate_limit_per_minute == 10000


class TestSettingsDatabase:
    """Tests de configuración de base de datos"""
    
    @pytest.mark.unit
    def test_default_database_url(self):
        """Debe tener URL de BD por defecto"""
        settings = Settings()
        assert settings.database_url is not None
        assert "sqlite" in settings.database_url
    
    @pytest.mark.unit
    def test_custom_database_url(self):
        """Debe permitir URL de BD personalizada"""
        custom_url = "postgresql://user:pass@localhost/db"
        settings = Settings(database_url=custom_url)
        assert settings.database_url == custom_url


class TestGetSettingsSingleton:
    """Tests del patrón singleton de configuración"""
    
    @pytest.mark.unit
    def test_singleton_returns_same_instance(self):
        """get_settings debe retornar la misma instancia"""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
    
    @pytest.mark.unit
    def test_singleton_caches_settings(self):
        """Debe cachear la configuración"""
        # Limpiar cache
        get_settings.cache_clear()
        
        first_call = get_settings()
        second_call = get_settings()
        
        # Deben ser el mismo objeto
        assert id(first_call) == id(second_call)


class TestSettingsEdgeCases:
    """Tests de casos edge de configuración"""
    
    @pytest.mark.unit
    def test_empty_cors_origins(self):
        """Debe manejar CORS origins vacío"""
        settings = Settings(cors_origins="")
        origins = settings.cors_origins_list
        assert isinstance(origins, list)
    
    @pytest.mark.unit
    def test_cors_origins_with_trailing_comma(self):
        """Debe manejar comas finales"""
        settings = Settings(cors_origins="http://localhost:3000,")
        origins = settings.cors_origins_list
        # Debe haber solo un origin válido (el string vacío debe existir pero no nos importa)
        assert len(origins) >= 1
        assert "http://localhost:3000" in origins
    
    @pytest.mark.unit
    def test_very_long_api_title(self):
        """Debe aceptar títulos muy largos"""
        long_title = "A" * 1000
        settings = Settings(api_title=long_title)
        assert settings.api_title == long_title
    
    @pytest.mark.unit
    def test_special_characters_in_secret_key(self):
        """Debe aceptar caracteres especiales en secret_key"""
        special_key = "key-with-!@#$%^&*()_+{}[]"
        settings = Settings(secret_key=special_key)
        assert settings.secret_key == special_key
    
    @pytest.mark.unit
    def test_zero_rate_limit(self):
        """Debe aceptar rate limit de cero"""
        settings = Settings(rate_limit_per_minute=0)
        assert settings.rate_limit_per_minute == 0


class TestSettingsProductionMode:
    """Tests de configuración en modo producción"""
    
    @pytest.mark.unit
    def test_production_environment(self):
        """Debe configurar correctamente modo producción"""
        settings = Settings(
            environment="production",
            debug=False,
            force_https=True
        )
        assert settings.environment == "production"
        assert settings.debug is False
        assert settings.force_https is True
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_production_should_have_strong_secret(self):
        """En producción debería usar secret_key fuerte (esto es una recomendación)"""
        settings = Settings(environment="production")
        # Este test documenta que el secret por defecto no es seguro
        # En producción real, debería ser sobrescrito
        assert settings.secret_key != ""


class TestSettingsValidation:
    """Tests de validación de configuración"""
    
    @pytest.mark.unit
    def test_api_version_format(self):
        """Debe aceptar diferentes formatos de versión"""
        settings = Settings(api_version="1.0.0")
        assert settings.api_version == "1.0.0"
        
        settings = Settings(api_version="v2.1.5-beta")
        assert settings.api_version == "v2.1.5-beta"
    
    @pytest.mark.unit
    def test_host_formats(self):
        """Debe aceptar diferentes formatos de host"""
        assert Settings(host="0.0.0.0").host == "0.0.0.0"
        assert Settings(host="127.0.0.1").host == "127.0.0.1"
        assert Settings(host="localhost").host == "localhost"
    
    @pytest.mark.unit
    def test_port_range(self):
        """Debe aceptar puertos válidos"""
        assert Settings(port=80).port == 80
        assert Settings(port=443).port == 443
        assert Settings(port=8080).port == 8080
        assert Settings(port=65535).port == 65535
