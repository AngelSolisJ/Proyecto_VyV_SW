import sqlite3

def validar_datos_entrada(cantidad, precio, nombre=""):
    
    if not nombre.strip():
        return False, "El nombre del producto no puede estar vacío."
    
    try:
        cantidad = int(cantidad)
        if cantidad < 0:
            return False, "La cantidad debe ser mayor o igual a 0."
    except ValueError:
        return False, "La cantidad debe ser un número entero válido."
    
    try:
        precio = float(precio)
        if precio <= 0:
            return False, "El precio tiene que ser un valor positivo."
    except ValueError:
        return False, "El precio debe ser un número decimal válido."
    
    return True, "Datos válidos."