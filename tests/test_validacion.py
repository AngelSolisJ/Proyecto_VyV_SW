import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Validacion_datos import validar_datos_entrada


def test_validacion_valida_campos_ok():
    valido, mensaje = validar_datos_entrada("3", "2.5", "Producto X")
    assert valido


def test_validacion_nombre_vacio():
    valido, mensaje = validar_datos_entrada("1", "1.0", "   ")
    assert not valido


def test_validacion_cantidad_invalida():
    valido, mensaje = validar_datos_entrada("abc", "1.0", "Prod")
    assert not valido


def test_validacion_precio_invalido():
    valido, mensaje = validar_datos_entrada("1", "-5", "Prod")
    assert not valido


def test_validacion_precio_cero():
    """Test that price of zero is invalid"""
    valido, mensaje = validar_datos_entrada("1", "0", "Prod")
    assert not valido
    assert "positivo" in mensaje.lower()


def test_validacion_cantidad_negativa():
    """Test that negative quantity is invalid"""
    valido, mensaje = validar_datos_entrada("-1", "1.0", "Prod")
    assert not valido
    assert "mayor o igual" in mensaje.lower()


def test_validacion_cantidad_cero():
    """Test that zero quantity is valid"""
    valido, mensaje = validar_datos_entrada("0", "1.0", "Prod")
    assert valido


def test_validacion_precio_no_numerico():
    """Test that non-numeric price is invalid"""
    valido, mensaje = validar_datos_entrada("1", "abc", "Prod")
    assert not valido
    assert "decimal válido" in mensaje.lower()


def test_validacion_cantidad_decimal():
    """Test that decimal quantity is invalid"""
    valido, mensaje = validar_datos_entrada("1.5", "1.0", "Prod")
    assert not valido
    assert "entero válido" in mensaje.lower()


def test_validacion_nombre_solo_espacios():
    """Test that name with only spaces is invalid"""
    valido, mensaje = validar_datos_entrada("1", "1.0", "     ")
    assert not valido
    assert "vacío" in mensaje.lower()


def test_validacion_precio_muy_grande():
    """Test that very large price is valid"""
    valido, mensaje = validar_datos_entrada("1", "999999.99", "Prod")
    assert valido


def test_validacion_cantidad_muy_grande():
    """Test that very large quantity is valid"""
    valido, mensaje = validar_datos_entrada("1000000", "1.0", "Prod")
    assert valido


def test_validacion_nombre_con_caracteres_especiales():
    """Test that name with special characters is valid"""
    valido, mensaje = validar_datos_entrada("1", "1.0", "Prod@#$%123")
    assert valido


def test_validacion_precio_decimal_valido():
    """Test that valid decimal price works"""
    valido, mensaje = validar_datos_entrada("5", "12.99", "Producto")
    assert valido
