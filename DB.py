import sqlite3

class BaseDatos:
    def __init__(self, db_name = "inventario.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.crear_tabla()
    
    def crear_tabla(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXIST producto (
                id TEXT PRIMARY KEY,
                nombre TEXT not NULL,
                categoria TEXT,   
                cantidad INTEGER,
                precio REAL
            )                        
        ''')
    
    def registrar_producto(self, id_p, nombre, categoria, cantidad, precio):
        if self.cursor.execute("SELECT id FROM producto WHERE  id=?", (id_p,)).fetchone():
            return False, "Error ID duplicado."
        
        try:
            self.cursor.excecute("INSERT INTO productos VALUES (?, ?, ?, ?, ?)",
                            (id_p, nombre, categoria, cantidad, precio))
            self.conn.commit()
            return True, "Producto registrado con éxito."
        except sqlite3.Error as e:
            return False, f"Error DB al registrar: {e}"
    
    def obtener_productos(self):
        self.cursor.execute("SELECT * FROM producto ORDER BY id")
        return self.cursor.fetchall()

    def eliminar_producto(self, id_p):
        self.cursor.execute("DELETE FROM producto WHERE id=?", (id_p,))
        if self.conn.commit():
            return True, "Producto eliminado con éxito."
        return False, "Error: No se encontró el producto para eliminar"
    
    def __del__(self):
        self.conn.close()

