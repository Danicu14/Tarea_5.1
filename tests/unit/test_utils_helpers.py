"""
Tests unitarios exhaustivos para módulo de utilidades
Tests de funciones helper con casos positivos, negativos y edge cases
"""
import pytest
from datetime import datetime, timedelta
from app.utils import (
    parse_comma_separated_list,
    validate_email,
    sanitize_string,
    is_valid_url,
    calculate_time_remaining,
    format_file_size,
    merge_dicts,
    truncate_text,
    validate_positive_number,
    chunk_list
)


class TestParseCommaSeparatedList:
    """Tests unitarios para parse_comma_separated_list"""
    
    @pytest.mark.unit
    def test_parse_simple_list(self):
        """Debe parsear una lista simple correctamente"""
        result = parse_comma_separated_list("item1,item2,item3")
        assert result == ["item1", "item2", "item3"]
    
    @pytest.mark.unit
    def test_parse_list_with_spaces(self):
        """Debe eliminar espacios en blanco por defecto"""
        result = parse_comma_separated_list("item1 , item2 , item3")
        assert result == ["item1", "item2", "item3"]
    
    @pytest.mark.unit
    def test_parse_empty_string(self):
        """Debe retornar lista vacía para string vacío"""
        result = parse_comma_separated_list("")
        assert result == []
    
    @pytest.mark.unit
    def test_parse_single_item(self):
        """Debe manejar un solo item"""
        result = parse_comma_separated_list("solo_item")
        assert result == ["solo_item"]
    
    @pytest.mark.unit
    def test_parse_with_empty_items(self):
        """Debe filtrar items vacíos"""
        result = parse_comma_separated_list("item1,,item2, ,item3")
        assert result == ["item1", "item2", "item3"]
    
    @pytest.mark.unit
    def test_parse_without_strip(self):
        """Debe mantener espacios si strip_whitespace=False"""
        result = parse_comma_separated_list(" item1 , item2 ", strip_whitespace=False)
        assert " item1 " in result
        assert " item2 " in result


class TestValidateEmail:
    """Tests unitarios para validate_email"""
    
    @pytest.mark.unit
    def test_valid_email(self):
        """Debe validar emails correctos"""
        assert validate_email("user@example.com") is True
        assert validate_email("test.user@domain.co.uk") is True
        assert validate_email("name+tag@example.org") is True
    
    @pytest.mark.unit
    def test_invalid_email_no_at(self):
        """Debe rechazar emails sin @"""
        assert validate_email("userexample.com") is False
    
    @pytest.mark.unit
    def test_invalid_email_no_domain(self):
        """Debe rechazar emails sin dominio"""
        assert validate_email("user@") is False
    
    @pytest.mark.unit
    def test_invalid_email_no_tld(self):
        """Debe rechazar emails sin TLD"""
        assert validate_email("user@domain") is False
    
    @pytest.mark.unit
    def test_empty_email(self):
        """Debe rechazar email vacío"""
        assert validate_email("") is False
        assert validate_email(None) is False
    
    @pytest.mark.unit
    def test_special_characters(self):
        """Debe manejar caracteres especiales"""
        assert validate_email("user@domain.com") is True
        assert validate_email("user name@domain.com") is False


