import customtkinter as ctk
from .inventory_view import InventoryView
 
 
class SalesView(ctk.CTkFrame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, fg_color="transparent")
        self.db = db_manager
        self._build_ui()
 
    def _build_ui(self):
        label = ctk.CTkLabel(self, text="Módulo de Ventas\n\nAquí se mostrarán las ventas activas,\nproductos disponibles, etc.",
                             font=ctk.CTkFont(size=24, weight="bold"), justify="center")
        label.pack(expand=True)
 
 
class VendeMasApp(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
 
        # --- Paleta de Colores ---
        self.primary_blue   = "#007bff"
        self.success_green  = "#28a745"
        self.warning_orange = "#ffc107"
        self.danger_red     = "#dc3545"
        self.bg_color       = "#f8f9fa"
        self.card_color     = "#ffffff"
        self.border_color   = "#dee2e6"
 
        # Estado de navegación
        self.current_context = "ventas"
        self.nav_buttons = {}
 
        # --- Configuración de Ventana ---
        self.title("VendeMás POS v0.2.1")
        self.configure(fg_color=self.bg_color)
        self.after(0, self._maximize_window)
 
        # Grid Principal: navbar arriba, contenido abajo
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
 
        self._init_ui()
        self.update()
 
    def _maximize_window(self):
        try: self.state('zoomed')
        except: pass
        try: self.attributes('-zoomed', True)
        except: pass
 
    def _init_ui(self):
        # NAVBAR SUPERIOR
        self.navbar = ctk.CTkFrame(self, height=80, corner_radius=0,
                                   fg_color=self.card_color,
                                   border_width=1, border_color=self.border_color)
        self.navbar.grid(row=0, column=0, sticky="ew")
        self.navbar.grid_propagate(False)
 
        # Contenedor interno centrado verticalmente
        nav_inner = ctk.CTkFrame(self.navbar, fg_color="transparent")
        nav_inner.place(relx=0, rely=0.5, anchor="w", x=30)
 
        # Logo
        self.logo_lbl = ctk.CTkLabel(
            nav_inner, text="🛒  VendeMás POS",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.primary_blue
        )
        self.logo_lbl.pack(side="left", padx=(0, 40))
 
        # Botones de navegación (dentro del mismo contenedor)
        self._create_nav_buttons(nav_inner)
 
        # ÁREA DE CONTENIDO (sin sidebar)
        self.main_container = ctk.CTkFrame(
            self, corner_radius=16,
            fg_color=self.card_color,
            border_width=1, border_color=self.border_color
        )
        self.main_container.grid(row=1, column=0, padx=30, pady=30, sticky="nsew")
 
        self._switch_context("ventas")
 
    def _create_nav_buttons(self, parent):
        nav_items = [
            ("Ventas",      "ventas"),
            ("Inventario",  "inventario"),
        ]
        for text, ctx in nav_items:
            btn = ctk.CTkButton(
                parent, text=text, width=150, height=44,
                fg_color=self.primary_blue if ctx == self.current_context else "transparent",
                border_width=2, border_color=self.primary_blue,
                hover_color=self.primary_blue,
                text_color="white" if ctx == self.current_context else self.primary_blue,
                font=ctk.CTkFont(size=15, weight="bold"),
                corner_radius=8,
                command=lambda c=ctx: self._switch_context(c)
            )
            btn.pack(side="left", padx=6)
            self.nav_buttons[ctx] = btn
 
    def _switch_context(self, context):
        if context == self.current_context and self.main_container.winfo_children():
            return
 
        # Actualizar estado visual de botones
        for ctx, btn in self.nav_buttons.items():
            if ctx == context:
                btn.configure(fg_color=self.primary_blue, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=self.primary_blue)
 
        self.current_context = context
 
        # Limpiar contenido anterior
        for widget in self.main_container.winfo_children():
            widget.destroy()
 
        if context == "ventas":
            self.sales_view = SalesView(self.main_container, self.db)
            self.sales_view.pack(expand=True, fill="both", padx=20, pady=20)
 
        elif context == "inventario":
            self.inventory_view = InventoryView(self.main_container, self.db)
            self.inventory_view.pack(expand=True, fill="both", padx=20, pady=20)
 
        self.update()