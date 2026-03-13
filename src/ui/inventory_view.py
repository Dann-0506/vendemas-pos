import customtkinter as ctk

class InventoryView(ctk.CTkFrame):
    def __init__(self, master, db_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.db = db_manager
        
        # Configuración de layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Encabezado
        self.title_label = ctk.CTkLabel(self, text="Inventario de Productos", font=("Roboto", 24, "bold"))
        self.title_label.grid(row=0, column=0, pady=20, padx=20, sticky="w")

        # Tabla de datos (Usamos un ScrollableFrame para cuando haya muchos productos)
        self.table_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.table_container.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.table_container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.cargar_datos()

    def cargar_datos(self):
        # 1. Limpiar tabla previa
        for widget in self.table_container.winfo_children():
            widget.destroy()

        # 2. Encabezados de columna
        headers = ["ID", "Nombre", "Precio", "Stock"]
        for i, header in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_container, text=header, font=("Roboto", 12, "bold"), text_color="gray")
            lbl.grid(row=0, column=i, pady=10, sticky="nsew")

        # 3. Obtener datos de la DB
        productos = self.db.obtener_productos()

        # 4. Desplegar datos
        for row_idx, prod in enumerate(productos, start=1):
            # prod[0]=id, prod[1]=nombre, prod[4]=precio, prod[5]=stock (según tu clase POSDatabase)
            ctk.CTkLabel(self.table_container, text=f"#{prod[0]}").grid(row=row_idx, column=0, pady=5)
            ctk.CTkLabel(self.table_container, text=prod[1]).grid(row=row_idx, column=1, pady=5)
            ctk.CTkLabel(self.table_container, text=f"${prod[4]:.2f}").grid(row=row_idx, column=2, pady=5)
            
            # Color dinámico para el stock (ejemplo de lógica simple)
            stock_color = "red" if prod[5] < 5 else "white"
            ctk.CTkLabel(self.table_container, text=str(prod[5]), text_color=stock_color).grid(row=row_idx, column=3, pady=5)