class TestSanitizeString:
    """Tests unitarios para sanitize_string"""
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_sanitize_html_tags(self):
        """Debe eliminar tags HTML"""
        result = sanitize_string("<script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_sanitize_quotes(self):
        """Debe eliminar comillas"""
        result = sanitize_string("test'with\"quotes")
        assert "'" not in result
        assert '"' not in result
    
    @pytest.mark.unit
    def test_sanitize_with_max_length(self):
        """Debe truncar a longitud máxima"""
        result = sanitize_string("texto muy largo", max_length=10)
        assert len(result) <= 10
    
    @pytest.mark.unit
    def test_sanitize_empty_string(self):
        """Debe manejar string vacío"""
        assert sanitize_string("") == ""
        assert sanitize_string(None) == ""
    
    @pytest.mark.unit
    def test_sanitize_normal_text(self):
        """Debe mantener texto normal"""
        result = sanitize_string("Texto normal sin caracteres especiales")
        assert "Texto normal sin caracteres especiales" == result


class TestIsValidUrl:
    """Tests unitarios para is_valid_url"""
    
    @pytest.mark.unit
    def test_valid_https_url(self):
        """Debe validar URLs HTTPS válidas"""
        assert is_valid_url("https://example.com") is True
        assert is_valid_url("https://www.example.com/path") is True
    
    @pytest.mark.unit
    def test_valid_http_url(self):
        """Debe validar URLs HTTP válidas"""
        assert is_valid_url("http://example.com") is True
    
    @pytest.mark.unit
    def test_invalid_url_no_protocol(self):
        """Debe rechazar URLs sin protocolo"""
        assert is_valid_url("www.example.com") is False
        assert is_valid_url("example.com") is False
    
    @pytest.mark.unit
    def test_invalid_url_format(self):
        """Debe rechazar formatos inválidos"""
        assert is_valid_url("not-a-url") is False
        assert is_valid_url("ftp://example.com") is False
    
    @pytest.mark.unit
    def test_empty_url(self):
        """Debe rechazar URL vacía"""
        assert is_valid_url("") is False
        assert is_valid_url(None) is False


class TestCalculateTimeRemaining:
    """Tests unitarios para calculate_time_remaining"""
    
    @pytest.mark.unit
    def test_future_time(self):
        """Debe calcular tiempo futuro correctamente"""
        future = datetime.now() + timedelta(hours=2)
        result = calculate_time_remaining(future)
        assert result.total_seconds() > 0
    
    @pytest.mark.unit
    def test_past_time(self):
        """Debe retornar tiempo negativo para fechas pasadas"""
        past = datetime.now() - timedelta(hours=1)
        result = calculate_time_remaining(past)
        assert result.total_seconds() < 0
    
    @pytest.mark.unit
    def test_current_time(self):
        """Debe retornar cerca de cero para tiempo actual"""
        now = datetime.now()
        result = calculate_time_remaining(now)
        # Pequeña tolerancia por tiempo de ejecución
        assert abs(result.total_seconds()) < 1


class TestFormatFileSize:
    """Tests unitarios para format_file_size"""
    
    @pytest.mark.unit
    def test_bytes(self):
        """Debe formatear bytes correctamente"""
        assert format_file_size(100) == "100.0 B"
    
    @pytest.mark.unit
    def test_kilobytes(self):
        """Debe formatear KB correctamente"""
        assert format_file_size(1024) == "1.0 KB"
    
    @pytest.mark.unit
    def test_megabytes(self):
        """Debe formatear MB correctamente"""
        assert format_file_size(1048576) == "1.0 MB"
    
    @pytest.mark.unit
    def test_gigabytes(self):
        """Debe formatear GB correctamente"""
        assert format_file_size(1073741824) == "1.0 GB"
    
    @pytest.mark.unit
    def test_negative_size(self):
        """Debe manejar tamaño negativo"""
        assert format_file_size(-100) == "0 B"
    
    @pytest.mark.unit
    def test_zero_size(self):
        """Debe manejar tamaño cero"""
        assert format_file_size(0) == "0.0 B"


class TestMergeDicts:
    """Tests unitarios para merge_dicts"""
    
    @pytest.mark.unit
    def test_merge_simple_dicts(self):
        """Debe combinar diccionarios simples"""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3}
        result = merge_dicts(dict1, dict2)
        assert result == {"a": 1, "b": 2, "c": 3}
    
    @pytest.mark.unit
    def test_merge_with_override(self):
        """Debe sobrescribir valores duplicados"""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        result = merge_dicts(dict1, dict2)
        assert result["b"] == 3
    
    @pytest.mark.unit
    def test_merge_empty_dicts(self):
        """Debe manejar diccionarios vacíos"""
        assert merge_dicts({}, {}) == {}
        assert merge_dicts({"a": 1}, {}) == {"a": 1}
    
    @pytest.mark.unit
    def test_original_unchanged(self):
        """No debe modificar diccionarios originales"""
        dict1 = {"a": 1}
        dict2 = {"b": 2}
        result = merge_dicts(dict1, dict2)
        assert dict1 == {"a": 1}  # Sin cambios


