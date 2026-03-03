"""
Tests unitarios exhaustivos para validadores
Tests con casos positivos, negativos y edge cases
"""
import pytest
from datetime import datetime
from app.validators import (
    ValidationError,
    validate_item_name,
    validate_item_price,
    validate_item_quantity,
    validate_item_data,
    validate_date_range,
    validate_pagination,
    validate_search_query
)


class TestValidateItemName:
    """Tests para validación de nombres de items"""
    
    @pytest.mark.unit
    def test_valid_name(self):
        """Debe aceptar nombres válidos"""
        assert validate_item_name("Item valido") is True
        assert validate_item_name("Product 123") is True
        assert validate_item_name("My-Item_Name") is True
    
    @pytest.mark.unit
    def test_reject_empty_name(self):
        """Debe rechazar nombres vacíos"""
        with pytest.raises(ValidationError, match="nombre es requerido"):
            validate_item_name("")
        
        with pytest.raises(ValidationError):
            validate_item_name(None)
    
    @pytest.mark.unit
    def test_reject_too_short(self):
        """Debe rechazar nombres muy cortos"""
        with pytest.raises(ValidationError, match="al menos 3 caracteres"):
            validate_item_name("ab")
    
    @pytest.mark.unit
    def test_reject_too_long(self):
        """Debe rechazar nombres muy largos"""
        long_name = "a" * 101
        with pytest.raises(ValidationError, match="no puede exceder 100"):
            validate_item_name(long_name)
    
    @pytest.mark.unit
    def test_reject_special_characters(self):
        """Debe rechazar caracteres especiales no permitidos"""
        with pytest.raises(ValidationError, match="letras, números"):
            validate_item_name("Item@Invalid!")
        
        with pytest.raises(ValidationError):
            validate_item_name("Item<script>")
    
    @pytest.mark.unit
    def test_boundary_lengths(self):
        """Debe manejar correctamente longitudes límite"""
        assert validate_item_name("abc") is True  # Mínimo válido (3)
        assert validate_item_name("a" * 100) is True  # Máximo válido (100)


class TestValidateItemPrice:
    """Tests para validación de precios"""
    
    @pytest.mark.unit
    def test_valid_price_float(self):
        """Debe aceptar precios flotantes válidos"""
        assert validate_item_price(10.5) == 10.5
        assert validate_item_price(99.99) == 99.99
    
    @pytest.mark.unit
    def test_valid_price_int(self):
        """Debe aceptar precios enteros"""
        assert validate_item_price(10) == 10.0
        assert validate_item_price(0) == 0.0
    
    @pytest.mark.unit
    def test_valid_price_string(self):
        """Debe aceptar precios como string"""
        assert validate_item_price("15.99") == 15.99
        assert validate_item_price("100") == 100.0
    
    @pytest.mark.unit
    def test_reject_negative_price(self):
        """Debe rechazar precios negativos"""
        with pytest.raises(ValidationError, match="no puede ser negativo"):
            validate_item_price(-10.5)
    
    @pytest.mark.unit
    def test_reject_too_high_price(self):
        """Debe rechazar precios muy altos"""
        with pytest.raises(ValidationError, match="excede el máximo"):
            validate_item_price(1000001)
    
    @pytest.mark.unit
    def test_reject_invalid_price(self):
        """Debe rechazar precios inválidos"""
        with pytest.raises(ValidationError, match="número válido"):
            validate_item_price("abc")
        
        with pytest.raises(ValidationError):
            validate_item_price(None)
    
    @pytest.mark.unit
    def test_rounds_to_two_decimals(self):
        """Debe redondear a 2 decimales"""
        assert validate_item_price(10.999) == 11.0
        assert validate_item_price(10.123) == 10.12


class TestValidateItemQuantity:
    """Tests para validación de cantidades"""
    
    @pytest.mark.unit
    def test_valid_quantity(self):
        """Debe aceptar cantidades válidas"""
        assert validate_item_quantity(5) == 5
        assert validate_item_quantity(100) == 100
        assert validate_item_quantity(0) == 0
    
    @pytest.mark.unit
    def test_convert_string_to_int(self):
        """Debe convertir strings a enteros"""
        assert validate_item_quantity("10") == 10
        assert validate_item_quantity("0") == 0
    
    @pytest.mark.unit
    def test_reject_negative_quantity(self):
        """Debe rechazar cantidades negativas"""
        with pytest.raises(ValidationError, match="no puede ser negativa"):
            validate_item_quantity(-5)
    
    @pytest.mark.unit
    def test_reject_too_high_quantity(self):
        """Debe rechazar cantidades muy altas"""
        with pytest.raises(ValidationError, match="excede el máximo"):
            validate_item_quantity(10001)
    
    @pytest.mark.unit
    def test_reject_invalid_quantity(self):
        """Debe rechazar cantidades inválidas"""
        with pytest.raises(ValidationError, match="número entero"):
            validate_item_quantity("abc")
        
        with pytest.raises(ValidationError):
            validate_item_quantity(None)
    
    @pytest.mark.unit
    def test_reject_float_quantity(self):
        """Debe rechazar/truncar floats"""
        # int() trunca, así que 10.5 se convierte en 10
        assert validate_item_quantity(10.5) == 10
        assert validate_item_quantity(10.9) == 10


