import sqlite3

def validar_datos_entrada(self, id_producto, cantidad, precio, nombre=""):
    
    if not nombre.strip():
        return False, "El nombre del prodcuto no puede estar vacio."
    
    try:
        cantidad = int(cantidad)
        if cantidad < 0:
            return False, "La cantidad debe ser mayor o igual a 0."
    except ValueError:
        return False, "La cantidad debe ser un numero entero valido."
    
    try:
        precio = float(precio)
        if precio < 0:
            return False, "El precio tiene que ser un valor positivo"
    except ValueError:
        return False, "El precio debe ser un  nuemero decimal valido"
    
    return True, "Datos validos"