import sqlite3


class POSDatabase:

    def __init__(self, db_name="pos.db"):
        self.db_name = db_name
        self.crear_tablas()

    # -----------------------------
    # conexión
    # -----------------------------
    def conectar(self):
        return sqlite3.connect(self.db_name)

    # -----------------------------
    # crear tablas
    # -----------------------------
    def crear_tablas(self):
        conn = self.conectar()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS producto (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            codigo_barras TEXT UNIQUE,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            categoria TEXT,
            activo INTEGER DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS venta (
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            total REAL NOT NULL,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
        )
        """)

        conn.commit()
        conn.close()

    # =============================
    # CRUD PRODUCTOS
    # =============================

    def crear_producto(self, nombre, descripcion, codigo_barras, precio, stock, categoria):
        conn = self.conectar()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO producto (nombre, descripcion, codigo_barras, precio, stock, categoria)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, descripcion, codigo_barras, precio, stock, categoria))

        conn.commit()
        conn.close()

    def obtener_productos(self):
        conn = self.conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM producto")
        productos = cursor.fetchall()

        conn.close()
        return productos

    def obtener_producto_por_codigo(self, codigo):
        conn = self.conectar()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM producto WHERE codigo_barras = ?
        """, (codigo,))

        producto = cursor.fetchone()

        conn.close()
        return producto

    def actualizar_producto(self, id_producto, nombre, descripcion, precio, stock, categoria):
        conn = self.conectar()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE producto
        SET nombre = ?, descripcion = ?, precio = ?, stock = ?, categoria = ?
        WHERE id_producto = ?
        """, (nombre, descripcion, precio, stock, categoria, id_producto))

        conn.commit()
        conn.close()

    def eliminar_producto(self, id_producto):
        conn = self.conectar()
        cursor = conn.cursor()

        cursor.execute("""
        DELETE FROM producto WHERE id_producto = ?
        """, (id_producto,))

        conn.commit()
        conn.close()

    # =============================
    # VENTAS
    # =============================

    def registrar_venta(self, id_producto, cantidad):
        conn = self.conectar()
        cursor = conn.cursor()

        # obtener producto
        cursor.execute("""
        SELECT precio, stock FROM producto WHERE id_producto = ?
        """, (id_producto,))
        producto = cursor.fetchone()

        if producto is None:
            conn.close()
            return "Producto no encontrado"

        precio, stock = producto

        if stock < cantidad:
            conn.close()
            return "Stock insuficiente"

        total = precio * cantidad

        # registrar venta
        cursor.execute("""
        INSERT INTO venta (id_producto, cantidad, precio_unitario, total)
        VALUES (?, ?, ?, ?)
        """, (id_producto, cantidad, precio, total))

        # actualizar stock
        cursor.execute("""
        UPDATE producto
        SET stock = stock - ?
        WHERE id_producto = ?
        """, (cantidad, id_producto))

        conn.commit()
        conn.close()

        return "Venta registrada"

    def obtener_ventas(self):
        conn = self.conectar()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM venta
        """)

        ventas = cursor.fetchall()

        conn.close()
        return ventas