class TestValidateItemData:
    """Tests para validación de datos completos de item"""
    
    @pytest.mark.unit
    def test_valid_complete_item(self):
        """Debe validar item completo válido"""
        item = {
            "name": "Test Item",
            "price": 19.99,
            "quantity": 10
        }
        result = validate_item_data(item)
        
        assert result["name"] == "Test Item"
        assert result["price"] == 19.99
        assert result["quantity"] == 10
    
    @pytest.mark.unit
    def test_valid_minimal_item(self):
        """Debe validar item solo con nombre"""
        item = {"name": "Minimal Item"}
        result = validate_item_data(item)
        
        assert result["name"] == "Minimal Item"
        assert "price" not in result
        assert "quantity" not in result
    
    @pytest.mark.unit
    def test_reject_missing_name(self):
        """Debe rechazar item sin nombre"""
        item = {"price": 10.0, "quantity": 5}
        
        with pytest.raises(ValidationError, match="nombre es requerido"):
            validate_item_data(item)
    
    @pytest.mark.unit
    def test_reject_invalid_type(self):
        """Debe rechazar tipo de datos inválido"""
        with pytest.raises(ValidationError, match="deben ser un diccionario"):
            validate_item_data("not a dict")
        
        with pytest.raises(ValidationError):
            validate_item_data(None)
    
    @pytest.mark.unit
    def test_trims_whitespace(self):
        """Debe eliminar espacios en blanco del nombre"""
        item = {"name": "  Spaced Item  "}
        result = validate_item_data(item)
        
        assert result["name"] == "Spaced Item"
    
    @pytest.mark.unit
    def test_validates_nested_fields(self):
        """Debe validar campos anidados (precio, cantidad)"""
        # Precio inválido
        with pytest.raises(ValidationError):
            validate_item_data({"name": "Item", "price": -10})
        
        # Cantidad inválida
        with pytest.raises(ValidationError):
            validate_item_data({"name": "Item", "quantity": -5})


class TestValidateDateRange:
    """Tests para validación de rangos de fechas"""
    
    @pytest.mark.unit
    def test_valid_date_range(self):
        """Debe aceptar rangos de fechas válidos"""
        assert validate_date_range("2026-01-01", "2026-12-31") is True
    
    @pytest.mark.unit
    def test_both_dates_optional(self):
        """Debe aceptar cuando ambas fechas son None"""
        assert validate_date_range(None, None) is True
    
    @pytest.mark.unit
    def test_reject_only_start_date(self):
        """Debe rechazar si solo se especifica fecha de inicio"""
        with pytest.raises(ValidationError, match="debe especificarse fecha de fin"):
            validate_date_range("2026-01-01", None)
    
    @pytest.mark.unit
    def test_reject_only_end_date(self):
        """Debe rechazar si solo se especifica fecha de fin"""
        with pytest.raises(ValidationError, match="debe especificarse fecha de inicio"):
            validate_date_range(None, "2026-12-31")
    
    @pytest.mark.unit
    def test_reject_invalid_format(self):
        """Debe rechazar formatos de fecha inválidos"""
        with pytest.raises(ValidationError, match="formato ISO"):
            validate_date_range("01/01/2026", "31/12/2026")
    
    @pytest.mark.unit
    def test_reject_reversed_dates(self):
        """Debe rechazar si inicio es después del fin"""
        with pytest.raises(ValidationError, match="debe ser anterior"):
            validate_date_range("2026-12-31", "2026-01-01")
    
    @pytest.mark.unit
    def test_reject_same_dates(self):
        """Debe rechazar si las fechas son iguales"""
        with pytest.raises(ValidationError, match="debe ser anterior"):
            validate_date_range("2026-06-01", "2026-06-01")
    
    @pytest.mark.unit
    def test_reject_too_old_start_date(self):
        """Debe rechazar fechas muy antiguas"""
        with pytest.raises(ValidationError, match="no puede ser anterior a 2020"):
            validate_date_range("2019-01-01", "2026-01-01")
    
    @pytest.mark.unit
    def test_reject_too_far_future(self):
        """Debe rechazar fechas muy futuras"""
        future_year = datetime.now().year + 15
        with pytest.raises(ValidationError, match="10 años en el futuro"):
            validate_date_range("2026-01-01", f"{future_year}-01-01")


