import sqlite3

class BaseDatos:
    def __init__(self, db_name = "inventario.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.crear_tabla()
    
    def _normalizar_id(self, id_p):
        """Normalize ID by removing leading zeros from numeric IDs"""
        if not id_p or str(id_p).strip() == "":
            return ""
        id_str = str(id_p).strip()
        # If it's purely numeric, convert to int and back to remove leading zeros
        if id_str.isdigit():
            return str(int(id_str))
        return id_str
    
    def crear_tabla(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS producto (
                id TEXT PRIMARY KEY,
                nombre TEXT not NULL,
                categoria TEXT,   
                cantidad INTEGER,
                precio REAL
            )                        
        ''')
    
    def registrar_producto(self, id_p, nombre, categoria, cantidad, precio):
        try:
            # Normalize the ID
            id_normalizado = self._normalizar_id(id_p)
            
            # If id is blank or None, generate next numeric id
            if not id_normalizado:
                rows = self.cursor.execute("SELECT id FROM producto").fetchall()
                max_id = 0
                for (rid,) in rows:
                    try:
                        v = int(rid)
                        if v > max_id:
                            max_id = v
                    except Exception:
                        continue
                next_id = str(max_id + 1)
                self.cursor.execute("INSERT INTO producto VALUES (?, ?, ?, ?, ?)",
                                    (next_id, nombre, categoria, cantidad, precio))
                self.conn.commit()
                return True, f"Producto registrado con éxito con ID {next_id}."

            # If id provided and exists -> update
            existing = self.cursor.execute("SELECT id FROM producto WHERE id=?", (id_normalizado,)).fetchone()
            if existing:
                return self.actualizar_producto(id_normalizado, nombre, categoria, cantidad, precio)

            # Otherwise insert with provided id
            self.cursor.execute("INSERT INTO producto VALUES (?, ?, ?, ?, ?)",
                                (id_normalizado, nombre, categoria, cantidad, precio))
            self.conn.commit()
            return True, "Producto registrado con éxito."
        except sqlite3.Error as e:
            return False, f"Error DB al registrar: {e}"
    
    def obtener_productos(self):
        self.cursor.execute("SELECT * FROM producto ORDER BY id")
        return self.cursor.fetchall()

    def actualizar_producto(self, id_p, nombre, categoria, cantidad, precio):
        try:
            self.cursor.execute(
                "UPDATE producto SET nombre=?, categoria=?, cantidad=?, precio=? WHERE id=?",
                (nombre, categoria, cantidad, precio, id_p)
            )
            self.conn.commit()
            if self.cursor.rowcount == 0:
                return False, "Error: Producto no encontrado para actualizar."
            return True, "Producto actualizado con éxito."
        except sqlite3.Error as e:
            return False, f"Error DB: {e}"


    def eliminar_producto(self, id_p):
        self.cursor.execute("DELETE FROM producto WHERE id=?", (id_p,))
        filas_afectadas = self.cursor.rowcount
        self.conn.commit()
        if filas_afectadas > 0:
            return True, "Producto eliminado con éxito."
        else:
            return False, "Error: No se encontró el producto para eliminar"
    
    def __del__(self):
        try:
            self.conn.close()
        except Exception:
            pass


