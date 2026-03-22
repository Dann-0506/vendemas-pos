import customtkinter as ctk
from .product_form_modal import ProductFormModal
from .confirm_delete_modal import ConfirmDeleteModal

# ─────────────────────────────────────────────────────────────────────────────
# Configuración de columnas de la tabla
# ─────────────────────────────────────────────────────────────────────────────
COLS = [
    # (label,       minsize, weight)
    ("ID",          70,      0),
    ("Nombre",     200,      1),
    ("Categoría",  140,      0),
    ("Precio",     110,      0),
    ("Stock",       90,      0),
    ("Acciones",   210,      0),
]


def _cfg_cols(frame):
    for i, (_, ms, w) in enumerate(COLS):
        frame.grid_columnconfigure(i, minsize=ms, weight=w)


# ─────────────────────────────────────────────────────────────────────────────
# Vista principal de Inventario
# ─────────────────────────────────────────────────────────────────────────────

class InventoryView(ctk.CTkFrame):

    PRIMARY = "#007bff"
    SUCCESS = "#28a745"
    DANGER  = "#dc3545"
    WARNING = "#e69500"
    CARD    = "#ffffff"
    BG      = "#f8f9fa"
    BORDER  = "#dee2e6"
    ROW_PAD = 16

    def __init__(self, master, db_manager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.db          = db_manager
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter())

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_toolbar()
        self._build_table()
        self.load()

    # ── UI ───────────────────────────────────────────────────────────────────

    def _build_header(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")
        ctk.CTkLabel(f, text="Inventario de Productos",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color="#007bff").pack(anchor="w")
        ctk.CTkLabel(f, text="Gestiona el catálogo y stock de tu tienda",
                     font=ctk.CTkFont(size=13),
                     text_color="#333333").pack(anchor="w")

    def _build_toolbar(self):
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        tb.grid_columnconfigure(0, weight=1)

        ctk.CTkEntry(tb, textvariable=self._search_var,
                     placeholder_text="Buscar por nombre o categoría...",
                     height=42, font=ctk.CTkFont(size=13), width=340,
                     text_color="#111111",
                     fg_color="#ffffff",
                     border_color="#dee2e6",
                     border_width=1
                     ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(tb, text="+ Nuevo Producto", height=42,
                      fg_color=self.SUCCESS, hover_color="#1e7e34",
                      text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._open_create
                      ).grid(row=0, column=1, padx=(10, 0))

        ctk.CTkButton(tb, text="Actualizar", height=42, width=120,
                      fg_color="#6c757d", hover_color="#545b62",
                      text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
                      command=self.load
                      ).grid(row=0, column=2, padx=(8, 0))

    def _build_table(self):
        outer = ctk.CTkFrame(self, fg_color=self.CARD,
                             border_width=1, border_color=self.BORDER,
                             corner_radius=12)
        outer.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        # Encabezados (fuera del scrollable)
        self._hdr = ctk.CTkFrame(outer, fg_color="#eef0f3", corner_radius=0)
        self._hdr.grid(row=0, column=0, sticky="ew", padx=1, pady=(1, 0))
        _cfg_cols(self._hdr)

        for i, (label, _, _w) in enumerate(COLS):
            ctk.CTkLabel(self._hdr,
                         text=label.upper(),
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color="#333333", anchor="center"
                         ).grid(row=0, column=i, padx=6, pady=13, sticky="ew")

        # Filas (scrollable)
        self._rows = ctk.CTkScrollableFrame(outer, fg_color="transparent")
        self._rows.grid(row=1, column=0, sticky="nsew", padx=1, pady=(0, 1))
        _cfg_cols(self._rows)
        self._rows.bind("<Configure>", self._sync_header_width)

    def _sync_header_width(self, event=None):
        w = self._rows.winfo_width()
        if w > 1:
            self._hdr.configure(width=w)

    # ── Datos ─────────────────────────────────────────────────────────────────

    def load(self):
        self._all = self.db.obtener_productos()
        self._filter()

    def _filter(self):
        q = self._search_var.get().lower().strip()
        data = [p for p in self._all
                if not q or q in (p[1] or "").lower() or q in (p[6] or "").lower()]
        self._render(data)

    def _render(self, productos):
        for w in self._rows.winfo_children():
            w.destroy()

        if not productos:
            ctk.CTkLabel(self._rows, text="No se encontraron productos.",
                         font=ctk.CTkFont(size=14), text_color="#555555"
                         ).grid(row=0, column=0, columnspan=6, pady=50)
            return

        for idx, prod in enumerate(productos):
            self._make_row(idx, prod, self.CARD if idx % 2 == 0 else "#f4f6f8")

    def _make_row(self, idx, prod, bg):
        P = self.ROW_PAD

        ctk.CTkFrame(self._rows, height=1, fg_color=self.BORDER
                     ).grid(row=idx*2, column=0, columnspan=6, sticky="ew")

        row = ctk.CTkFrame(self._rows, fg_color=bg, corner_radius=0)
        row.grid(row=idx*2+1, column=0, columnspan=6, sticky="ew")
        _cfg_cols(row)

        ctk.CTkLabel(row, text=f"#{prod[0]}",
                     font=ctk.CTkFont(size=13), text_color="#555555",
                     anchor="center"
                     ).grid(row=0, column=0, padx=6, pady=P, sticky="ew")

        ctk.CTkLabel(row, text=prod[1],
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="#111111",
                     anchor="center"
                     ).grid(row=0, column=1, padx=6, pady=P, sticky="ew")

        ctk.CTkLabel(row, text=prod[6] or "—",
                     font=ctk.CTkFont(size=13), text_color="#333333",
                     anchor="center"
                     ).grid(row=0, column=2, padx=6, pady=P, sticky="ew")

        ctk.CTkLabel(row, text=f"${prod[4]:,.2f}",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="#111111",
                     anchor="center"
                     ).grid(row=0, column=3, padx=6, pady=P, sticky="ew")

        # Stock badge
        if prod[5] == 0:    badge = (self.DANGER,  "white")
        elif prod[5] < 5:   badge = (self.WARNING, "white")
        else:               badge = (self.SUCCESS, "white")

        bw = ctk.CTkFrame(row, fg_color="transparent")
        bw.grid(row=0, column=4, padx=6, pady=P, sticky="ew")
        bw.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(bw, text=str(prod[5]),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=badge[1], fg_color=badge[0],
                     corner_radius=8, width=48, anchor="center"
                     ).grid(row=0, column=0)

        # Botones de acción
        aw = ctk.CTkFrame(row, fg_color="transparent")
        aw.grid(row=0, column=5, padx=6, pady=P-4, sticky="ew")
        aw.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(aw, text="Editar", height=34,
                      fg_color=self.PRIMARY, hover_color="#0056b3",
                      text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
                      anchor="center",
                      command=lambda p=prod: self._open_edit(p)
                      ).grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(aw, text="Eliminar", height=34,
                      fg_color=self.DANGER, hover_color="#a71d2a",
                      text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
                      anchor="center",
                      command=lambda p=prod: self._delete(p)
                      ).grid(row=0, column=1, sticky="ew")

    # ── Acciones CRUD ─────────────────────────────────────────────────────────

    def _open_create(self):
        ProductFormModal(self, self.db, on_save_callback=self.load)

    def _open_edit(self, producto):
        ProductFormModal(self, self.db, on_save_callback=self.load, producto=producto)

    def _delete(self, producto):
        def confirmar():
            self.db.eliminar_producto(producto[0])
            self.load()
        ConfirmDeleteModal(self, producto[1], on_confirm=confirmar)