import threading
import customtkinter as ctk
from .product_form_modal import ProductFormModal
from .confirm_delete_modal import ConfirmDeleteModal
from ..utils import constants as C

COLS = [
    # (label,      minsize, weight)
    ("ID",          70,     0),
    ("Nombre",     200,     1),
    ("Categoría",  140,     0),
    ("Precio",     110,     0),
    ("Stock",       90,     0),
    ("Acciones",   210,     0),
]


def _cfg_cols(frame):
    for i, (_, ms, w) in enumerate(COLS):
        frame.grid_columnconfigure(i, minsize=ms, weight=w)


class InventoryView(ctk.CTkFrame):

    ROW_PAD = C.ROW_PAD

    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._ctrl       = controller
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter())

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_toolbar()
        self._build_table()
        # self.after(0, self.load) # Se carga manualmente al mostrar la vista

    def _build_header(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")
        ctk.CTkLabel(f, text="Inventario de Productos",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=C.PRIMARY).pack(anchor="w")
        ctk.CTkLabel(f, text="Gestiona el catálogo y stock de tu tienda",
                     font=ctk.CTkFont(size=13),
                     text_color=C.TEXT_SECONDARY).pack(anchor="w")

    def _build_toolbar(self):
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        tb.grid_columnconfigure(0, weight=1)

        ctk.CTkEntry(tb, textvariable=self._search_var,
                     placeholder_text="Buscar por nombre o categoría...",
                     height=C.TOOLBAR_HEIGHT, font=ctk.CTkFont(size=13), width=340,
                     text_color=C.TEXT_PRIMARY, fg_color=C.CARD,
                     border_color=C.BORDER, border_width=C.BORDER_WIDTH
                     ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(tb, text="+ Nuevo Producto", height=C.TOOLBAR_HEIGHT,
                      fg_color=C.SUCCESS, hover_color=C.SUCCESS_HOVER,
                      text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._open_create
                      ).grid(row=0, column=1, padx=(10, 0))

        ctk.CTkButton(tb, text="Actualizar", height=C.TOOLBAR_HEIGHT, width=120,
                      fg_color=C.SECONDARY, hover_color=C.SECONDARY_HOVER,
                      text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
                      command=self.load
                      ).grid(row=0, column=2, padx=(8, 0))

    def _build_table(self):
        outer = ctk.CTkFrame(self, fg_color=C.CARD,
                             border_width=C.BORDER_WIDTH, border_color=C.BORDER,
                             corner_radius=C.CORNER_RADIUS_LG)
        outer.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        self._hdr = ctk.CTkFrame(outer, fg_color=C.HDR_BG, corner_radius=0)
        self._hdr.grid(row=0, column=0, sticky="ew", padx=1, pady=(1, 0))
        _cfg_cols(self._hdr)

        for i, (label, _, _w) in enumerate(COLS):
            ctk.CTkLabel(self._hdr, text=label.upper(),
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=C.TEXT_SECONDARY, anchor="center"
                         ).grid(row=0, column=i, padx=6, pady=13, sticky="ew")

        self._rows = ctk.CTkScrollableFrame(outer, fg_color="transparent")
        self._rows.grid(row=1, column=0, sticky="nsew", padx=1, pady=(0, 1))
        _cfg_cols(self._rows)
        self._rows.bind("<Configure>", self._sync_header_width)

    def _sync_header_width(self, event=None):
        w = self._rows.winfo_width()
        if w > 1:
            self._hdr.configure(width=w)

    # Datos 

    def load(self):
        """Carga los productos de forma síncrona."""
        try:
            data = self._ctrl.obtener_todos()
            self._render(data)
        except Exception:
            pass

    def _filter(self):
        """Realiza la búsqueda de forma síncrona."""
        query = self._search_var.get()
        try:
            data = self._ctrl.buscar(query)
            self._render(data)
        except Exception:
            pass

    def _render(self, productos):
        if not self.winfo_exists():
            return
        
        for w in self._rows.winfo_children():
            w.destroy()

        if not productos:
            ctk.CTkLabel(self._rows, text="No se encontraron productos.",
                         font=ctk.CTkFont(size=14), text_color=C.TEXT_MUTED
                         ).grid(row=0, column=0, columnspan=6, pady=50)
            return

        # Limitar renderizado a los primeros 100 para mantener fluidez
        display_list = productos[:100]
        
        for idx, prod in enumerate(display_list):
            self._make_row(idx, prod, C.CARD if idx % 2 == 0 else "#f4f6f8")
            
        if len(productos) > 100:
             ctk.CTkLabel(self._rows, text=f"... y {len(productos)-100} productos más (usa el buscador para filtrar)",
                         font=ctk.CTkFont(size=12, slant="italic"), text_color=C.TEXT_HINT
                         ).grid(row=201, column=0, columnspan=6, pady=10)

    def _make_row(self, idx, prod, bg):
        P = self.ROW_PAD

        ctk.CTkFrame(self._rows, height=1, fg_color=C.BORDER
                     ).grid(row=idx*2, column=0, columnspan=6, sticky="ew")

        row = ctk.CTkFrame(self._rows, fg_color=bg, corner_radius=0)
        row.grid(row=idx*2+1, column=0, columnspan=6, sticky="ew")
        _cfg_cols(row)

        ctk.CTkLabel(row, text=f"#{prod[0]}",
                     font=ctk.CTkFont(size=13), text_color=C.TEXT_MUTED,
                     anchor="center"
                     ).grid(row=0, column=0, padx=6, pady=P, sticky="ew")

        ctk.CTkLabel(row, text=prod[1],
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C.TEXT_PRIMARY, anchor="center"
                     ).grid(row=0, column=1, padx=6, pady=P, sticky="ew")

        ctk.CTkLabel(row, text=prod[6] or "—",
                     font=ctk.CTkFont(size=13), text_color=C.TEXT_SECONDARY,
                     anchor="center"
                     ).grid(row=0, column=2, padx=6, pady=P, sticky="ew")

        ctk.CTkLabel(row, text=f"${prod[4]:,.2f}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C.TEXT_PRIMARY, anchor="center"
                     ).grid(row=0, column=3, padx=6, pady=P, sticky="ew")

        if prod[5] == 0:    badge = (C.DANGER,  "white")
        elif prod[5] < C.STOCK_LOW: badge = (C.WARNING, "white")
        else:               badge = (C.SUCCESS, "white")

        bw = ctk.CTkFrame(row, fg_color="transparent")
        bw.grid(row=0, column=4, padx=6, pady=P, sticky="ew")
        bw.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(bw, text=str(prod[5]),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=badge[1], fg_color=badge[0],
                     corner_radius=C.CORNER_RADIUS_MD, width=48, anchor="center"
                     ).grid(row=0, column=0)

        aw = ctk.CTkFrame(row, fg_color="transparent")
        aw.grid(row=0, column=5, padx=6, pady=P-4, sticky="ew")
        aw.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(aw, text="Editar", height=34,
                      fg_color=C.PRIMARY, hover_color=C.PRIMARY_HOVER,
                      text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
                      anchor="center",
                      command=lambda p=prod: self._open_edit(p)
                      ).grid(row=0, column=0, padx=(0, 5), sticky="ew")

        ctk.CTkButton(aw, text="Eliminar", height=34,
                      fg_color=C.DANGER, hover_color=C.DANGER_HOVER,
                      text_color="white", font=ctk.CTkFont(size=12, weight="bold"),
                      anchor="center",
                      command=lambda p=prod: self._delete(p)
                      ).grid(row=0, column=1, sticky="ew")

    # Acciones

    def _open_create(self):
        ProductFormModal(self, self._ctrl, on_save_callback=self.load)

    def _open_edit(self, producto):
        ProductFormModal(self, self._ctrl, on_save_callback=self.load, producto=producto)

    def _delete(self, producto):
        def confirmar():
            self._ctrl.eliminar(producto[0])
            self.after(0, self.load)
        ConfirmDeleteModal(self, producto[1], on_confirm=confirmar)