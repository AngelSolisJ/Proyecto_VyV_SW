import sqlite3

class BaseDatos:
    def __init__(self, db_name="inventario.db"):
        self.conn = sqlite3.connect(db_name)
        # Activar soporte para llaves foráneas (Foreign Keys)
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.cursor = self.conn.cursor()
        self.crear_tablas()
    
    def crear_tablas(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS producto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria_id INTEGER,   
                cantidad INTEGER,
                precio REAL,
                FOREIGN KEY (categoria_id) REFERENCES categoria (id)
            )                        
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_usuario TEXT NOT NULL UNIQUE,
                contraseña TEXT NOT NULL,
                es_admin INTEGER NOT NULL DEFAULT 0
            )
        ''')
        
        self.cursor.execute("SELECT COUNT(*) FROM usuario WHERE nombre_usuario = 'admin'")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(
                "INSERT INTO usuario (nombre_usuario, contraseña, es_admin) VALUES (?, ?, ?)",
                ("admin", "1234", 1)
            )
        
        self.conn.commit()

    def _gestionar_categoria(self, nombre_categoria):
        """
        Método privado auxiliar:
        Busca el ID de una categoría. Si no existe, la crea.
        Retorna el ID numérico de la categoría.
        """
        nombre_limpio = nombre_categoria.strip()
        
        # Buscamos si ya existe
        self.cursor.execute("SELECT id FROM categoria WHERE nombre = ?", (nombre_limpio,))
        resultado = self.cursor.fetchone()
        
        if resultado:
            return resultado[0] # Retorna el ID existente
        else:
            # Si no existe, la creamos
            self.cursor.execute("INSERT INTO categoria (nombre) VALUES (?)", (nombre_limpio,))
            self.conn.commit()
            return self.cursor.lastrowid # Retorna el nuevo ID

    def registrar_producto(self, id_p, nombre, categoria_texto, cantidad, precio):
        try:
            # Primero obtenemos el ID de la categoría (el usuario manda texto, nosotros guardamos ID)
            cat_id = self._gestionar_categoria(categoria_texto)

            if not id_p or str(id_p).strip() == "":
                # Registro nuevo con ID automático
                self.cursor.execute("""
                    INSERT INTO producto (nombre, categoria_id, cantidad, precio) 
                    VALUES (?, ?, ?, ?)
                """, (nombre, cat_id, cantidad, precio))
                
                self.conn.commit()
                nuevo_id = self.cursor.lastrowid
                return True, f"Producto registrado con éxito con ID {nuevo_id}."
            
            # Lógica para ID personalizado
            try:
                id_int = int(id_p)
            except ValueError:
                return False, "Error: El ID debe ser un número entero."
            
            existing = self.cursor.execute("SELECT id FROM producto WHERE id=?", (id_int,)).fetchone()
            if existing:
                # Si existe, actualizamos
                return self.actualizar_producto(id_int, nombre, categoria_texto, cantidad, precio)

            # Insertar con ID específico manual
            self.cursor.execute("""
                INSERT INTO producto (id, nombre, categoria_id, cantidad, precio) 
                VALUES (?, ?, ?, ?, ?)
            """, (id_int, nombre, cat_id, cantidad, precio))
            
            self.conn.commit()
            return True, "Producto registrado con éxito."
            
        except sqlite3.Error as e:
            return False, f"Error DB al registrar: {e}"
    
    def obtener_productos(self):
        # Hacemos un JOIN para traer el NOMBRE de la categoría, no el número
        query = """
            SELECT p.id, p.nombre, c.nombre, p.cantidad, p.precio 
            FROM producto p
            JOIN categoria c ON p.categoria_id = c.id
            ORDER BY p.id
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def actualizar_producto(self, id_p, nombre, categoria_texto, cantidad, precio):
        try:
            try:
                id_int = int(id_p)
            except ValueError:
                return False, "Error: El ID debe ser un número entero."
            
            # Obtenemos el ID de la categoría nuevamente
            cat_id = self._gestionar_categoria(categoria_texto)
            
            self.cursor.execute("""
                UPDATE producto 
                SET nombre=?, categoria_id=?, cantidad=?, precio=? 
                WHERE id=?
            """, (nombre, cat_id, cantidad, precio, id_int))
            
            self.conn.commit()
            if self.cursor.rowcount == 0:
                return False, "Error: Producto no encontrado para actualizar."
            return True, "Producto actualizado con éxito."
        except sqlite3.Error as e:
            return False, f"Error DB: {e}"

    def eliminar_producto(self, id_p):
        try:
            id_int = int(id_p)
        except ValueError:
            return False, "Error: El ID debe ser un número entero."
        
        self.cursor.execute("DELETE FROM producto WHERE id=?", (id_int,))
        filas_afectadas = self.cursor.rowcount
        self.conn.commit()
        if filas_afectadas > 0:
            return True, "Producto eliminado con éxito."
        else:
            return False, "Error: No se encontró el producto para eliminar"
    
    def validar_usuario(self, nombre_usuario, contraseña):
        self.cursor.execute(
            "SELECT id, es_admin FROM usuario WHERE nombre_usuario = ? AND contraseña = ?",
            (nombre_usuario, contraseña)
        )
        resultado = self.cursor.fetchone()
        if resultado:
            return True, resultado[0], bool(resultado[1])
        return False, None, False
    
    def registrar_usuario(self, nombre_usuario, contraseña, es_admin=0):
        try:
            self.cursor.execute(
                "INSERT INTO usuario (nombre_usuario, contraseña, es_admin) VALUES (?, ?, ?)",
                (nombre_usuario, contraseña, es_admin)
            )
            self.conn.commit()
            return True, "Usuario registrado con éxito."
        except sqlite3.IntegrityError:
            return False, "Error: El nombre de usuario ya existe."
        except sqlite3.Error as e:
            return False, f"Error DB: {e}"
    
    def obtener_usuarios(self):
        self.cursor.execute("SELECT id, nombre_usuario, es_admin FROM usuario ORDER BY id")
        return self.cursor.fetchall()
    
    def eliminar_usuario(self, id_usuario):
        try:
            id_int = int(id_usuario)
            self.cursor.execute("SELECT nombre_usuario FROM usuario WHERE id = ?", (id_int,))
            usuario = self.cursor.fetchone()
            
            if usuario and usuario[0] == "admin":
                return False, "Error: No se puede eliminar el usuario admin."
            
            self.cursor.execute("DELETE FROM usuario WHERE id=?", (id_int,))
            filas_afectadas = self.cursor.rowcount
            self.conn.commit()
            
            if filas_afectadas > 0:
                return True, "Usuario eliminado con éxito."
            else:
                return False, "Error: No se encontró el usuario."
        except ValueError:
            return False, "Error: El ID debe ser un número entero."
        except sqlite3.Error as e:
            return False, f"Error DB: {e}"
    
    def __del__(self):
        try:
            self.conn.close()
        except Exception:
            pass