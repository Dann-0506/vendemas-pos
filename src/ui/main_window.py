import customtkinter as ctk
from .inventory_view import InventoryView

class SalesView(ctk.CTkFrame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, fg_color="transparent")
        self.db = db_manager
        self._build_ui()

    def _build_ui(self):
        # Placeholder para vista de ventas
        label = ctk.CTkLabel(self, text="Módulo de Ventas\n\nAquí se mostrarán las ventas activas,\nproductos disponibles, etc.", 
                             font=ctk.CTkFont(size=24, weight="bold"), justify="center")
        label.pack(expand=True)

class VendeMasApp(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager

        # --- Paleta de Colores Mejorada para POS ---
        self.primary_blue = "#007bff"  # Azul moderno
        self.success_green = "#28a745"  # Verde para acciones positivas
        self.warning_orange = "#ffc107"  # Naranja para advertencias
        self.danger_red = "#dc3545"  # Rojo para acciones críticas
        self.bg_color = "#f8f9fa"  # Fondo claro para mejor legibilidad
        self.card_color = "#ffffff"  # Blanco para cards
        self.sidebar_bg = "#343a40"  # Gris oscuro para sidebar
        self.border_color = "#dee2e6"

        # Estado de navegación
        self.current_context = "ventas"
        self.nav_buttons = {}

        # --- Configuración de Ventana ---
        self.title("VendeMás POS v0.1.1")
        self.configure(fg_color=self.bg_color)
        self.after(0, self._maximize_window)
        
        # Grid Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._init_ui()
        self.update()  # Forzar actualización de la UI para mostrar widgets iniciales

    def _maximize_window(self):
        # Mantenemos tu lógica de maximizado que es robusta para Linux/Fedora
        try: self.state('zoomed')
        except: pass
        try: self.attributes('-zoomed', True)
        except: pass

    def _init_ui(self):
        # 1. NAVBAR SUPERIOR
        self.navbar = ctk.CTkFrame(self, height=80, corner_radius=0, 
                                   fg_color=self.card_color, border_width=1, border_color=self.border_color)
        self.navbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Logo
        self.logo_lbl = ctk.CTkLabel(self.navbar, text="🛒 VendeMás POS", 
                                     font=ctk.CTkFont(size=24, weight="bold"), text_color=self.primary_blue)
        self.logo_lbl.pack(side="left", padx=30, pady=20)

        # Botones de navegación
        self._create_nav_buttons()

        # 2. SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, 
                                    fg_color=self.sidebar_bg)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # 3. ÁREA DE CONTENIDO
        self.main_container = ctk.CTkFrame(self, corner_radius=20, 
                                           fg_color=self.card_color, border_width=2, border_color=self.border_color)
        self.main_container.grid(row=1, column=1, padx=30, pady=30, sticky="nsew")
        
        self._switch_context("ventas")

    def _create_nav_buttons(self):
        nav_items = [
            ("Ventas", "ventas"),
            ("Inventario", "inventario")
        ]
        for text, ctx in nav_items:
            btn = ctk.CTkButton(
                self.navbar, text=text, width=140, height=40,
                fg_color=self.primary_blue if ctx == self.current_context else "transparent",
                border_width=2, border_color=self.primary_blue,
                hover_color=self.primary_blue, font=ctk.CTkFont(size=16, weight="bold"),
                command=lambda c=ctx: self._switch_context(c)
            )
            btn.pack(side="left", padx=10, pady=20)
            self.nav_buttons[ctx] = btn

    def _switch_context(self, context):
        if context == self.current_context:
            return  # Ya está activo

        # Actualizar estado de botones
        self.nav_buttons[self.current_context].configure(fg_color="transparent")
        self.nav_buttons[context].configure(fg_color=self.primary_blue)
        self.current_context = context

        # Limpieza
        for widget in self.sidebar.winfo_children(): widget.destroy()
        for widget in self.main_container.winfo_children(): widget.destroy()

        if context == "ventas":
            self._build_sidebar("GESTIÓN DE VENTAS", [
                ("Nueva Venta", self.success_green, lambda: print("Nueva Venta")),
                ("Procesar Pago", self.primary_blue, lambda: print("Pago")),
                ("Reportes de Ventas", self.warning_orange, lambda: print("Reportes")),
                ("Cerrar Caja", self.danger_red, lambda: print("Cerrar Caja"))
            ])
            self.sales_view = SalesView(self.main_container, self.db)
            self.sales_view.pack(expand=True, fill="both", padx=20, pady=20)
            
        elif context == "inventario":
            self._build_sidebar("CONTROL DE INVENTARIO", [
                ("Nuevo Producto", self.success_green, lambda: print("Nuevo Producto")),
                ("Buscar Producto", self.primary_blue, lambda: print("Buscar")),
                ("Reporte de Stock", self.warning_orange, lambda: print("Reporte")),
                ("Configuración", "#6c757d", lambda: print("Config"))
            ])
            self.inventory_view = InventoryView(self.main_container, self.db)
            self.inventory_view.pack(expand=True, fill="both", padx=20, pady=20)

        self.update()  # Forzar actualización después de cambiar contexto

    def _build_sidebar(self, header_text, buttons):
        # Header
        header = ctk.CTkLabel(self.sidebar, text=header_text, 
                              font=ctk.CTkFont(size=14, weight="bold"), 
                              text_color="white")
        header.pack(pady=(40, 20), padx=25, anchor="w")

        # Botones
        for text, color, cmd in buttons:
            btn = ctk.CTkButton(self.sidebar, text=text, command=cmd, height=45, 
                                fg_color=color, text_color="white", hover_color=self._darken_color(color),
                                font=ctk.CTkFont(size=12, weight="bold"))
            btn.pack(fill="x", padx=15, pady=5)

    def _darken_color(self, color):
        # Función simple para oscurecer color (placeholder)
        return color  # En producción