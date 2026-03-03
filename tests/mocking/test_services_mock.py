"""
Tests de Mocking - Servicios Externos y Sistema
===============================================

Simula servicios del sistema (filesystem, tiempo, variables de entorno)
para hacer tests determinísticos y reproducibles.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta
import os
from pathlib import Path


# ============================================================================
# MOCK DE SISTEMA DE ARCHIVOS (File System)
# ============================================================================

class FileManager:
    """Gestor de archivos"""
    
    def read_config(self, filepath: str) -> dict:
        """Lee archivo de configuración"""
        with open(filepath, 'r') as f:
            import json
            return json.load(f)
    
    def write_log(self, filepath: str, message: str):
        """Escribe en archivo de log"""
        with open(filepath, 'a') as f:
            f.write(f"{datetime.now()}: {message}\n")
    
    def file_exists(self, filepath: str) -> bool:
        """Verifica si archivo existe"""
        return os.path.exists(filepath)
    
    def get_file_size(self, filepath: str) -> int:
        """Obtiene tamaño de archivo"""
        return os.path.getsize(filepath)


class TestFileSystemMocking:
    """
    Tests con mocking de sistema de archivos
    
    VENTAJAS:
    1. NO creamos archivos reales en disco
    2. Tests rápidos (sin I/O a disco)
    3. No ensuciamos el filesystem
    4. Podemos simular errores (permisos, disco lleno)
    """
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"api_key": "test123", "timeout": 30}')
    def test_read_config_success(self, mock_file):
        """
        Mock de lectura de archivo
        
        Beneficio: NO necesitamos archivo config.json real
        """
        # ACT
        manager = FileManager()
        config = manager.read_config("config.json")
        
        # ASSERT
        assert config["api_key"] == "test123"
        assert config["timeout"] == 30
        mock_file.assert_called_once_with("config.json", 'r')
    
    @patch('builtins.open', new_callable=mock_open)
    def test_write_log_success(self, mock_file):
        """Mock de escritura de log"""
        # ARRANGE: Mock simple de archivo
        
        # ACT
        manager = FileManager()
        manager.write_log("app.log", "Usuario login exitoso")
        
        # ASSERT
        mock_file.assert_called_once_with("app.log", 'a')
        # Verificar que se escribió el contenido
        handle = mock_file()
        handle.write.assert_called_once()
    
    @patch('os.path.exists')
    def test_file_exists_true(self, mock_exists):
        """Mock de verificación de existencia de archivo"""
        # ARRANGE: Simular que archivo existe
        mock_exists.return_value = True
        
        # ACT
        manager = FileManager()
        exists = manager.file_exists("data.json")
        
        # ASSERT
        assert exists is True
        mock_exists.assert_called_once_with("data.json")
    
    @patch('os.path.exists')
    def test_file_exists_false(self, mock_exists):
        """Mock de archivo no existente"""
        # ARRANGE
        mock_exists.return_value = False
        
        # ACT
        manager = FileManager()
        exists = manager.file_exists("missing.txt")
        
        # ASSERT
        assert exists is False
    
    @patch('os.path.getsize')
    def test_get_file_size(self, mock_getsize):
        """Mock de tamaño de archivo"""
        # ARRANGE: Simular archivo de 1024 bytes
        mock_getsize.return_value = 1024
        
        # ACT
        manager = FileManager()
        size = manager.get_file_size("document.pdf")
        
        # ASSERT
        assert size == 1024
        mock_getsize.assert_called_once_with("document.pdf")


# ============================================================================
# MOCK DE FECHA Y HORA (Datetime)
# ============================================================================

class ReportGenerator:
    """Generador de reportes con timestamp"""
    
    def generate_daily_report(self) -> dict:
        """Genera reporte diario"""
        now = datetime.now()
        return {
            "report_date": now.strftime("%Y-%m-%d"),
            "report_time": now.strftime("%H:%M:%S"),
            "type": "daily"
        }
    
    def is_business_hours(self) -> bool:
        """Verifica si es horario laboral (9-18)"""
        now = datetime.now()
        return 9 <= now.hour < 18
    
    def calculate_expiry_date(self, days: int) -> str:
        """Calcula fecha de expiración"""
        expiry = datetime.now() + timedelta(days=days)
        return expiry.strftime("%Y-%m-%d")


class TestDatetimeMocking:
    """
    Tests con mocking de fecha/hora
    
    VENTAJAS:
    1. Tests determinísticos (misma fecha siempre)
    2. Podemos probar cualquier fecha/hora sin esperar
    3. Podemos probar condiciones temporales específicas
    """
    
    def test_datetime_mock_concept(self):
        """
        Ejemplo conceptual de mock de datetime
        
        En producción, usaríamos @patch('module.datetime')
        Aquí demostramos el concepto sin dependencias externas
        """
        # ARRANGE: Crear mock de datetime
        mock_datetime = MagicMock()
        fixed_date = datetime(2024, 3, 15, 14, 30, 0)
        mock_datetime.now.return_value = fixed_date
        
        # ACT: Usar el mock
        result = mock_datetime.now()
        
        # ASSERT: Verificar fecha fija
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 15
        assert result.hour == 14
    
    def test_business_hours_check_concept(self):
        """Concepto de verificación de horario laboral con mock"""
        # ARRANGE: Mock de hora laboral
        mock_datetime = MagicMock()
        work_time = datetime(2024, 3, 15, 10, 0, 0)
        mock_datetime.now.return_value = work_time
        
        # ACT
        current_hour = mock_datetime.now().hour
        is_business_hours = 9 <= current_hour < 18
        
        # ASSERT
        assert is_business_hours is True
    
    def test_after_hours_check_concept(self):
        """Concepto de verificación fuera de horario con mock"""
        # ARRANGE: Mock de hora fuera de trabajo
        mock_datetime = MagicMock()
        after_work = datetime(2024, 3, 15, 20, 0, 0)
        mock_datetime.now.return_value = after_work
        
        # ACT
        current_hour = mock_datetime.now().hour
        is_business_hours = 9 <= current_hour < 18
        
        # ASSERT
        assert is_business_hours is False
    
    def test_date_calculation_concept(self):
        """Concepto de cálculo de fechas con mock"""
        # ARRANGE
        base_date = datetime(2024, 3, 1, 12, 0, 0)
        days_to_add = 30
        
        # ACT
        expiry_date = base_date + timedelta(days=days_to_add)
        
        # ASSERT
        assert expiry_date.day == 31
        assert expiry_date.month == 3
        assert expiry_date.year == 2024


# ============================================================================
# MOCK DE VARIABLES DE ENTORNO
# ============================================================================

class ConfigLoader:
    """Cargador de configuración desde variables de entorno"""
    
    def get_database_url(self) -> str:
        """Obtiene URL de BD desde variable de entorno"""
        return os.getenv("DATABASE_URL", "sqlite:///default.db")
    
    def get_api_key(self) -> str:
        """Obtiene API key desde variable de entorno"""
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("API_KEY not set")
        return api_key
    
    def is_debug_mode(self) -> bool:
        """Verifica si está en modo debug"""
        return os.getenv("DEBUG", "false").lower() == "true"
    
    def get_max_connections(self) -> int:
        """Obtiene número máximo de conexiones"""
        return int(os.getenv("MAX_CONNECTIONS", "10"))


class TestEnvironmentMocking:
    """
    Tests con mocking de variables de entorno
    
    VENTAJAS:
    1. NO modificamos variables de entorno reales
    2. Tests aislados
    3. Podemos probar diferentes configuraciones
    """
    
    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/testdb"})
    def test_get_database_url_from_env(self):
        """
        Mock de variable de entorno: DATABASE_URL
        
        Beneficio: NO usamos configuración real del sistema
        """
        # ACT
        loader = ConfigLoader()
        db_url = loader.get_database_url()
        
        # ASSERT
        assert db_url == "postgresql://test:test@localhost/testdb"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_database_url_default(self):
        """Mock de variable de entorno no definida (usa default)"""
        # ACT
        loader = ConfigLoader()
        db_url = loader.get_database_url()
        
        # ASSERT
        assert db_url == "sqlite:///default.db"
    
    @patch.dict(os.environ, {"API_KEY": "sk_test_12345"})
    def test_get_api_key_success(self):
        """Mock de API key presente"""
        # ACT
        loader = ConfigLoader()
        api_key = loader.get_api_key()
        
        # ASSERT
        assert api_key == "sk_test_12345"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_missing(self):
        """Mock de API key ausente (debe lanzar error)"""
        # ACT & ASSERT
        loader = ConfigLoader()
        with pytest.raises(ValueError, match="API_KEY not set"):
            loader.get_api_key()
    
    @patch.dict(os.environ, {"DEBUG": "true"})
    def test_is_debug_mode_enabled(self):
        """Mock de modo debug activado"""
        # ACT
        loader = ConfigLoader()
        debug = loader.is_debug_mode()
        
        # ASSERT
        assert debug is True
    
    @patch.dict(os.environ, {"DEBUG": "false"})
    def test_is_debug_mode_disabled(self):
        """Mock de modo debug desactivado"""
        # ACT
        loader = ConfigLoader()
        debug = loader.is_debug_mode()
        
        # ASSERT
        assert debug is False
    
    @patch.dict(os.environ, {"MAX_CONNECTIONS": "50"})
    def test_get_max_connections_custom(self):
        """Mock de variable de entorno numérica"""
        # ACT
        loader = ConfigLoader()
        max_conn = loader.get_max_connections()
        
        # ASSERT
        assert max_conn == 50
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_max_connections_default(self):
        """Mock de variable de entorno con valor por defecto"""
        # ACT
        loader = ConfigLoader()
        max_conn = loader.get_max_connections()
        
        # ASSERT
        assert max_conn == 10


# ============================================================================
# MOCK DE DEPENDENCIAS MÚLTIPLES (Escenario Complejo)
# ============================================================================

class OrderProcessor:
    """Procesador de órdenes que usa múltiples dependencias externas"""
    
    def process_order(self, order_id: int, user_email: str):
        """
        Procesa una orden:
        1. Consulta BD para obtener orden
        2. Procesa pago con gateway externo
        3. Envía email de confirmación
        4. Guarda timestamp en log
        """
        # Simularíamos llamadas a BD, API de pagos, email, etc.
        pass


class TestComplexMocking:
    """
    Tests con múltiples mocks simultáneos
    
    Demuestra cómo aislar un componente que depende de múltiples servicios externos
    """
    
    @patch('requests.post')  # Mock de API de email
    @patch('os.path.exists')  # Mock de filesystem
    def test_complex_scenario_multiple_mocks(self, mock_exists, mock_post):
        """
        Ejemplo de test con múltiples mocks
        
        Demuestra aislamiento completo de todas las dependencias externas
        """
        # ARRANGE: Configurar todos los mocks
        current_time = datetime(2024, 3, 15, 12, 0, 0)
        mock_exists.return_value = True
        mock_post.return_value = MagicMock(json=lambda: {"status": "sent"})
        
        # ACT: Aquí ejecutaríamos lógica que usa todas estas dependencias
        result_file = mock_exists("order.json")
        result_email = mock_post("https://api.example.com/send")
        
        # ASSERT: Verificar que los mocks funcionan correctamente
        assert result_file is True
        assert result_email.json()["status"] == "sent"
        
        # Este test demuestra que podemos aislar TODAS las dependencias
        # y probar lógica de negocio sin tocar ningún servicio real
