import sqlite3
from contextlib import contextmanager


class POSDatabase:

    def __init__(self, db_name="pos.db"):
        self.db_name = db_name
        self._conn = None
        self.crear_tablas()

    # -----------------------------
    # conexión (Singleton-like / Persistent)
    # -----------------------------
    @property
    def connection(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
        return self._conn

    @contextmanager
    def transaction(self):
        """Manejador de contexto para transacciones atómicas."""
        conn = self.connection
        try:
            yield conn.cursor()
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    # -----------------------------
    # crear tablas e índices
    # -----------------------------
    def crear_tablas(self):
        with self.transaction() as cursor:
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

            # Índices para mejorar rendimiento de búsqueda y predicción
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_producto_codigo ON producto(codigo_barras)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_producto_nombre ON producto(nombre)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_venta_fecha ON venta(fecha)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_venta_producto ON venta(id_producto)")

    # =============================
    # CRUD PRODUCTOS (SQL-Optimized)
    # =============================

    def crear_producto(self, nombre, descripcion, codigo_barras, precio, stock, categoria):
        with self.transaction() as cursor:
            cursor.execute("""
            INSERT INTO producto (nombre, descripcion, codigo_barras, precio, stock, categoria)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre, descripcion, codigo_barras, precio, stock, categoria))

    def obtener_productos(self, solo_activos=True, con_stock=False):
        """Obtiene productos con filtros opcionales aplicados en SQL."""
        query = "SELECT * FROM producto WHERE 1=1"
        params = []
        if solo_activos:
            query += " AND activo = 1"
        if con_stock:
            query += " AND stock > 0"
        
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return [tuple(row) for row in cursor.fetchall()]

    def buscar_productos(self, texto, solo_con_stock=False):
        """Busca productos usando SQL LIKE para máxima eficiencia."""
        query = """
        SELECT * FROM producto 
        WHERE (nombre LIKE ? OR categoria LIKE ? OR codigo_barras LIKE ?)
        AND activo = 1
        """
        params = [f"%{texto}%", f"%{texto}%", f"%{texto}%"]
        
        if solo_con_stock:
            query += " AND stock > 0"
            
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return [tuple(row) for row in cursor.fetchall()]

    def obtener_producto_por_id(self, id_producto):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM producto WHERE id_producto = ?", (id_producto,))
        row = cursor.fetchone()
        return tuple(row) if row else None

    def obtener_producto_por_codigo(self, codigo):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM producto WHERE codigo_barras = ?", (codigo,))
        row = cursor.fetchone()
        return tuple(row) if row else None

    def actualizar_producto(self, id_producto, nombre, descripcion, precio, stock, categoria):
        with self.transaction() as cursor:
            cursor.execute("""
            UPDATE producto
            SET nombre = ?, descripcion = ?, precio = ?, stock = ?, categoria = ?
            WHERE id_producto = ?
            """, (nombre, descripcion, precio, stock, categoria, id_producto))

    def eliminar_producto(self, id_producto):
        with self.transaction() as cursor:
            cursor.execute("DELETE FROM producto WHERE id_producto = ?", (id_producto,))

    # =============================
    # VENTAS (Transaccional)
    # =============================

    def procesar_venta_lote(self, items_carrito):
        """Procesa múltiples ventas en una única transacción atómica."""
        try:
            with self.transaction() as cursor:
                for item in items_carrito:
                    # 1. Verificar stock y obtener precio actual
                    cursor.execute("SELECT precio, stock FROM producto WHERE id_producto = ?", (item.id_producto,))
                    prod = cursor.fetchone()
                    
                    if not prod or prod['stock'] < item.cantidad:
                        raise ValueError(f"Stock insuficiente para {item.nombre}")

                    # 2. Registrar venta
                    total = prod['precio'] * item.cantidad
                    cursor.execute("""
                    INSERT INTO venta (id_producto, cantidad, precio_unitario, total)
                    VALUES (?, ?, ?, ?)
                    """, (item.id_producto, item.cantidad, prod['precio'], total))

                    # 3. Actualizar stock
                    cursor.execute("""
                    UPDATE producto SET stock = stock - ? WHERE id_producto = ?
                    """, (item.cantidad, item.id_producto))
            return True, "Venta procesada con éxito"
        except Exception as e:
            return False, str(e)

    def obtener_ventas_recientes(self, limite=50):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM venta ORDER BY fecha DESC LIMIT ?", (limite,))
        return [tuple(row) for row in cursor.fetchall()]

    def obtener_agregados_ventas(self, dias=30):
        """Calcula ventas totales por producto en un periodo usando SQL puro."""
        query = """
        SELECT id_producto, SUM(cantidad) as total_vendido
        FROM venta
        WHERE fecha >= date('now', ?)
        GROUP BY id_producto
        """
        cursor = self.connection.cursor()
        cursor.execute(query, (f"-{dias} days",))
        return {row['id_producto']: row['total_vendido'] for row in cursor.fetchall()}