class TestTruncateText:
    """Tests unitarios para truncate_text"""
    
    @pytest.mark.unit
    def test_truncate_long_text(self):
        """Debe truncar texto largo"""
        text = "Este es un texto muy largo"
        result = truncate_text(text, 10)
        assert len(result) <= 10
        assert result.endswith("...")
    
    @pytest.mark.unit
    def test_no_truncate_short_text(self):
        """No debe truncar texto corto"""
        text = "Corto"
        result = truncate_text(text, 20)
        assert result == text
    
    @pytest.mark.unit
    def test_custom_suffix(self):
        """Debe usar sufijo personalizado"""
        result = truncate_text("Texto largo", 8, suffix=">>")
        assert result.endswith(">>")
    
    @pytest.mark.unit
    def test_empty_text(self):
        """Debe manejar texto vacío"""
        assert truncate_text("", 10) == ""
        assert truncate_text(None, 10) is None


class TestValidatePositiveNumber:
    """Tests unitarios para validate_positive_number"""
    
    @pytest.mark.unit
    def test_positive_integer(self):
        """Debe validar enteros positivos"""
        assert validate_positive_number(5) is True
        assert validate_positive_number(100) is True
    
    @pytest.mark.unit
    def test_positive_float(self):
        """Debe validar floats positivos"""
        assert validate_positive_number(3.14) is True
        assert validate_positive_number(0.001) is True
    
    @pytest.mark.unit
    def test_negative_number(self):
        """Debe rechazar números negativos"""
        assert validate_positive_number(-5) is False
        assert validate_positive_number(-0.1) is False
    
    @pytest.mark.unit
    def test_zero(self):
        """Debe rechazar cero"""
        assert validate_positive_number(0) is False
    
    @pytest.mark.unit
    def test_string_number(self):
        """Debe validar strings numéricos"""
        assert validate_positive_number("10") is True
        assert validate_positive_number("-5") is False
    
    @pytest.mark.unit
    def test_invalid_input(self):
        """Debe rechazar entrada inválida"""
        assert validate_positive_number("abc") is False
        assert validate_positive_number(None) is False
        assert validate_positive_number([]) is False


class TestChunkList:
    """Tests unitarios para chunk_list"""
    
    @pytest.mark.unit
    def test_chunk_evenly_divisible(self):
        """Debe dividir lista divisible uniformemente"""
        items = [1, 2, 3, 4, 5, 6]
        result = chunk_list(items, 2)
        assert result == [[1, 2], [3, 4], [5, 6]]
    
    @pytest.mark.unit
    def test_chunk_with_remainder(self):
        """Debe manejar listas con resto"""
        items = [1, 2, 3, 4, 5]
        result = chunk_list(items, 2)
        assert result == [[1, 2], [3, 4], [5]]
    
    @pytest.mark.unit
    def test_chunk_size_larger_than_list(self):
        """Debe manejar chunk_size mayor que la lista"""
        items = [1, 2, 3]
        result = chunk_list(items, 10)
        assert result == [[1, 2, 3]]
    
    @pytest.mark.unit
    def test_empty_list(self):
        """Debe manejar lista vacía"""
        assert chunk_list([], 5) == []
    
    @pytest.mark.unit
    def test_invalid_chunk_size(self):
        """Debe lanzar error para chunk_size inválido"""
        with pytest.raises(ValueError, match="chunk_size debe ser mayor que 0"):
            chunk_list([1, 2, 3], 0)
        
        with pytest.raises(ValueError):
            chunk_list([1, 2, 3], -1)
