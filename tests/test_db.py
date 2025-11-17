import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from DB import BaseDatos


def test_registrar_con_id_en_blanco_autoincrement():
    db = BaseDatos(":memory:")
    exito, mensaje = db.registrar_producto("", "Producto A", "Alimentos", 2, 1.5)
    assert exito
    productos = db.obtener_productos()
    assert len(productos) == 1
    # id should be 1 for first auto-increment
    assert productos[0][0] == 1


def test_registrar_con_id_personalizado_nuevo():
    db = BaseDatos(":memory:")
    exito, mensaje = db.registrar_producto("100", "Producto B", "Bebidas", 3, 2.0)
    assert exito
    productos = db.obtener_productos()
    assert any(p[0] == 100 for p in productos)


def test_registrar_con_id_existente_actualiza():
    db = BaseDatos(":memory:")
    exito, _ = db.registrar_producto("5", "Prod1", "Limpieza", 1, 1.0)
    assert exito

    # Register with same id should perform update
    exito_upd, msg = db.registrar_producto("5", "Prod1-mod", "Limpieza", 10, 2.0)
    assert exito_upd
    productos = db.obtener_productos()
    p5 = [p for p in productos if p[0] == 5][0]
    assert p5[1] == "Prod1-mod"
    assert p5[3] == 10
    assert abs(p5[4] - 2.0) < 1e-9


def test_autoincrement_secuencial():
    """Test that auto-increment IDs are sequential"""
    db = BaseDatos(":memory:")
    db.registrar_producto("", "Prod1", "Alimentos", 1, 1.0)
    db.registrar_producto("", "Prod2", "Bebidas", 2, 2.0)
    db.registrar_producto("", "Prod3", "Limpieza", 3, 3.0)
    
    productos = db.obtener_productos()
    ids = [p[0] for p in productos]
    assert ids == [1, 2, 3]


def test_autoincrement_despues_de_id_personalizado():
    """Test auto-increment continues correctly after custom IDs"""
    db = BaseDatos(":memory:")
    db.registrar_producto("100", "ProdCustom", "Otros", 1, 1.0)
    db.registrar_producto("", "ProdAuto", "Alimentos", 2, 2.0)
    
    productos = db.obtener_productos()
    auto_id = [p for p in productos if p[1] == "ProdAuto"][0][0]
    assert auto_id == 101


def test_eliminar_producto_existente():
    """Test deleting an existing product"""
    db = BaseDatos(":memory:")
    db.registrar_producto("50", "ToDelete", "Alimentos", 5, 5.0)
    
    exito, msg = db.eliminar_producto("50")
    assert exito
    assert "eliminado con éxito" in msg
    
    productos = db.obtener_productos()
    assert not any(p[0] == 50 for p in productos)


def test_eliminar_producto_inexistente():
    """Test attempting to delete non-existent product"""
    db = BaseDatos(":memory:")
    exito, msg = db.eliminar_producto("999")
    assert not exito
    assert "no se encontró" in msg.lower()


def test_actualizar_producto_inexistente():
    """Test updating a non-existent product fails"""
    db = BaseDatos(":memory:")
    exito, msg = db.actualizar_producto("999", "Nombre", "Cat", 1, 1.0)
    assert not exito
    assert "no encontrado" in msg.lower()


def test_registrar_multiples_productos_diferentes():
    """Test registering multiple products with different IDs"""
    db = BaseDatos(":memory:")
    db.registrar_producto("10", "ProdA", "Alimentos", 10, 5.0)
    db.registrar_producto("20", "ProdB", "Bebidas", 20, 10.0)
    db.registrar_producto("", "ProdC", "Limpieza", 30, 15.0)
    
    productos = db.obtener_productos()
    assert len(productos) == 3
    assert any(p[0] == 10 and p[1] == 'ProdA' for p in productos)
    assert any(p[0] == 20 and p[1] == 'ProdB' for p in productos)


def test_obtener_productos_vacio():
    """Test getting products from empty database"""
    db = BaseDatos(":memory:")
    productos = db.obtener_productos()
    assert productos == []


def test_id_none_autoincrement():
    """Test that None ID is treated as blank and auto-increments"""
    db = BaseDatos(":memory:")
    exito, mensaje = db.registrar_producto(None, "ProdNone", "Alimentos", 1, 1.0)
    assert exito
    productos = db.obtener_productos()
    assert len(productos) == 1
    assert productos[0][0] == 1


def test_id_con_ceros_delante_normaliza():
    """Test that IDs with leading zeros are normalized (02 -> 2)"""
    db = BaseDatos(":memory:")
    exito, _ = db.registrar_producto("02", "Prod1", "Alimentos", 1, 1.0)
    assert exito
    
    productos = db.obtener_productos()
    assert len(productos) == 1
    assert productos[0][0] == 2


def test_ids_duplicados_con_ceros_actualiza():
    """Test that 2, 02, 0002 are treated as the same ID"""
    db = BaseDatos(":memory:")
    
    # Register with ID "2"
    exito1, _ = db.registrar_producto("2", "Prod1", "Alimentos", 1, 1.0)
    assert exito1
    
    # Try to register with "02" - should update, not create new
    exito2, msg2 = db.registrar_producto("02", "Prod2", "Bebidas", 2, 2.0)
    assert exito2
    
    # Try to register with "0002" - should update again
    exito3, msg3 = db.registrar_producto("0002", "Prod3", "Limpieza", 3, 3.0)
    assert exito3
    
    # Should only have 1 product with the updated info
    productos = db.obtener_productos()
    assert len(productos) == 1
    assert productos[0][0] == 2
    assert productos[0][1] == 'Prod3'
    assert productos[0][3] == 3


def test_id_alfanumerico_rechaza():
    """Test that alphanumeric IDs are rejected"""
    db = BaseDatos(":memory:")
    exito, msg = db.registrar_producto("ABC02", "ProdAlfa", "Alimentos", 1, 1.0)
    assert not exito
    assert "entero" in msg.lower()
