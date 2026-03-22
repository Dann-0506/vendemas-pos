class InventoryController:

    def __init__(self, db_manager):
        self.db = db_manager

    # ── Consultas ─────────────────────────────────────────────────────────────

    def obtener_todos(self):
        """Devuelve todos los productos activos."""
        return self.db.obtener_productos()

    def buscar(self, texto: str):
        """Filtra productos por nombre o categoría (case-insensitive)."""
        texto = texto.lower().strip()
        if not texto:
            return self.obtener_todos()
        return [
            p for p in self.obtener_todos()
            if texto in (p[1] or "").lower()
            or texto in (p[6] or "").lower()
        ]

    def obtener_por_codigo(self, codigo: str):
        return self.db.obtener_producto_por_codigo(codigo)

    # ── Validación ────────────────────────────────────────────────────────────

    def validar_campos(self, nombre, precio_str, stock_str) -> str | None:
        """
        Valida los campos obligatorios de un producto.
        Retorna un mensaje de error o None si todo es correcto.
        """
        if not nombre.strip():
            return "El nombre del producto es obligatorio."
        try:
            precio = float(precio_str)
            if precio < 0:
                raise ValueError
        except ValueError:
            return "El precio debe ser un número positivo."
        try:
            stock = int(stock_str)
            if stock < 0:
                raise ValueError
        except ValueError:
            return "El stock debe ser un número entero no negativo."
        return None

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def crear(self, nombre, descripcion, codigo_barras,
              precio_str, stock_str, categoria) -> str | None:
        """
        Valida y crea un producto.
        Retorna mensaje de error o None si tuvo éxito.
        """
        error = self.validar_campos(nombre, precio_str, stock_str)
        if error:
            return error
        self.db.crear_producto(
            nombre.strip(),
            descripcion.strip(),
            codigo_barras.strip(),
            float(precio_str),
            int(stock_str),
            categoria.strip()
        )
        return None

    def actualizar(self, id_producto, nombre, descripcion,
                   precio_str, stock_str, categoria) -> str | None:
        """
        Valida y actualiza un producto existente.
        Retorna mensaje de error o None si tuvo éxito.
        """
        error = self.validar_campos(nombre, precio_str, stock_str)
        if error:
            return error
        self.db.actualizar_producto(
            id_producto,
            nombre.strip(),
            descripcion.strip(),
            float(precio_str),
            int(stock_str),
            categoria.strip()
        )
        return None

    def eliminar(self, id_producto: int):
        self.db.eliminar_producto(id_producto)