import pytest
import app as app_module
from DB import BaseDatos

# -----------------------
# Pruebas de la capa DB
# -----------------------
def test_db_validar_usuario_registrar_y_validar():
    db = BaseDatos(db_name=":memory:")
    ok, msg = db.registrar_usuario("usuario_test", "pass_test", es_admin=0)
    assert ok is True
    valido, id_usuario, es_admin = db.validar_usuario("usuario_test", "pass_test")
    assert valido is True
    assert isinstance(id_usuario, int)
    assert es_admin is False

    valido2, _, _ = db.validar_usuario("usuario_test", "wrongpass")
    assert valido2 is False

    valido3, _, _ = db.validar_usuario("no_existe", "whatever")
    assert valido3 is False

# -----------------------
# Helper para crear la App de forma aislada (sin Tk)
# -----------------------
def make_app_with_memory_db():
    """
    Creamos una instancia de AplicacionUnificada SIN ejecutar __init__,
    y le damos los atributos mínimos que usan los tests:
    - db (BaseDatos en memoria)
    - usuario_entry, contraseña_entry (objetos con get(), delete(), focus())
    - mostrar_inventario (función stub)
    Devolvemos (app, root_stub) donde root_stub tiene destroy() y withdraw()
    para mantener compatibilidad con los tests originales.
    """
    # Crear objeto sin llamar a __init__
    app = object.__new__(app_module.AplicacionUnificada)
    app.db = BaseDatos(db_name=":memory:")
    app.usuario_actual = None
    app.es_admin_actual = False

    class DummyEntry:
        def __init__(self, value=""):
            self._value = value
        def get(self):
            return self._value
        def delete(self, a, b=None):
            # simular borrar; los tests solo comprueban que se llamó
            return None
        def focus(self):
            return None

    app.usuario_entry = DummyEntry()
    app.contraseña_entry = DummyEntry()

    # Métodos/atributos que podrían ser llamados por la lógica
    def limpiar_contenedor():
        return None
    app.limpiar_contenedor = limpiar_contenedor

    def mostrar_inventario():
        return None
    app.mostrar_inventario = mostrar_inventario

    # root stub (tiene destroy y withdraw para compatibilidad)
    class RootStub:
        def withdraw(self): pass
        def destroy(self): pass

    return app, RootStub()

# -----------------------
# Pruebas de la lógica de login (validar_login)
# -----------------------
def test_validar_login_campos_vacios_muestra_error(monkeypatch):
    app, root = make_app_with_memory_db()

    captured = {}
    def fake_showerror(title, message):
        captured['title'] = title
        captured['message'] = message

    monkeypatch.setattr(app_module.messagebox, "showerror", fake_showerror)

    app.usuario_entry.get = lambda: ""
    app.contraseña_entry.get = lambda: ""

    app.validar_login()

    assert "Por favor ingrese usuario y contraseña." in captured.get('message', "")
    root.destroy()

def test_validar_login_credenciales_invalidas_muestra_error_y_borra_contraseña(monkeypatch):
    app, root = make_app_with_memory_db()

    called = {}
    def fake_showerror(title, message):
        called['title'] = title
        called['message'] = message
    monkeypatch.setattr(app_module.messagebox, "showerror", fake_showerror)

    # Forzamos que la validación de BD devuelva inválido
    app.db.validar_usuario = lambda usuario, contraseña: (False, None, False)

    app.usuario_entry.get = lambda: "alguno"
    app.contraseña_entry.get = lambda: "incorrecta"

    deleted = {'called': False}
    def fake_delete(a, b=None):
        deleted['called'] = True
    app.contraseña_entry.delete = fake_delete

    focused = {'called': False}
    def fake_focus():
        focused['called'] = True
    app.usuario_entry.focus = fake_focus

    app.validar_login()

    assert "Usuario o contraseña incorrectos." in called.get('message', "")
    assert deleted['called'] is True
    assert focused['called'] is True
    root.destroy()

def test_validar_login_credenciales_validas_llama_mostrar_inventario_y_setea_usuario(monkeypatch):
    app, root = make_app_with_memory_db()

    ok, msg = app.db.registrar_usuario("miusuario", "mipass", es_admin=1)
    assert ok

    called = {'mostrar': False}
    def fake_mostrar_inventario():
        called['mostrar'] = True
    app.mostrar_inventario = fake_mostrar_inventario

    app.usuario_entry.get = lambda: "miusuario"
    app.contraseña_entry.get = lambda: "mipass"

    app.validar_login()

    assert app.usuario_actual == "miusuario"
    assert app.es_admin_actual is True
    assert called['mostrar'] is True
    root.destroy()

def test_validar_login_usuario_no_admin_flag(monkeypatch):
    app, root = make_app_with_memory_db()

    ok, msg = app.db.registrar_usuario("user_normal", "pwd", es_admin=0)
    assert ok

    called = {'mostrar': False}
    app.mostrar_inventario = lambda: called.__setitem__('mostrar', True)

    app.usuario_entry.get = lambda: "user_normal"
    app.contraseña_entry.get = lambda: "pwd"

    app.validar_login()

    assert app.usuario_actual == "user_normal"
    assert app.es_admin_actual is False
    assert called['mostrar'] is True
    root.destroy()