"""
Utilidades y helpers de la aplicación
Funciones reutilizables de lógica de negocio
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import re


def parse_comma_separated_list(value: str, strip_whitespace: bool = True) -> List[str]:
    """
    Parsea una cadena separada por comas en una lista
    
    Args:
        value: String con valores separados por comas
        strip_whitespace: Si se debe eliminar espacios en blanco
    
    Returns:
        Lista de strings
    
    Examples:
        >>> parse_comma_separated_list("item1, item2, item3")
        ['item1', 'item2', 'item3']
    """
    if not value:
        return []
    
    items = value.split(",")
    
    if strip_whitespace:
        items = [item.strip() for item in items]
    
    # Filtrar items vacíos
    return [item for item in items if item]


def validate_email(email: str) -> bool:
    """
    Valida si un email tiene formato correcto
    
    Args:
        email: Email a validar
    
    Returns:
        True si es válido, False en caso contrario
    
    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not email:
        return False
    
    # Patrón básico de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitiza un string eliminando caracteres peligrosos
    
    Args:
        value: String a sanitizar
        max_length: Longitud máxima permitida
    
    Returns:
        String sanitizado
    
    Examples:
        >>> sanitize_string("<script>alert('xss')</script>")
        "scriptalert('xss')/script"
    """
    if not value:
        return ""
    
    # Eliminar caracteres HTML peligrosos
    sanitized = value.replace("<", "").replace(">", "")
    sanitized = sanitized.replace("'", "").replace('"', "")
    
    # Truncar si se especifica longitud máxima
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


def is_valid_url(url: str) -> bool:
    """
    Valida si una URL tiene formato correcto
    
    Args:
        url: URL a validar
    
    Returns:
        True si es válida, False en caso contrario
    
    Examples:
        >>> is_valid_url("https://example.com")
        True
        >>> is_valid_url("not-a-url")
        False
    """
    if not url:
        return False
    
    # Patrón básico de URL
    pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    return bool(re.match(pattern, url))


def calculate_time_remaining(expires_at: datetime) -> timedelta:
    """
    Calcula el tiempo restante hasta una fecha
    
    Args:
        expires_at: Fecha de expiración
    
    Returns:
        Timedelta con el tiempo restante
    
    Examples:
        >>> future = datetime.now() + timedelta(hours=2)
        >>> result = calculate_time_remaining(future)
        >>> result.total_seconds() > 0
        True
    """
    now = datetime.now()
    return expires_at - now


def format_file_size(size_bytes: int) -> str:
    """
    Formatea un tamaño de archivo en bytes a formato legible
    
    Args:
        size_bytes: Tamaño en bytes
    
    Returns:
        String formateado (ej: "10.5 MB")
    
    Examples:
        >>> format_file_size(1024)
        '1.0 KB'
        >>> format_file_size(1048576)
        '1.0 MB'
    """
    if size_bytes < 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combina dos diccionarios, dict2 sobrescribe dict1
    
    Args:
        dict1: Diccionario base
        dict2: Diccionario a combinar
    
    Returns:
        Diccionario combinado
    
    Examples:
        >>> merge_dicts({'a': 1, 'b': 2}, {'b': 3, 'c': 4})
        {'a': 1, 'b': 3, 'c': 4}
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Trunca un texto a una longitud máxima
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a añadir si se trunca
    
    Returns:
        Texto truncado
    
    Examples:
        >>> truncate_text("This is a long text", 10)
        'This is...'
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def validate_positive_number(value: Any) -> bool:
    """
    Valida si un valor es un número positivo
    
    Args:
        value: Valor a validar
    
    Returns:
        True si es positivo, False en caso contrario
    
    Examples:
        >>> validate_positive_number(5)
        True
        >>> validate_positive_number(-1)
        False
    """
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Divide una lista en chunks de tamaño específico
    
    Args:
        items: Lista a dividir
        chunk_size: Tamaño de cada chunk
    
    Returns:
        Lista de listas (chunks)
    
    Examples:
        >>> chunk_list([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size debe ser mayor que 0")
    
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
