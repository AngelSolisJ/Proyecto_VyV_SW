# validacion.py (CÓDIGO CORREGIDO)
import sqlite3

# Eliminamos 'self' y 'id_producto'
def validar_datos_entrada(cantidad, precio, nombre=""):
    
    # Nota: También corregí el error de tipeo "prodcuto" y "nuemero"
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
        if precio <= 0: # Corregido a <= 0 para incluir cero como inválido
            return False, "El precio tiene que ser un valor positivo."
    except ValueError:
        return False, "El precio debe ser un número decimal válido."
    
    return True, "Datos válidos."