import sqlite3

class BaseDatos:
    def __init__(self, db_name="inventario.db"):
        self.conn = sqlite3.connect(db_name, timeout=10, check_same_thread=False)
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
        nombre_limpio = nombre_categoria.strip()
        
        self.cursor.execute("SELECT id FROM categoria WHERE nombre = ?", (nombre_limpio,))
        resultado = self.cursor.fetchone()
        
        if resultado:
            return resultado[0]
        else:
            self.cursor.execute("INSERT INTO categoria (nombre) VALUES (?)", (nombre_limpio,))
            self.conn.commit()
            return self.cursor.lastrowid

    def _get_first_free_id(self, table='producto'):
        """
        Devuelve el menor entero positivo >=1 que NO está presente en la columna id de la tabla.
        """
        self.cursor.execute(f"SELECT id FROM {table} ORDER BY id")
        rows = self.cursor.fetchall()
        ids = [r[0] for r in rows]
        next_id = 1
        for v in ids:
            if v == next_id:
                next_id += 1
            elif v > next_id:
                break
        return next_id

    def registrar_producto(self, id_p, nombre, categoria_texto, cantidad, precio):
        """
        Registra un producto. Devuelve una tupla (exito:bool, mensaje:str, nuevo_id:int|None).

        - Si no se proporciona ID (id_p vacío o None) -> calcular el primer ID libre y 
          hacer INSERT especificando ese ID (reusa IDs eliminados).
        - Si se proporciona un ID:
            - Si el ID ya existe, la función RECHAZA la inserción y devuelve (False, mensaje, None).
            - Si el ID no existe, inserta con ese ID y devuelve (True, mensaje, id_int).
        """
        try:
            cat_id = self._gestionar_categoria(categoria_texto)

            # Normalizar id_p vacío / None
            if id_p is None or str(id_p).strip() == "":
                # Insertar con el primer ID libre (reusar IDs eliminados).
                try:
                    # Reservar la DB para evitar carrera: BEGIN IMMEDIATE bloquea escrituras concurrentes.
                    # Si hay error (p. ej. otro proceso ya tiene bloqueo), seguirá y SQLite lanzará excepción en el INSERT si hay conflicto.
                    self.conn.execute("BEGIN IMMEDIATE")
                except sqlite3.OperationalError:
                    # Si no se puede iniciar la transacción inmediata, se continúa y confiamos en el INSERT/commit para fallar en caso de conflicto.
                    pass

                try:
                    nuevo_id = self._get_first_free_id('producto')
                    self.cursor.execute("""
                        INSERT INTO producto (id, nombre, categoria_id, cantidad, precio)
                        VALUES (?, ?, ?, ?, ?)
                    """, (nuevo_id, nombre, cat_id, cantidad, precio))
                    self.conn.commit()
                    return True, f"Producto registrado con éxito con ID {nuevo_id}.", nuevo_id
                except sqlite3.IntegrityError as e:
                    # En caso de conflicto (otro proceso insertó el mismo ID entre la selección e INSERT),
                    # hacer rollback y reportar error (o podríamos reintentar varias veces).
                    try:
                        self.conn.rollback()
                    except Exception:
                        pass
                    return False, f"Error DB: conflicto al asignar ID. Intente nuevamente. ({e})", None
                except sqlite3.Error as e:
                    try:
                        self.conn.rollback()
                    except Exception:
                        pass
                    return False, f"Error DB al registrar: {e}", None

            # Si se proporcionó ID, validar y usarlo si está libre
            try:
                id_int = int(str(id_p).lstrip("0") or "0")
                if id_int == 0:
                    # si el usuario ingresó algo como "0" o "00", normalizamos a 0 y rechazamos (IDs empiezan en 1)
                    return False, "Error: El ID debe ser un entero positivo mayor o igual a 1.", None
            except ValueError:
                return False, "Error: El ID debe ser un número entero.", None
            
            # Si el ID ya existe, NO insertar ni actualizar desde aquí: devolver error y pedir usar Actualizar
            existing = self.cursor.execute("SELECT id FROM producto WHERE id=?", (id_int,)).fetchone()
            if existing:
                return False, f"Error: El ID {id_int} ya existe. Use 'Actualizar' para modificar el producto.", None

            # Insertar con ID específico (si no existe)
            try:
                self.cursor.execute("""
                    INSERT INTO producto (id, nombre, categoria_id, cantidad, precio) 
                    VALUES (?, ?, ?, ?, ?)
                """, (id_int, nombre, cat_id, cantidad, precio))
                self.conn.commit()
                return True, f"Producto registrado con éxito con ID {id_int}.", id_int
            except sqlite3.IntegrityError as e:
                try:
                    self.conn.rollback()
                except Exception:
                    pass
                return False, f"Error DB al registrar con ID especificado: {e}", None
            
        except sqlite3.Error as e:
            try:
                self.conn.rollback()
            except Exception:
                pass
            return False, f"Error DB al registrar: {e}", None
    
    def obtener_productos(self, filtro=None):
        """
        Devuelve productos. Si filtro es None o vacío devuelve todos.
        Si filtro es numérico busca por ID exacto. Si no, busca por nombre parcial (LIKE, case-insensitive).
        """
        if filtro is None or str(filtro).strip() == "":
            query = """
                SELECT p.id, p.nombre, c.nombre, p.cantidad, p.precio 
                FROM producto p
                JOIN categoria c ON p.categoria_id = c.id
                ORDER BY p.id
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        else:
            f = str(filtro).strip()
            # intentar buscar por ID exacto
            try:
                id_int = int(f)
                query = """
                    SELECT p.id, p.nombre, c.nombre, p.cantidad, p.precio
                    FROM producto p
                    JOIN categoria c ON p.categoria_id = c.id
                    WHERE p.id = ?
                    ORDER BY p.id
                """
                self.cursor.execute(query, (id_int,))
                return self.cursor.fetchall()
            except ValueError:
                # búsqueda por nombre parcial (LIKE)
                like = f"%{f}%"
                query = """
                    SELECT p.id, p.nombre, c.nombre, p.cantidad, p.precio
                    FROM producto p
                    JOIN categoria c ON p.categoria_id = c.id
                    WHERE LOWER(p.nombre) LIKE LOWER(?)
                    ORDER BY p.id
                """
                self.cursor.execute(query, (like,))
                return self.cursor.fetchall()

    def actualizar_producto(self, id_p, nombre, categoria_texto, cantidad, precio):
        try:
            try:
                id_int = int(str(id_p).lstrip("0") or "0")
            except ValueError:
                return False, "Error: El ID debe ser un número entero."
            
            if id_int == 0:
                return False, "Error: El ID debe ser un entero positivo mayor o igual a 1."

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
            try:
                self.conn.rollback()
            except Exception:
                pass
            return False, f"Error DB: {e}"

    def eliminar_producto(self, id_p):
        try:
            id_int = int(str(id_p).lstrip("0") or "0")
            if id_int == 0:
                return False, "Error: El ID debe ser un número entero positivo."
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
            try:
                self.conn.rollback()
            except Exception:
                pass
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
            try:
                self.conn.rollback()
            except Exception:
                pass
            return False, f"Error DB: {e}"
    
    def __del__(self):
        try:
            self.conn.close()
        except Exception:
            pass    