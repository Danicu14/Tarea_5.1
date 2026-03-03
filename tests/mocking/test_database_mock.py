"""
Tests de Mocking - Simulación de Base de Datos
===============================================

Simula operaciones de base de datos para evitar dependencia de BD real
y permitir tests rápidos, predecibles y sin efectos secundarios.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
from typing import List, Dict, Optional


# ============================================================================
# CLASE SIMULADA DE REPOSITORIO DE BASE DE DATOS
# ============================================================================

class User:
    """Modelo de usuario"""
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email
        self.created_at = datetime.now()


class UserRepository:
    """Repositorio de usuarios con acceso a BD"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene usuario por ID desde BD"""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return User(id=row[0], name=row[1], email=row[2])
        return None
    
    def create_user(self, name: str, email: str) -> User:
        """Crea un nuevo usuario en BD"""
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        self.db.commit()
        user_id = cursor.lastrowid
        return User(id=user_id, name=name, email=email)
    
    def get_all_users(self) -> List[User]:
        """Obtiene todos los usuarios"""
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return [User(id=r[0], name=r[1], email=r[2]) for r in rows]
    
    def delete_user(self, user_id: int) -> bool:
        """Elimina un usuario"""
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.db.commit()
        return cursor.rowcount > 0


class TestDatabaseMocking:
    """
    Tests con mocking de base de datos
    
    VENTAJAS DE MOCKEAR LA BD:
    1. Tests NO modifican base de datos real
    2. No necesitamos BD corriendo para tests
    3. Tests extremadamente rápidos (sin I/O)
    4. Podemos simular errores de BD fácilmente
    5. Tests aislados y sin efectos secundarios
    """
    
    def test_get_user_by_id_found(self):
        """Mock de consulta BD: Usuario encontrado"""
        # ARRANGE: Crear mock de BD
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        
        # Simular que el cursor devuelve un usuario
        mock_cursor.fetchone.return_value = (1, "Juan Pérez", "juan@example.com")
        mock_db.cursor.return_value = mock_cursor
        
        # ACT: Ejecutar operación
        repo = UserRepository(mock_db)
        user = repo.get_user_by_id(1)
        
        # ASSERT: Verificar resultados
        assert user is not None
        assert user.id == 1
        assert user.name == "Juan Pérez"
        assert user.email == "juan@example.com"
        
        # Verificar que se llamó a la BD correctamente
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM users WHERE id = ?", (1,)
        )
    
    def test_get_user_by_id_not_found(self):
        """Mock de consulta BD: Usuario no encontrado"""
        # ARRANGE: Simular usuario no existente
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # No hay resultado
        mock_db.cursor.return_value = mock_cursor
        
        # ACT
        repo = UserRepository(mock_db)
        user = repo.get_user_by_id(999)
        
        # ASSERT
        assert user is None
        mock_cursor.execute.assert_called_once()
    
    def test_create_user_success(self):
        """Mock de inserción en BD: Usuario creado exitosamente"""
        # ARRANGE
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 42  # ID auto-generado por BD
        mock_db.cursor.return_value = mock_cursor
        
        # ACT
        repo = UserRepository(mock_db)
        user = repo.create_user("María García", "maria@example.com")
        
        # ASSERT
        assert user.id == 42
        assert user.name == "María García"
        assert user.email == "maria@example.com"
        
        # Verificar que se hizo INSERT y COMMIT
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            ("María García", "maria@example.com")
        )
        mock_db.commit.assert_called_once()
    
    def test_get_all_users(self):
        """Mock de consulta BD: Obtener todos los usuarios"""
        # ARRANGE: Simular múltiples usuarios
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, "Usuario1", "user1@example.com"),
            (2, "Usuario2", "user2@example.com"),
            (3, "Usuario3", "user3@example.com")
        ]
        mock_db.cursor.return_value = mock_cursor
        
        # ACT
        repo = UserRepository(mock_db)
        users = repo.get_all_users()
        
        # ASSERT
        assert len(users) == 3
        assert users[0].name == "Usuario1"
        assert users[1].name == "Usuario2"
        assert users[2].name == "Usuario3"
    
    def test_delete_user_success(self):
        """Mock de eliminación en BD: Usuario eliminado"""
        # ARRANGE
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1  # 1 fila afectada
        mock_db.cursor.return_value = mock_cursor
        
        # ACT
        repo = UserRepository(mock_db)
        result = repo.delete_user(1)
        
        # ASSERT
        assert result is True
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM users WHERE id = ?", (1,)
        )
        mock_db.commit.assert_called_once()
    
    def test_delete_user_not_found(self):
        """Mock de eliminación BD: Usuario no existe"""
        # ARRANGE
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0  # 0 filas afectadas
        mock_db.cursor.return_value = mock_cursor
        
        # ACT
        repo = UserRepository(mock_db)
        result = repo.delete_user(999)
        
        # ASSERT
        assert result is False
    
    def test_database_connection_error(self):
        """Mock de error de conexión a BD"""
        # ARRANGE: Simular error de BD
        mock_db = MagicMock()
        mock_db.cursor.side_effect = Exception("Database connection lost")
        
        # ACT & ASSERT: Verificar que se propaga el error
        repo = UserRepository(mock_db)
        with pytest.raises(Exception, match="Database connection lost"):
            repo.get_user_by_id(1)


