import customtkinter as ctk
from .inventory_view import InventoryView

class VendeMasApp(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager

        # --- Paleta de Colores y Estilos ---
        self.primary_blue = "#1f6aa5"
        self.bg_color = "#121212"
        self.card_color = "#1c1c1c"
        self.border_color = "#2d2d2d"

        # --- Configuración de Ventana ---
        self.title("VendeMás POS - Enterprise")
        self.configure(fg_color=self.bg_color)
        self.after(0, self._maximize_window)
        
        # Grid Principal: Columna 0 (Sidebar fija), Columna 1 (Contenido expandible)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._init_ui()

    def _maximize_window(self):
        # Mantenemos tu lógica de maximizado que es robusta para Linux/Fedora
        try: self.state('zoomed')
        except: pass
        try: self.attributes('-zoomed', True)
        except: pass

    def _init_ui(self):
        # 1. NAVBAR SUPERIOR (Glassmorphism sutil)
        self.navbar = ctk.CTkFrame(self, height=70, corner_radius=0, 
                                   fg_color=self.card_color, border_width=1, border_color=self.border_color)
        self.navbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Logo o Identidad
        self.logo_lbl = ctk.CTkLabel(self.navbar, text="📦 VendeMás POS", 
                                     font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_lbl.pack(side="left", padx=30)

        # Botones de navegación con estilo "Tab"
        self.btn_nav_ventas = self._create_nav_btn("Ventas", "ventas")
        self.btn_nav_inv = self._create_nav_btn("Inventario", "inventario")

        # 2. SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, 
                                    fg_color=self.card_color, border_width=0)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # 3. ÁREA DE CONTENIDO (Como una "Card" de JavaFX)
        self.main_container = ctk.CTkFrame(self, corner_radius=15, 
                                           fg_color="#1a1a1a", border_width=1, border_color=self.border_color)
        self.main_container.grid(row=1, column=1, padx=25, pady=25, sticky="nsew")
        
        self._switch_context("ventas")

    def _create_nav_btn(self, text, ctx):
        """Helper para botones de navegación con mejor feedback visual"""
        return ctk.CTkButton(
            self.navbar, text=text, width=120, height=38,
            fg_color="transparent", border_width=1, border_color="#444",
            hover_color="#2d2d2d", font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self._switch_context(ctx)
        ).pack(side="left", padx=8)

    def _switch_context(self, context):
        # Limpieza eficiente
        for widget in self.sidebar.winfo_children(): widget.destroy()
        for widget in self.main_container.winfo_children(): widget.destroy()

        if context == "ventas":
            self._build_sidebar_header("GESTIÓN VENTAS")
            self._create_sidebar_btn("Nueva Venta", lambda: print("Venta"))
            self._create_sidebar_btn("Cerrar Caja", lambda: print("Cierre"))
            ctk.CTkLabel(self.main_container, text="Módulo de Ventas", font=("Inter", 30, "bold")).pack(expand=True)
            
        elif context == "inventario":
            self._build_sidebar_header("CONTROL STOCK")
            self._create_sidebar_btn("Nuevo Producto", lambda: print("Nuevo"))
            self._create_sidebar_btn("Reporte Stock", lambda: print("Reporte"))
            
            # Vista de Inventario real
            self.inventory_view = InventoryView(self.main_container, self.db)
            self.inventory_view.pack(expand=True, fill="both", padx=15, pady=15)

    def _build_sidebar_header(self, text):
        ctk.CTkLabel(self.sidebar, text=text, font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#666").pack(pady=(30, 15), padx=25, anchor="w")

    def _create_sidebar_btn(self, text, cmd):
        ctk.CTkButton(self.sidebar, text=text, command=cmd, height=40, anchor="w",
                      fg_color="transparent", hover_color="#2d2d2d").pack(fill="x", padx=15, pady=4)