class TestValidatePagination:
    """Tests para validación de paginación"""
    
    @pytest.mark.unit
    def test_valid_pagination(self):
        """Debe aceptar paginación válida"""
        assert validate_pagination(1, 10) == (1, 10)
        assert validate_pagination(5, 20) == (5, 20)
    
    @pytest.mark.unit
    def test_convert_strings(self):
        """Debe convertir strings a enteros"""
        assert validate_pagination("2", "15") == (2, 15)
    
    @pytest.mark.unit
    def test_reject_page_zero(self):
        """Debe rechazar página 0"""
        with pytest.raises(ValidationError, match="mayor o igual a 1"):
            validate_pagination(0, 10)
    
    @pytest.mark.unit
    def test_reject_negative_page(self):
        """Debe rechazar página negativa"""
        with pytest.raises(ValidationError, match="mayor o igual a 1"):
            validate_pagination(-1, 10)
    
    @pytest.mark.unit
    def test_reject_zero_page_size(self):
        """Debe rechazar tamaño de página 0"""
        with pytest.raises(ValidationError, match="mayor o igual a 1"):
            validate_pagination(1, 0)
    
    @pytest.mark.unit
    def test_reject_too_large_page_size(self):
        """Debe rechazar tamaño de página muy grande"""
        with pytest.raises(ValidationError, match="no puede exceder 100"):
            validate_pagination(1, 101)
    
    @pytest.mark.unit
    def test_reject_invalid_types(self):
        """Debe rechazar tipos inválidos"""
        with pytest.raises(ValidationError):
            validate_pagination("abc", 10)
        
        with pytest.raises(ValidationError):
            validate_pagination(1, "xyz")
    
    @pytest.mark.unit
    def test_boundary_values(self):
        """Debe aceptar valores límite válidos"""
        assert validate_pagination(1, 1) == (1, 1)  # Mínimos válidos
        assert validate_pagination(1000, 100) == (1000, 100)  # Máximos


class TestValidateSearchQuery:
    """Tests para validación de consultas de búsqueda"""
    
    @pytest.mark.unit
    def test_valid_query(self):
        """Debe aceptar queries válidas"""
        assert validate_search_query("test") == "test"
        assert validate_search_query("search term") == "search term"
    
    @pytest.mark.unit
    def test_trims_whitespace(self):
        """Debe eliminar espacios en blanco"""
        assert validate_search_query("  test  ") == "test"
    
    @pytest.mark.unit
    def test_reject_empty_query(self):
        """Debe rechazar query vacía"""
        with pytest.raises(ValidationError, match="es requerida"):
            validate_search_query("")
        
        with pytest.raises(ValidationError):
            validate_search_query(None)
    
    @pytest.mark.unit
    def test_reject_too_short(self):
        """Debe rechazar query muy corta"""
        with pytest.raises(ValidationError, match="al menos 2 caracteres"):
            validate_search_query("a")
    
    @pytest.mark.unit
    def test_custom_min_length(self):
        """Debe respetar longitud mínima personalizada"""
        with pytest.raises(ValidationError, match="al menos 5 caracteres"):
            validate_search_query("test", min_length=5)
    
    @pytest.mark.unit
    def test_reject_too_long(self):
        """Debe rechazar query muy larga"""
        long_query = "a" * 101
        with pytest.raises(ValidationError, match="no puede exceder 100"):
            validate_search_query(long_query)
    
    @pytest.mark.unit
    @pytest.mark.security
    def test_reject_dangerous_characters(self):
        """Debe rechazar caracteres peligrosos"""
        dangerous_queries = [
            "test<script>",
            "query>alert",
            'test"quoted',
            "sql';DROP",
            "path\\injection"
        ]
        
        for query in dangerous_queries:
            with pytest.raises(ValidationError, match="caracteres no permitidos"):
                validate_search_query(query)
    
    @pytest.mark.unit
    def test_allows_safe_characters(self):
        """Debe permitir caracteres seguros"""
        safe_queries = [
            "test query",
            "search-term",
            "query_with_underscore",
            "number123",
            "UPPERCASE"
        ]
        
        for query in safe_queries:
            result = validate_search_query(query)
            assert result is not None
