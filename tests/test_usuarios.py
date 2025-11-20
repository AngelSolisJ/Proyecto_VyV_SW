import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from DB import BaseDatos


def test_registrar_usuario_nuevo():
    """Test registering a new user"""
    db = BaseDatos(":memory:")
    exito, mensaje = db.registrar_usuario("usuario1", "pass123", 0)
    assert exito
    assert "éxito" in mensaje.lower()


def test_registrar_usuario_admin():
    """Test registering a new admin user"""
    db = BaseDatos(":memory:")
    exito, mensaje = db.registrar_usuario("admin2", "admin123", 1)
    assert exito
    usuarios = db.obtener_usuarios()
    admin_users = [u for u in usuarios if u[1] == "admin2"]
    assert len(admin_users) == 1
    assert admin_users[0][2] == 1


def test_registrar_usuario_duplicado():
    """Test that duplicate usernames are rejected"""
    db = BaseDatos(":memory:")
    db.registrar_usuario("usuario1", "pass1", 0)
    exito, mensaje = db.registrar_usuario("usuario1", "pass2", 0)
    assert not exito
    assert "ya existe" in mensaje.lower()


def test_validar_usuario_correcto():
    """Test validating a user with correct credentials"""
    db = BaseDatos(":memory:")
    db.registrar_usuario("testuser", "testpass", 0)
    valido, id_usuario, es_admin = db.validar_usuario("testuser", "testpass")
    assert valido
    assert id_usuario is not None
    assert es_admin == False


def test_validar_usuario_admin():
    """Test validating an admin user"""
    db = BaseDatos(":memory:")
    db.registrar_usuario("adminuser", "adminpass", 1)
    valido, id_usuario, es_admin = db.validar_usuario("adminuser", "adminpass")
    assert valido
    assert es_admin == True


def test_validar_usuario_incorrecto():
    """Test validating with incorrect credentials"""
    db = BaseDatos(":memory:")
    db.registrar_usuario("testuser", "testpass", 0)
    valido, id_usuario, es_admin = db.validar_usuario("testuser", "wrongpass")
    assert not valido
    assert id_usuario is None
    assert es_admin == False


def test_validar_usuario_inexistente():
    """Test validating a non-existent user"""
    db = BaseDatos(":memory:")
    valido, id_usuario, es_admin = db.validar_usuario("noexiste", "pass")
    assert not valido
    assert id_usuario is None


def test_obtener_usuarios():
    """Test getting all users"""
    db = BaseDatos(":memory:")
    db.registrar_usuario("user1", "pass1", 0)
    db.registrar_usuario("user2", "pass2", 1)
    usuarios = db.obtener_usuarios()
    # Should have admin (default) + 2 new users = 3 total
    assert len(usuarios) >= 3
    user_names = [u[1] for u in usuarios]
    assert "user1" in user_names
    assert "user2" in user_names


def test_eliminar_usuario_existente():
    """Test deleting an existing user"""
    db = BaseDatos(":memory:")
    db.registrar_usuario("todelete", "pass", 0)
    usuarios = db.obtener_usuarios()
    user_to_delete = [u for u in usuarios if u[1] == "todelete"][0]
    
    exito, mensaje = db.eliminar_usuario(user_to_delete[0])
    assert exito
    assert "éxito" in mensaje.lower()
    
    usuarios_after = db.obtener_usuarios()
    assert not any(u[1] == "todelete" for u in usuarios_after)


def test_eliminar_usuario_admin_protegido():
    """Test that admin user cannot be deleted"""
    db = BaseDatos(":memory:")
    usuarios = db.obtener_usuarios()
    admin_user = [u for u in usuarios if u[1] == "admin"][0]
    
    exito, mensaje = db.eliminar_usuario(admin_user[0])
    assert not exito
    assert "admin" in mensaje.lower()


def test_eliminar_usuario_inexistente():
    """Test deleting a non-existent user"""
    db = BaseDatos(":memory:")
    exito, mensaje = db.eliminar_usuario(9999)
    assert not exito
    assert "no se encontró" in mensaje.lower()


def test_usuario_admin_creado_por_defecto():
    """Test that default admin user is created automatically"""
    db = BaseDatos(":memory:")
    valido, id_usuario, es_admin = db.validar_usuario("admin", "1234")
    assert valido
    assert es_admin == True


def test_multiples_usuarios_diferentes_roles():
    """Test creating multiple users with different roles"""
    db = BaseDatos(":memory:")
    db.registrar_usuario("user_normal", "pass1", 0)
    db.registrar_usuario("user_admin", "pass2", 1)
    
    valido1, _, es_admin1 = db.validar_usuario("user_normal", "pass1")
    valido2, _, es_admin2 = db.validar_usuario("user_admin", "pass2")
    
    assert valido1 and not es_admin1
    assert valido2 and es_admin2
