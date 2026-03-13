import customtkinter as ctk
from .inventory_view import InventoryView

class VendeMasApp(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager

        # --- Configuración de Ventana ---
        self.title("VendeMás POS v0.1")
        # Maximizar ventana al iniciar (Linux/Windows)
        # - Windows: state('zoomed') funciona bien.
        # - Linux: Tk puede no respetar 'zoomed' en algunos entornos; usamos fallback a geometry completa.
        self.after(0, self._maximize_window)
        
        # --- Layout Principal (Grid de 2 filas x 2 columnas) ---
        # Fila 0: Navbar (Ocupa las 2 columnas)
        # Fila 1: Sidebar (Col 0) y Main Content (Col 1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._init_ui()

    def _maximize_window(self):
        """Maximiza la ventana en Windows y Linux.

        Tkinter tiene distintas formas de maximizar según la plataforma y la
        versión de Tk. En Windows, `state('zoomed')` funciona bien. En Linux
        puede que no, así que también aplicamos un fallback con `geometry`.
        """
        try:
            # Windows (y algunos entornos Linux con soporte)
            self.state('zoomed')
        except Exception:
            pass

        try:
            # Otra forma que funciona en algunos entornos Linux
            self.attributes('-zoomed', True)
        except Exception:
            pass

        # Fallback: forzamos tamaño al máximo de la pantalla (sin quitar bordes)
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"{screen_w}x{screen_h}+0+0")

    def _init_ui(self):
        # 1. BARRA SUPERIOR (Navbar)
        self.navbar = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.navbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        self.btn_nav_ventas = ctk.CTkButton(self.navbar, text="VENTAS", 
                                            command=lambda: self._switch_context("ventas"))
        self.btn_nav_ventas.pack(side="left", padx=20, pady=10)

        self.btn_nav_inv = ctk.CTkButton(self.navbar, text="INVENTARIO", 
                                         command=lambda: self._switch_context("inventario"))
        self.btn_nav_inv.pack(side="left", padx=10, pady=10)

        # 2. BARRA LATERAL (Sidebar)
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Mantiene el ancho fijo

        # 3. CONTENEDOR DE VISTA PRINCIPAL
        self.main_container = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_container.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        
        # Estado inicial
        self._switch_context("ventas")

    def _switch_context(self, context):
        """Cambia el contenido del sidebar y la vista principal según el botón superior"""
        # Limpiar Sidebar
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        
        # Limpiar Vista Principal
        for widget in self.main_container.winfo_children():
            widget.destroy()

        if context == "ventas":
            self._build_sales_context()
        elif context == "inventario":
            self._build_inventory_context()

    def _build_sales_context(self):
        # Botones específicos de Ventas en el Sidebar
        ctk.CTkLabel(self.sidebar, text="Acciones Ventas", font=("Arial", 14, "bold")).pack(pady=20)
        ctk.CTkButton(self.sidebar, text="Nueva Venta").pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="Cerrar Caja").pack(pady=10, padx=10)
        
        # Vista de Ventas (Aquí llamarías a SalesView de otro archivo)
        ctk.CTkLabel(self.main_container, text="Pantalla de Ventas activa", font=("Arial", 20)).pack(expand=True)

    def _build_inventory_context(self):
        # Botones específicos de Inventario en el Sidebar
        ctk.CTkLabel(self.sidebar, text="Acciones Stock", font=("Arial", 14, "bold")).pack(pady=20)
        ctk.CTkButton(self.sidebar, text="Agregar Producto").pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="Editar Producto").pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="Eliminar Producto").pack(pady=10, padx=10)
        ctk.CTkButton(self.sidebar, text="Reporte Faltantes").pack(pady=10, padx=10)

        # Vista de Inventario
        self.inventory_view = InventoryView(self.main_container, self.db)
        self.inventory_view.pack(expand=True, fill="both")