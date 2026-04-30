import customtkinter as ctk
from .inventory_view import InventoryView
from .sales_view import SalesView
from .prediction_view import PredictionView
from ..utils import constants as C


class VendeMasApp(ctk.CTk):

    def __init__(self, inventory_ctrl, sales_ctrl, prediction_ctrl):
        super().__init__()

        self._inventory_ctrl  = inventory_ctrl
        self._sales_ctrl      = sales_ctrl
        self._prediction_ctrl = prediction_ctrl

        self.current_context = "ventas"
        self.nav_buttons     = {}

        self.title("VendeMás POS - Gestión de Ventas e Inventario")
        self.configure(fg_color=C.BG)
        self.after(0, self._maximize_window)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._init_ui()
        self.update()

    def _maximize_window(self):
        try: self.state("zoomed")
        except: pass
        try: self.attributes("-zoomed", True)
        except: pass

    def _init_ui(self):
        self.navbar = ctk.CTkFrame(self, height=C.NAV_HEIGHT, corner_radius=0,
                                   fg_color=C.CARD,
                                   border_width=C.BORDER_WIDTH,
                                   border_color=C.BORDER)
        self.navbar.grid(row=0, column=0, sticky="ew")
        self.navbar.grid_propagate(False)

        nav_inner = ctk.CTkFrame(self.navbar, fg_color="transparent")
        nav_inner.place(relx=0, rely=0.5, anchor="w", x=30)

        ctk.CTkLabel(nav_inner, text="VendeMás POS",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=C.PRIMARY
                     ).pack(side="left", padx=(0, 40))

        self._create_nav_buttons(nav_inner)

        self.main_container = ctk.CTkFrame(
            self, corner_radius=C.CORNER_RADIUS_XL,
            fg_color=C.CARD,
            border_width=C.BORDER_WIDTH, border_color=C.BORDER
        )
        self.main_container.grid(row=1, column=0, padx=30, pady=30, sticky="nsew")

        self._switch_context("ventas")

    def _create_nav_buttons(self, parent):
        for text, ctx in [
            ("Ventas",     "ventas"),
            ("Inventario", "inventario"),
            ("Predicción", "prediccion"),
        ]:
            btn = ctk.CTkButton(
                parent, text=text, width=150, height=44,
                fg_color=C.PRIMARY if ctx == self.current_context else "transparent",
                border_width=2, border_color=C.PRIMARY,
                hover_color=C.PRIMARY,
                text_color="white" if ctx == self.current_context else C.PRIMARY,
                font=ctk.CTkFont(size=15, weight="bold"),
                corner_radius=C.CORNER_RADIUS_MD,
                command=lambda c=ctx: self._switch_context(c)
            )
            btn.pack(side="left", padx=6)
            self.nav_buttons[ctx] = btn

    def _switch_context(self, context):
        if context == self.current_context and self.main_container.winfo_children():
            return

        for ctx, btn in self.nav_buttons.items():
            btn.configure(
                fg_color=C.PRIMARY if ctx == context else "transparent",
                text_color="white" if ctx == context else C.PRIMARY
            )

        self.current_context = context

        for widget in self.main_container.winfo_children():
            widget.destroy()

        self.update() # Asegurar que el contenedor esté listo antes de crear la vista

        if context == "ventas":
            v = SalesView(self.main_container, self._sales_ctrl)
            v.pack(expand=True, fill="both", padx=20, pady=20)
            v._refresh_products()

        elif context == "inventario":
            v = InventoryView(self.main_container, self._inventory_ctrl)
            v.pack(expand=True, fill="both", padx=20, pady=20)
            v.load()

        elif context == "prediccion":
            v = PredictionView(self.main_container, self._prediction_ctrl)
            v.pack(expand=True, fill="both", padx=20, pady=20)
            v.load()