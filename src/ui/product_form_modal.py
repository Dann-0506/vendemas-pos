import customtkinter as ctk
from .alert_modal import AlertModal
from ..utils import constants as C


class ProductFormModal(ctk.CTkToplevel):
    """Modal reutilizable para Crear y Editar productos."""

    def __init__(self, master, db_manager, on_save_callback, producto=None):
        super().__init__(master)
        self.db       = db_manager
        self.on_save  = on_save_callback
        self.producto = producto
        is_edit       = producto is not None

        self.title("Editar Producto" if is_edit else "Nuevo Producto")
        self.geometry("500x640")
        self.minsize(500, 640)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color=C.BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build(is_edit)
        self.after(50, self._post_init, is_edit)

    def _on_close(self):
        self.grab_release()
        self.destroy()

    def _post_init(self, is_edit):
        self.lift()
        self.focus_force()
        self.grab_set()
        self.bind("<FocusOut>", self._on_focus_out)
        if is_edit:
            self._fill()

    def _on_focus_out(self, event):
        if self.focus_get() is None:
            self.after(10, self.focus_force)

    def _build(self, is_edit):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Franja azul de encabezado
        header = ctk.CTkFrame(self, fg_color=C.PRIMARY, corner_radius=0, height=70)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header,
                     text="Editar Producto" if is_edit else "Nuevo Producto",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color="white"
                     ).grid(row=0, column=0, padx=24, sticky="w")

        ctk.CTkLabel(header,
                     text="Modifica los datos del producto" if is_edit
                     else "Completa los datos del nuevo producto",
                     font=ctk.CTkFont(size=12),
                     text_color="#cce5ff"
                     ).grid(row=1, column=0, padx=24, sticky="w", pady=(0, 10))

        # Tarjeta blanca con formulario
        card = ctk.CTkFrame(self, fg_color=C.CARD,
                            corner_radius=12, border_width=1, border_color=C.BORDER)
        card.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        scroll.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        self._entries = {}
        for lbl, key in [
            ("Nombre del producto *", "nombre"),
            ("Descripción",           "descripcion"),
            ("Código de barras",      "codigo_barras"),
            ("Precio (MXN) *",        "precio"),
            ("Stock *",               "stock"),
            ("Categoría",             "categoria"),
        ]:
            ctk.CTkLabel(scroll, text=lbl,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=C.TEXT_SECONDARY, anchor="w"
                         ).grid(row=len(self._entries)*2, column=0,
                                sticky="ew", padx=16, pady=(14, 2))
            entry = ctk.CTkEntry(scroll, height=42,
                                 font=ctk.CTkFont(size=13),
                                 fg_color=C.BG,
                                 border_color=C.BORDER, border_width=1,
                                 text_color=C.TEXT_PRIMARY, corner_radius=8)
            entry.grid(row=len(self._entries)*2+1, column=0,
                       sticky="ew", padx=16, pady=(0, 2))
            self._entries[key] = entry

        # Barra de botones fija en la parte inferior
        btn_bar = ctk.CTkFrame(self, fg_color=C.BG,
                               border_width=1, border_color=C.BORDER,
                               corner_radius=0, height=64)
        btn_bar.grid(row=2, column=0, sticky="ew")
        btn_bar.grid_propagate(False)
        btn_bar.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_bar, text="Cancelar",
                      fg_color="transparent", border_width=2, border_color=C.BORDER,
                      text_color=C.TEXT_SECONDARY, hover_color="#e9ecef",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      height=40, corner_radius=8,
                      command=self._on_close
                      ).grid(row=0, column=0, padx=(16, 8), pady=12, sticky="ew")

        ctk.CTkButton(btn_bar,
                      text="Guardar Cambios" if is_edit else "Crear Producto",
                      fg_color=C.PRIMARY, hover_color=C.PRIMARY_HOVER,
                      text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
                      height=40, corner_radius=8,
                      command=self._guardar
                      ).grid(row=0, column=1, padx=(8, 16), pady=12, sticky="ew")

    def _fill(self):
        # prod: (id, nombre, descripcion, codigo_barras, precio, stock, categoria, activo)
        p = self.producto
        for key, val in [
            ("nombre",        p[1]),
            ("descripcion",   p[2] or ""),
            ("codigo_barras", p[3] or ""),
            ("precio",        str(p[4])),
            ("stock",         str(p[5])),
            ("categoria",     p[6] or ""),
        ]:
            self._entries[key].delete(0, "end")
            self._entries[key].insert(0, val)

    def _guardar(self):
        nombre        = self._entries["nombre"].get().strip()
        descripcion   = self._entries["descripcion"].get().strip()
        codigo_barras = self._entries["codigo_barras"].get().strip()
        precio_str    = self._entries["precio"].get().strip()
        stock_str     = self._entries["stock"].get().strip()
        categoria     = self._entries["categoria"].get().strip()

        if not nombre:
            AlertModal(self, "El nombre del producto es obligatorio.")
            return
        try:
            precio = float(precio_str)
            assert precio >= 0
        except Exception:
            AlertModal(self, "El precio debe ser un número positivo.")
            return
        try:
            stock = int(stock_str)
            assert stock >= 0
        except Exception:
            AlertModal(self, "El stock debe ser un número entero no negativo.")
            return

        if self.producto is None:
            self.db.crear_producto(nombre, descripcion, codigo_barras, precio, stock, categoria)
        else:
            self.db.actualizar_producto(
                self.producto[0], nombre, descripcion, precio, stock, categoria
            )
        self.on_save()
        self.destroy()