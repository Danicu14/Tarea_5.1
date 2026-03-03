"""
Validadores de datos de entrada
Lógica de negocio para validación de datos
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import re


class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass


def validate_item_name(name: str) -> bool:
    """
    Valida que un nombre de item sea válido
    
    Rules:
        - No vacío
        - Longitud entre 3 y 100 caracteres
        - Solo letras, números, espacios y guiones
    
    Args:
        name: Nombre a validar
    
    Returns:
        True si es válido
    
    Raises:
        ValidationError: Si el nombre no es válido
    
    Examples:
        >>> validate_item_name("Item válido")
        True
    """
    if not name or not isinstance(name, str):
        raise ValidationError("El nombre es requerido y debe ser un string")
    
    name = name.strip()
    
    if len(name) < 3:
        raise ValidationError("El nombre debe tener al menos 3 caracteres")
    
    if len(name) > 100:
        raise ValidationError("El nombre no puede exceder 100 caracteres")
    
    # Solo letras, números, espacios, guiones y underscores
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        raise ValidationError("El nombre solo puede contener letras, números, espacios y guiones")
    
    return True


def validate_item_price(price: Any) -> float:
    """
    Valida y normaliza un precio
    
    Args:
        price: Precio a validar (puede ser string, int, float)
    
    Returns:
        Precio como float normalizado a 2 decimales
    
    Raises:
        ValidationError: Si el precio no es válido
    
    Examples:
        >>> validate_item_price(10.5)
        10.5
        >>> validate_item_price("15.99")
        15.99
    """
    try:
        price_float = float(price)
    except (ValueError, TypeError):
        raise ValidationError("El precio debe ser un número válido")
    
    if price_float < 0:
        raise ValidationError("El precio no puede ser negativo")
    
    if price_float > 1000000:
        raise ValidationError("El precio excede el máximo permitido")
    
    # Redondear a 2 decimales
    return round(price_float, 2)


def validate_item_quantity(quantity: Any) -> int:
    """
    Valida una cantidad de items
    
    Args:
        quantity: Cantidad a validar
    
    Returns:
        Cantidad como entero
    
    Raises:
        ValidationError: Si la cantidad no es válida
    
    Examples:
        >>> validate_item_quantity(5)
        5
        >>> validate_item_quantity("10")
        10
    """
    try:
        quantity_int = int(quantity)
    except (ValueError, TypeError):
        raise ValidationError("La cantidad debe ser un número entero")
    
    if quantity_int < 0:
        raise ValidationError("La cantidad no puede ser negativa")
    
    if quantity_int > 10000:
        raise ValidationError("La cantidad excede el máximo permitido")
    
    return quantity_int


def validate_item_data(item_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida datos completos de un item
    
    Args:
        item_data: Diccionario con datos del item
    
    Returns:
        Diccionario validado y normalizado
    
    Raises:
        ValidationError: Si los datos no son válidos
    
    Examples:
        >>> data = {"name": "Item 1", "price": 10.5, "quantity": 5}
        >>> validate_item_data(data)
        {'name': 'Item 1', 'price': 10.5, 'quantity': 5}
    """
    if not isinstance(item_data, dict):
        raise ValidationError("Los datos del item deben ser un diccionario")
    
    # Validar nombre
    if "name" not in item_data:
        raise ValidationError("El nombre es requerido")
    validate_item_name(item_data["name"])
    
    # Validar precio (opcional)
    price = None
    if "price" in item_data:
        price = validate_item_price(item_data["price"])
    
    # Validar cantidad (opcional)
    quantity = None
    if "quantity" in item_data:
        quantity = validate_item_quantity(item_data["quantity"])
    
    # Construir item validado
    validated_item = {
        "name": item_data["name"].strip()
    }
    
    if price is not None:
        validated_item["price"] = price
    
    if quantity is not None:
        validated_item["quantity"] = quantity
    
    return validated_item


def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> bool:
    """
    Valida un rango de fechas
    
    Args:
        start_date: Fecha de inicio (formato ISO: YYYY-MM-DD)
        end_date: Fecha de fin (formato ISO: YYYY-MM-DD)
    
    Returns:
        True si el rango es válido
    
    Raises:
        ValidationError: Si el rango no es válido
    
    Examples:
        >>> validate_date_range("2026-01-01", "2026-12-31")
        True
    """
    if not start_date and not end_date:
        return True  # Ambas opcionales
    
    if start_date and not end_date:
        raise ValidationError("Si se especifica fecha de inicio, debe especificarse fecha de fin")
    
    if end_date and not start_date:
        raise ValidationError("Si se especifica fecha de fin, debe especificarse fecha de inicio")
    
    # Parsear fechas
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except ValueError:
        raise ValidationError("Las fechas deben estar en formato ISO (YYYY-MM-DD)")
    
    # Validar que start sea antes que end
    if start >= end:
        raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin")
    
    # Validar que no sean fechas muy antiguas
    min_date = datetime(2020, 1, 1)
    if start < min_date:
        raise ValidationError("La fecha de inicio no puede ser anterior a 2020")
    
    # Validar que no sean fechas muy futuras (más de 10 años)
    max_date = datetime.now().replace(year=datetime.now().year + 10)
    if end > max_date:
        raise ValidationError("La fecha de fin no puede ser superior a 10 años en el futuro")
    
    return True


def validate_pagination(page: Any, page_size: Any) -> tuple[int, int]:
    """
    Valida parámetros de paginación
    
    Args:
        page: Número de página
        page_size: Tamaño de página
    
    Returns:
        Tupla (page, page_size) validada
    
    Raises:
        ValidationError: Si los parámetros no son válidos
    
    Examples:
        >>> validate_pagination(1, 10)
        (1, 10)
    """
    # Validar page
    try:
        page_int = int(page)
    except (ValueError, TypeError):
        raise ValidationError("El número de página debe ser un entero")
    
    if page_int < 1:
        raise ValidationError("El número de página debe ser mayor o igual a 1")
    
    # Validar page_size
    try:
        page_size_int = int(page_size)
    except (ValueError, TypeError):
        raise ValidationError("El tamaño de página debe ser un entero")
    
    if page_size_int < 1:
        raise ValidationError("El tamaño de página debe ser mayor o igual a 1")
    
    if page_size_int > 100:
        raise ValidationError("El tamaño de página no puede exceder 100")
    
    return (page_int, page_size_int)


def validate_search_query(query: str, min_length: int = 2) -> str:
    """
    Valida una consulta de búsqueda
    
    Args:
        query: Consulta de búsqueda
        min_length: Longitud mínima requerida
    
    Returns:
        Query sanitizado
    
    Raises:
        ValidationError: Si la query no es válida
    
    Examples:
        >>> validate_search_query("test")
        'test'
    """
    if not query or not isinstance(query, str):
        raise ValidationError("La consulta de búsqueda es requerida")
    
    query = query.strip()
    
    if len(query) < min_length:
        raise ValidationError(f"La consulta debe tener al menos {min_length} caracteres")
    
    if len(query) > 100:
        raise ValidationError("La consulta no puede exceder 100 caracteres")
    
    # Sanitizar caracteres peligrosos
    dangerous_chars = ['<', '>', '"', "'", ';', '\\']
    for char in dangerous_chars:
        if char in query:
            raise ValidationError(f"La consulta contiene caracteres no permitidos: {char}")
    
    return query