# ============================================================================
# MOCK DE ORM (SQLAlchemy simulado)
# ============================================================================

class Product:
    """Modelo de producto"""
    def __init__(self, id: int, name: str, price: float, stock: int):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock


class ProductService:
    """Servicio de productos usando ORM"""
    
    def __init__(self, session):
        self.session = session
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Obtiene producto por ID - Simplificado para mocking"""
        # Simulamos query ORM sin usar Product.id como atributo
        result = self.session.query_product(product_id)
        return result
    
    def create_product(self, name: str, price: float, stock: int) -> Product:
        """Crea un producto"""
        product = Product(id=0, name=name, price=price, stock=stock)
        self.session.add(product)
        self.session.commit()
        return product
    
    def update_stock(self, product_id: int, new_stock: int) -> bool:
        """Actualiza stock de producto"""
        product = self.get_product(product_id)
        if product:
            product.stock = new_stock
            self.session.commit()
            return True
        return False


class TestORMMocking:
    """Tests con mocking de ORM (SQLAlchemy)"""
    
    def test_get_product_with_orm_mock(self):
        """
        Mock de ORM: Obtener producto
        
        Beneficio: NO necesitamos SQLAlchemy configurado ni BD real
        """
        # ARRANGE: Mock de sesión ORM
        mock_session = MagicMock()
        
        # Configurar producto mockeado
        mock_product = Product(1, "Laptop", 999.99, 10)
        mock_session.query_product.return_value = mock_product
        
        # ACT
        service = ProductService(mock_session)
        product = service.get_product(1)
        
        # ASSERT
        assert product is not None
        assert product.name == "Laptop"
        assert product.price == 999.99
        assert product.stock == 10
        mock_session.query_product.assert_called_once_with(1)
    
    def test_create_product_with_orm_mock(self):
        """Mock de ORM: Crear producto"""
        # ARRANGE
        mock_session = MagicMock()
        
        # ACT
        service = ProductService(mock_session)
        product = service.create_product("Mouse", 29.99, 50)
        
        # ASSERT
        assert product.name == "Mouse"
        assert product.price == 29.99
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    def test_update_stock_success(self):
        """Mock de ORM: Actualizar stock"""
        # ARRANGE
        mock_session = MagicMock()
        
        mock_product = Product(1, "Teclado", 79.99, 20)
        mock_session.query_product.return_value = mock_product
        
        # ACT
        service = ProductService(mock_session)
        result = service.update_stock(1, 15)
        
        # ASSERT
        assert result is True
        assert mock_product.stock == 15
        mock_session.commit.assert_called_once()
    
    def test_update_stock_product_not_found(self):
        """Mock de ORM: Producto no encontrado"""
        # ARRANGE
        mock_session = MagicMock()
        
        # Producto no existe
        mock_session.query_product.return_value = None
        
        # ACT
        service = ProductService(mock_session)
        result = service.update_stock(999, 10)
        
        # ASSERT
        assert result is False
        # No debe llamar a commit si no hay producto
        assert mock_session.commit.call_count == 0
