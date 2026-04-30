from dataclasses import dataclass, field


@dataclass
class CartItem:
    """Representa un producto dentro del carrito."""
    id_producto: int
    nombre:      str
    precio:      float
    cantidad:    int = 1

    @property
    def subtotal(self) -> float:
        return round(self.precio * self.cantidad, 2)


class SalesController:
    """
    Lógica de negocio del módulo de Ventas.
    Gestiona el carrito y el proceso de cobro.
    No importa customtkinter.
    """

    IVA_RATE = 0.16

    def __init__(self, db_manager):
        self.db    = db_manager
        self._cart: list[CartItem] = []

    # Catálogo

    def obtener_productos_disponibles(self):
        """Devuelve productos con stock > 0 usando SQL."""
        return self.db.obtener_productos(solo_activos=True, con_stock=True)

    def buscar_producto(self, texto: str):
        """Filtra productos disponibles por nombre, categoría o código usando SQL."""
        texto = texto.lower().strip()
        if not texto:
            return self.obtener_productos_disponibles()
        return self.db.buscar_productos(texto, solo_con_stock=True)

    # Carrito

    def agregar_al_carrito(self, id_producto: int,
                           nombre: str, precio: float) -> str | None:
        """
        Agrega o incrementa un producto en el carrito.
        Retorna mensaje de error o None si tuvo éxito.
        """
        # Verificar stock disponible consultando solo el producto necesario
        prod = self.db.obtener_producto_por_id(id_producto)
        if not prod:
            return f"Producto '{nombre}' no encontrado."
        
        stock_actual = prod[5]
        
        for item in self._cart:
            if item.id_producto == id_producto:
                if item.cantidad >= stock_actual:
                    return f"Stock insuficiente para '{nombre}'."
                item.cantidad += 1
                return None

        if stock_actual <= 0:
            return f"Stock insuficiente para '{nombre}'."

        self._cart.append(CartItem(id_producto, nombre, precio))
        return None

    def cambiar_cantidad(self, id_producto: int, delta: int) -> str | None:
        """
        Incrementa o decrementa la cantidad de un item.
        Elimina el item si la cantidad llega a 0.
        """
        for item in self._cart:
            if item.id_producto == id_producto:
                nueva = item.cantidad + delta
                if nueva <= 0:
                    self._cart.remove(item)
                    return None
                
                prod = self.db.obtener_producto_por_id(id_producto)
                if delta > 0 and prod and nueva > prod[5]:
                    return f"Stock insuficiente para '{item.nombre}'."
                item.cantidad = nueva
                return None
        return "Producto no encontrado en el carrito."

    def eliminar_del_carrito(self, id_producto: int):
        self._cart = [i for i in self._cart if i.id_producto != id_producto]

    def limpiar_carrito(self):
        self._cart.clear()

    def obtener_carrito(self) -> list[CartItem]:
        return list(self._cart)

    # Totales

    def calcular_subtotal(self) -> float:
        return round(sum(i.subtotal for i in self._cart), 2)

    def calcular_iva(self) -> float:
        return round(self.calcular_subtotal() * self.IVA_RATE, 2)

    def calcular_total(self) -> float:
        return round(self.calcular_subtotal() + self.calcular_iva(), 2)

    def obtener_resumen(self) -> dict:
        """Devuelve un dict con subtotal, iva y total."""
        return {
            "subtotal": self.calcular_subtotal(),
            "iva":      self.calcular_iva(),
            "total":    self.calcular_total(),
        }

    # Cobro

    def procesar_cobro(self) -> tuple[bool, str]:
        """
        Registra todas las ventas del carrito en una sola transacción.
        """
        if not self._cart:
            return False, "El carrito está vacío."

        exito, mensaje = self.db.procesar_venta_lote(self._cart)
        
        if exito:
            self.limpiar_carrito()
            
        return exito, mensaje

    # Helpers privados

    def _get_producto(self, id_producto: int):
        for p in self.db.obtener_productos():
            if p[0] == id_producto:
                return p
        return None