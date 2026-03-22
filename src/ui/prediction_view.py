import customtkinter as ctk
from ..utils import constants as C

TCOLS = [
    # (label,               weight, minsize)
    ("Producto",              1,    200),
    ("Categoría",             0,    120),
    ("Stock actual",          0,    100),
    ("Venta diaria prom.",    0,    130),
    ("Días restantes",        0,    120),
    ("Fecha estimada",        0,    140),
    ("Estado",                0,    110),
]


class PredictionView(ctk.CTkFrame):

    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._ctrl = controller             # PredictionController

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_summary_cards()
        self._build_table()

        # Diferir carga hasta que la ventana esté renderizada
        self.after(0, self.load)

    # ── Encabezado ────────────────────────────────────────────────────────────

    def _build_header(self):
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")
        ctk.CTkLabel(f, text="Predicción de Inventario",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=C.PRIMARY).pack(anchor="w")
        ctk.CTkLabel(f, text="Estimación de agotamiento basada en el historial de ventas",
                     font=ctk.CTkFont(size=13),
                     text_color=C.TEXT_SECONDARY).pack(anchor="w")

    # ── Tarjetas de resumen ───────────────────────────────────────────────────

    def _build_summary_cards(self):
        self._cards_row = ctk.CTkFrame(self, fg_color="transparent")
        self._cards_row.grid(row=1, column=0, padx=20, pady=16, sticky="ew")

    def _refresh_summary(self, resumen):
        for w in self._cards_row.winfo_children():
            w.destroy()

        cards = [
            ("En riesgo",       str(resumen["en_riesgo"]),        C.DANGER,    "Agotamiento próximo"),
            ("Estables",        str(resumen["estables"]),          C.SUCCESS,   "Stock suficiente"),
            ("Sin movimiento",  str(resumen["sin_movimiento"]),    C.SECONDARY, "Sin ventas recientes"),
            ("Días analizados", str(resumen["dias_analizados"]),   C.PRIMARY,   "Ventana de historial"),
        ]

        for i, (label, value, color, sub) in enumerate(cards):
            self._cards_row.grid_columnconfigure(i, weight=1)
            self._make_card(self._cards_row, label, value, color, sub, i)

    def _make_card(self, parent, label, value, color, sub, col):
        card = ctk.CTkFrame(parent, fg_color=C.CARD, corner_radius=C.CORNER_RADIUS_LG,
                            border_width=C.BORDER_WIDTH, border_color=C.BORDER)
        card.grid(row=0, column=col,
                  padx=(0 if col == 0 else 8, 8 if col < 3 else 0), sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(card, fg_color=color, height=5,
                     corner_radius=0).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(card, text=value,
                     font=ctk.CTkFont(size=32, weight="bold"),
                     text_color=color).grid(row=1, column=0, pady=(14, 2))
        ctk.CTkLabel(card, text=label,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=C.TEXT_PRIMARY).grid(row=2, column=0, padx=16)
        ctk.CTkLabel(card, text=sub,
                     font=ctk.CTkFont(size=11),
                     text_color=C.TEXT_HINT).grid(row=3, column=0, padx=16, pady=(2, 14))

    # ── Tabla ─────────────────────────────────────────────────────────────────

    def _build_table(self):
        outer = ctk.CTkFrame(self, fg_color=C.CARD, corner_radius=C.CORNER_RADIUS_LG,
                             border_width=C.BORDER_WIDTH, border_color=C.BORDER)
        outer.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(2, weight=1)

        # Toolbar con filtros
        tb = ctk.CTkFrame(outer, fg_color="transparent")
        tb.grid(row=0, column=0, padx=16, pady=12, sticky="ew")
        tb.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tb, text="Detalle por Producto",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=C.TEXT_PRIMARY).grid(row=0, column=0, sticky="w")

        ff = ctk.CTkFrame(tb, fg_color="transparent")
        ff.grid(row=0, column=1)
        self._filter_btns = {}
        for i, (label, color) in enumerate([
            ("Todos",     C.PRIMARY),
            ("En riesgo", C.DANGER),
            ("Estables",  C.SUCCESS),
        ]):
            btn = ctk.CTkButton(ff, text=label, width=90, height=30,
                                fg_color=color if i == 0 else "transparent",
                                border_width=2, border_color=color,
                                text_color="white" if i == 0 else color,
                                hover_color=color,
                                font=ctk.CTkFont(size=11, weight="bold"),
                                corner_radius=C.CORNER_RADIUS_SM,
                                command=lambda lbl=label: self._apply_filter(lbl))
            btn.pack(side="left", padx=4)
            self._filter_btns[label] = btn

        # Encabezados
        hdr = ctk.CTkFrame(outer, fg_color=C.HDR_BG, corner_radius=0)
        hdr.grid(row=1, column=0, sticky="ew", padx=1)
        for i, (lbl, w, ms) in enumerate(TCOLS):
            hdr.grid_columnconfigure(i, weight=w, minsize=ms)
            ctk.CTkLabel(hdr, text=lbl.upper(),
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=C.TEXT_SECONDARY, anchor="center"
                         ).grid(row=0, column=i, padx=6, pady=12, sticky="ew")

        # Filas scrollable
        self._rows = ctk.CTkScrollableFrame(outer, fg_color="transparent")
        self._rows.grid(row=2, column=0, sticky="nsew", padx=1, pady=(0, 1))
        for i, (_, w, ms) in enumerate(TCOLS):
            self._rows.grid_columnconfigure(i, weight=w, minsize=ms)

    # ── Carga y filtrado — llama al controller ────────────────────────────────

    def load(self):
        self._predicciones = self._ctrl.calcular_predicciones()
        self._refresh_summary(self._ctrl.obtener_resumen())
        self._active_filter = "Todos"
        self._render(self._predicciones)

    def _apply_filter(self, filtro):
        self._active_filter = filtro

        color_map = {"Todos": C.PRIMARY, "En riesgo": C.DANGER, "Estables": C.SUCCESS}
        for label, btn in self._filter_btns.items():
            color  = color_map[label]
            active = label == filtro
            btn.configure(
                fg_color=color if active else "transparent",
                text_color="white" if active else color
            )

        if filtro == "Todos":
            data = self._predicciones
        elif filtro == "En riesgo":
            data = [p for p in self._predicciones if p.estado in ("CRÍTICO", "RIESGO")]
        else:
            data = [p for p in self._predicciones if p.estado == "ESTABLE"]

        self._render(data)

    def _render(self, predicciones):
        for w in self._rows.winfo_children():
            w.destroy()

        if not predicciones:
            ctk.CTkLabel(self._rows, text="No hay productos en esta categoría.",
                         font=ctk.CTkFont(size=14), text_color=C.TEXT_MUTED
                         ).grid(row=0, column=0, columnspan=7, pady=50)
            return

        for idx, pred in enumerate(predicciones):
            self._make_row(idx, pred, C.CARD if idx % 2 == 0 else "#f4f6f8")

    def _make_row(self, idx, pred, bg):
        if pred.estado == "CRÍTICO":
            estado_fg, estado_txt = C.DANGER,    "white"
        elif pred.estado == "RIESGO":
            estado_fg, estado_txt = C.WARNING,   "white"
        elif pred.estado == "ESTABLE":
            estado_fg, estado_txt = C.SUCCESS,   "white"
        else:
            estado_fg, estado_txt = C.SECONDARY, "white"

        P = C.ROW_PAD  # mismo padding que inventory_view

        ctk.CTkFrame(self._rows, height=1, fg_color=C.BORDER
                     ).grid(row=idx*2, column=0, columnspan=7, sticky="ew")

        row = ctk.CTkFrame(self._rows, fg_color=bg, corner_radius=0)
        row.grid(row=idx*2+1, column=0, columnspan=7, sticky="ew")
        for i, (_, w, ms) in enumerate(TCOLS):
            row.grid_columnconfigure(i, weight=w, minsize=ms)

        # Nombre con barra de color lateral — height fijo para no expandir la fila
        nf = ctk.CTkFrame(row, fg_color="transparent")
        nf.grid(row=0, column=0, padx=6, pady=P, sticky="ew")
        nf.grid_columnconfigure(1, weight=1)
        ctk.CTkFrame(nf, fg_color=estado_fg, width=4, height=20,
                     corner_radius=2).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkLabel(nf, text=pred.nombre,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C.TEXT_PRIMARY, anchor="w"
                     ).grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(row, text=pred.categoria,
                     font=ctk.CTkFont(size=12), text_color=C.TEXT_MUTED, anchor="center"
                     ).grid(row=0, column=1, padx=6, pady=P, sticky="ew")

        ctk.CTkLabel(row, text=str(pred.stock_actual),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=C.TEXT_PRIMARY, anchor="center"
                     ).grid(row=0, column=2, padx=6, pady=P, sticky="ew")

        ctk.CTkLabel(row, text=f"{pred.venta_diaria:.1f} / día",
                     font=ctk.CTkFont(size=12), text_color=C.TEXT_MUTED, anchor="center"
                     ).grid(row=0, column=3, padx=6, pady=P, sticky="ew")

        if pred.dias_restantes is None:
            dias_txt, dias_color = "—", "#aaaaaa"
        else:
            dias_txt   = f"{pred.dias_restantes} días"
            dias_color = (C.DANGER  if pred.dias_restantes <= 3 else
                          C.WARNING if pred.dias_restantes <= 10 else C.TEXT_PRIMARY)

        ctk.CTkLabel(row, text=dias_txt,
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=dias_color, anchor="center"
                     ).grid(row=0, column=4, padx=6, pady=P, sticky="ew")

        ctk.CTkLabel(row, text=pred.fecha_agotamiento,
                     font=ctk.CTkFont(size=12), text_color=C.TEXT_MUTED, anchor="center"
                     ).grid(row=0, column=5, padx=6, pady=P, sticky="ew")

        bw = ctk.CTkFrame(row, fg_color="transparent")
        bw.grid(row=0, column=6, padx=6, pady=P, sticky="ew")
        bw.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(bw, text=pred.estado,
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=estado_txt, fg_color=estado_fg,
                     corner_radius=C.CORNER_RADIUS_SM, anchor="center"
                     ).grid(row=0, column=0, ipadx=8, ipady=3)