import customtkinter as ctk
from ..utils import constants as C

CATEGORY_COLORS = {
    "Bebidas": "#e3f2fd",
    "Botanas": "#f3e5f5",
    "Básicos": "#e8f5e9",
    "Dulces":  "#fff3e0",
    "Lácteos": "#e0f7fa",
    "Otros":   "#f5f5f5",
}
DEFAULT_ACCENT = "#f0f0f0"


class SalesView(ctk.CTkFrame):

    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._ctrl = controller             # SalesController

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_products_panel()
        self._build_cart_panel()

        # Diferir carga hasta que la ventana esté renderizada
        self.after(0, self._refresh_products)

    # ── Encabezado ────────────────────────────────────────────────────────────

    def _build_header(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 0), sticky="ew")
        ctk.CTkLabel(f, text="Punto de Venta",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=C.PRIMARY).pack(anchor="w")
        ctk.CTkLabel(f, text="Selecciona productos y procesa el cobro",
                     font=ctk.CTkFont(size=13),
                     text_color=C.TEXT_SECONDARY).pack(anchor="w")

    # ── Panel izquierdo: catálogo ─────────────────────────────────────────────

    def _build_products_panel(self):
        panel = ctk.CTkFrame(self, fg_color=C.CARD, corner_radius=C.CORNER_RADIUS_LG,
                             border_width=C.BORDER_WIDTH, border_color=C.BORDER)
        panel.grid(row=1, column=0, padx=(20, 8), pady=20, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        tb = ctk.CTkFrame(panel, fg_color="transparent")
        tb.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        tb.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(tb, text="Productos Disponibles",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=C.TEXT_PRIMARY).grid(row=0, column=0, sticky="w")

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh_products())
        ctk.CTkEntry(panel, textvariable=self._search_var,
                     placeholder_text="Buscar producto o escanear código...",
                     height=40, font=ctk.CTkFont(size=13),
                     fg_color=C.BG, border_color=C.BORDER,
                     border_width=C.BORDER_WIDTH, text_color=C.TEXT_PRIMARY
                     ).grid(row=1, column=0, padx=16, pady=(0, 10), sticky="ew")

        self._grid_frame = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self._grid_frame.grid(row=2, column=0, padx=8, pady=(0, 12), sticky="nsew")
        self._N_COLS = 3
        for c in range(self._N_COLS):
            self._grid_frame.grid_columnconfigure(c, weight=1, uniform="prod_col")

    def _refresh_products(self):
        q        = self._search_var.get() if hasattr(self, '_search_var') else ""
        products = self._ctrl.buscar_producto(q)

        for w in self._grid_frame.winfo_children():
            w.destroy()

        if not products:
            ctk.CTkLabel(self._grid_frame, text="No se encontraron productos.",
                         font=ctk.CTkFont(size=13), text_color=C.TEXT_HINT
                         ).grid(row=0, column=0, columnspan=self._N_COLS, pady=30)
            return

        for idx, prod in enumerate(products):
            accent = CATEGORY_COLORS.get(prod[6] or "", DEFAULT_ACCENT)
            self._make_product_card(
                self._grid_frame,
                id_producto = prod[0],
                nombre      = prod[1],
                categoria   = prod[6] or "—",
                precio      = prod[4],
                stock       = prod[5],
                accent      = accent,
                row         = idx // self._N_COLS,
                col         = idx % self._N_COLS,
            )

    def _make_product_card(self, parent, id_producto, nombre, categoria,
                           precio, stock, accent, row, col):
        card = ctk.CTkFrame(parent, fg_color=C.CARD, corner_radius=10,
                            border_width=C.BORDER_WIDTH, border_color=C.BORDER)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(card, fg_color=accent, height=6,
                     corner_radius=0).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(card, text=nombre,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=C.TEXT_PRIMARY, wraplength=130, justify="center"
                     ).grid(row=1, column=0, padx=10, pady=(10, 2))
        ctk.CTkLabel(card, text=categoria,
                     font=ctk.CTkFont(size=11), text_color=C.TEXT_HINT
                     ).grid(row=2, column=0, padx=10, pady=(0, 6))
        ctk.CTkLabel(card, text=f"${precio:,.2f}",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=C.PRIMARY
                     ).grid(row=3, column=0, padx=10, pady=(0, 4))

        stock_color = C.DANGER if stock == 0 else (C.WARNING if stock < C.STOCK_LOW else C.SUCCESS)
        ctk.CTkLabel(card, text=f"Stock: {stock}",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="white", fg_color=stock_color, corner_radius=6
                     ).grid(row=4, column=0, padx=20, pady=(0, 8), sticky="ew")

        ctk.CTkButton(card, text="+ Agregar", height=32,
                      fg_color=C.PRIMARY, hover_color=C.PRIMARY_HOVER,
                      text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
                      corner_radius=C.CORNER_RADIUS_MD,
                      state="disabled" if stock == 0 else "normal",
                      command=lambda i=id_producto, n=nombre, p=precio:
                          self._add_to_cart(i, n, p)
                      ).grid(row=5, column=0, padx=10, pady=(0, 12), sticky="ew")

    # ── Panel derecho: carrito ────────────────────────────────────────────────

    def _build_cart_panel(self):
        self._cart_panel = ctk.CTkFrame(self, fg_color=C.CARD,
                                        corner_radius=C.CORNER_RADIUS_LG,
                                        border_width=C.BORDER_WIDTH, border_color=C.BORDER)
        self._cart_panel.grid(row=1, column=1, padx=(8, 20), pady=20, sticky="nsew")
        self._cart_panel.grid_columnconfigure(0, weight=1)
        self._cart_panel.grid_rowconfigure(1, weight=1)

        # Encabezado
        ch = ctk.CTkFrame(self._cart_panel, fg_color=C.HDR_BG,
                          corner_radius=0, height=50)
        ch.grid(row=0, column=0, sticky="ew", padx=1, pady=(1, 0))
        ch.grid_propagate(False)
        ch.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(ch, text="Carrito de Venta",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C.TEXT_PRIMARY
                     ).grid(row=0, column=0, padx=16, sticky="w", pady=14)
        ctk.CTkButton(ch, text="Limpiar", width=70, height=28,
                      fg_color="transparent", border_width=1, border_color=C.BORDER,
                      text_color=C.TEXT_MUTED, hover_color="#f0f0f0",
                      font=ctk.CTkFont(size=11), corner_radius=6,
                      command=self._clear_cart
                      ).grid(row=0, column=1, padx=(0, 12), pady=11)

        # Lista
        self._cart_list = ctk.CTkScrollableFrame(self._cart_panel, fg_color="transparent")
        self._cart_list.grid(row=1, column=0, padx=1, pady=0, sticky="nsew")
        self._cart_list.grid_columnconfigure(0, weight=1)

        # Totales
        self._totals_frame = ctk.CTkFrame(self._cart_panel, fg_color=C.BG,
                                          corner_radius=0,
                                          border_width=C.BORDER_WIDTH, border_color=C.BORDER)
        self._totals_frame.grid(row=2, column=0, sticky="ew", padx=1, pady=(0, 1))
        self._totals_frame.grid_columnconfigure(1, weight=1)

        # Ventas recientes
        self._recent_frame = ctk.CTkFrame(self._cart_panel, fg_color="transparent")
        self._recent_frame.grid(row=3, column=0, padx=16, pady=(8, 16), sticky="ew")
        self._recent_frame.grid_columnconfigure(0, weight=1)

        self._refresh_cart()

    def _refresh_cart(self):
        for w in self._cart_list.winfo_children():
            w.destroy()

        items = self._ctrl.obtener_carrito()

        if not items:
            ctk.CTkLabel(self._cart_list,
                         text="El carrito está vacío.\nAgrega productos para comenzar.",
                         font=ctk.CTkFont(size=12), text_color=C.TEXT_HINT,
                         justify="center"
                         ).grid(row=0, column=0, pady=30)
        else:
            for idx, item in enumerate(items):
                self._make_cart_item(idx, item)

        self._refresh_totals()

    def _make_cart_item(self, idx, item):
        bg = C.CARD if idx % 2 == 0 else C.BG

        row = ctk.CTkFrame(self._cart_list, fg_color=bg, corner_radius=0)
        row.grid(row=idx, column=0, sticky="ew", pady=(0, 1))
        row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(row, text=item.nombre,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=C.TEXT_PRIMARY, anchor="w"
                     ).grid(row=0, column=0, padx=14, pady=(10, 2), sticky="ew")
        ctk.CTkLabel(row, text=f"${item.precio:.2f} c/u",
                     font=ctk.CTkFont(size=11), text_color=C.TEXT_HINT, anchor="w"
                     ).grid(row=1, column=0, padx=14, pady=(0, 8), sticky="ew")

        controls = ctk.CTkFrame(row, fg_color="transparent")
        controls.grid(row=0, column=1, rowspan=2, padx=10, pady=8)

        ctk.CTkButton(controls, text="−", width=28, height=28,
                      fg_color=C.BG, hover_color="#e0e0e0",
                      text_color=C.TEXT_SECONDARY, border_width=1,
                      border_color=C.BORDER,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      corner_radius=C.CORNER_RADIUS_SM,
                      command=lambda i=item.id_producto: self._change_qty(i, -1)
                      ).pack(side="left")

        ctk.CTkLabel(controls, text=str(item.cantidad),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C.TEXT_PRIMARY, width=28).pack(side="left")

        ctk.CTkButton(controls, text="+", width=28, height=28,
                      fg_color=C.PRIMARY, hover_color=C.PRIMARY_HOVER,
                      text_color="white",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      corner_radius=C.CORNER_RADIUS_SM,
                      command=lambda i=item.id_producto: self._change_qty(i, +1)
                      ).pack(side="left")

        ctk.CTkLabel(row, text=f"${item.subtotal:.2f}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C.PRIMARY
                     ).grid(row=0, column=2, rowspan=2, padx=(4, 6))

        ctk.CTkButton(row, text="✕", width=26, height=26,
                      fg_color="transparent",
                      border_width=1, border_color="#ffcccc",
                      text_color=C.DANGER, hover_color="#fff0f0",
                      font=ctk.CTkFont(size=11, weight="bold"),
                      corner_radius=C.CORNER_RADIUS_SM,
                      command=lambda i=item.id_producto: self._remove_item(i)
                      ).grid(row=0, column=3, rowspan=2, padx=(0, 10))

    def _refresh_totals(self):
        for w in self._totals_frame.winfo_children():
            w.destroy()

        resumen  = self._ctrl.obtener_resumen()
        subtotal = resumen["subtotal"]
        iva      = resumen["iva"]
        total    = resumen["total"]

        for i, (label, valor, bold) in enumerate([
            ("Subtotal",  f"${subtotal:,.2f}", False),
            ("IVA (16%)", f"${iva:,.2f}",      False),
            ("TOTAL",     f"${total:,.2f}",     True),
        ]):
            ctk.CTkLabel(self._totals_frame, text=label,
                         font=ctk.CTkFont(size=13, weight="bold" if bold else "normal"),
                         text_color=C.TEXT_PRIMARY if bold else C.TEXT_MUTED
                         ).grid(row=i, column=0, padx=16,
                                pady=(14 if i == 0 else 4, 4), sticky="w")
            ctk.CTkLabel(self._totals_frame, text=valor,
                         font=ctk.CTkFont(size=14 if bold else 13,
                                          weight="bold" if bold else "normal"),
                         text_color=C.PRIMARY if bold else C.TEXT_SECONDARY
                         ).grid(row=i, column=1, padx=16, sticky="e")

        ctk.CTkFrame(self._totals_frame, height=1, fg_color=C.BORDER
                     ).grid(row=3, column=0, columnspan=2, padx=12, pady=8, sticky="ew")

        ctk.CTkButton(self._totals_frame, text=f"Cobrar  ${total:,.2f}",
                      height=48, fg_color=C.SUCCESS, hover_color=C.SUCCESS_HOVER,
                      text_color="white", font=ctk.CTkFont(size=15, weight="bold"),
                      corner_radius=10, command=self._procesar_cobro
                      ).grid(row=4, column=0, columnspan=2,
                             padx=14, pady=(0, 14), sticky="ew")

    def _refresh_recent_sales(self):
        for w in self._recent_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(self._recent_frame, text="Ventas recientes",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=C.TEXT_MUTED
                     ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ventas    = self._ctrl.db.obtener_ventas()
        recientes = list(reversed(ventas[-3:])) if ventas else []

        if not recientes:
            ctk.CTkLabel(self._recent_frame, text="Sin ventas registradas aún.",
                         font=ctk.CTkFont(size=11), text_color=C.TEXT_HINT
                         ).grid(row=1, column=0, sticky="w")
            return

        self._recent_frame.grid_columnconfigure(0, weight=1)
        for i, venta in enumerate(recientes):
            row_f = ctk.CTkFrame(self._recent_frame, fg_color=C.BG,
                                 corner_radius=C.CORNER_RADIUS_MD,
                                 border_width=C.BORDER_WIDTH, border_color=C.BORDER)
            row_f.grid(row=i+1, column=0, sticky="ew", pady=3)
            row_f.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row_f, text=f"#{venta[0]:03d}",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=C.PRIMARY
                         ).grid(row=0, column=0, padx=12, pady=8)
            ctk.CTkLabel(row_f, text=venta[5][:16] if venta[5] else "—",
                         font=ctk.CTkFont(size=11), text_color=C.TEXT_HINT
                         ).grid(row=0, column=1, sticky="w")
            ctk.CTkLabel(row_f, text=f"${venta[4]:,.2f}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=C.TEXT_PRIMARY
                         ).grid(row=0, column=2, padx=12)

    # ── Acciones — delega al controller ──────────────────────────────────────

    def _add_to_cart(self, id_producto, nombre, precio):
        error = self._ctrl.agregar_al_carrito(id_producto, nombre, precio)
        if error:
            from .alert_modal import AlertModal
            AlertModal(self, error)
        else:
            self._refresh_cart()

    def _change_qty(self, id_producto, delta):
        error = self._ctrl.cambiar_cantidad(id_producto, delta)
        if error:
            from .alert_modal import AlertModal
            AlertModal(self, error)
        else:
            self._refresh_cart()

    def _remove_item(self, id_producto):
        self._ctrl.eliminar_del_carrito(id_producto)
        self._refresh_cart()

    def _clear_cart(self):
        self._ctrl.limpiar_carrito()
        self._refresh_cart()

    def _procesar_cobro(self):
        exito, mensaje = self._ctrl.procesar_cobro()
        if exito:
            self._refresh_cart()
            self._refresh_products()
            self._refresh_recent_sales()
        else:
            from .alert_modal import AlertModal
            AlertModal(self, mensaje)