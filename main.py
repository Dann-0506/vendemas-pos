import customtkinter as ctk
from src.logic.database_manager import POSDatabase
from src.ui.main_window import VendeMasApp
from pathlib import Path
import os

def bootstrap():
    """Configura el entorno e inicializa los servicios base"""
    
    base_path = Path(__file__).parent
    db_folder = base_path / "database"
    db_path = db_folder / "pos.db"

    # 1. Asegurar persistencia de la carpeta de datos
    if not db_folder.exists():
        db_folder.mkdir(parents=True)
    
    # 2. Inicializar Capa de Datos
    db = POSDatabase(str(db_path))
    
    # 3. Datos de Prueba
    if not db.obtener_productos():
        print("-> Base de datos vacía. Insertando productos de prueba...")
        db.crear_producto("Coca Cola 600ml", "Refresco de cola", "750105530001", 18.50, 50, "Bebidas")
        db.crear_producto("Papas Saladas 45g", "Snack de papa", "750105530002", 15.00, 12, "Botanas")
        db.crear_producto("Leche Entera 1L", "Lácteo pasteurizado", "750105530003", 24.50, 4, "Básicos")
        db.crear_producto("Chocolate Amargo", "Barra 70% cacao", "750105530004", 35.00, 25, "Dulces")
    
    # 4. Configuración Global de CustomTkinter
    ctk.set_appearance_mode("System")  
    ctk.set_default_color_theme("blue")
        
    # 5. Inicializar y lanzar Ventana Principal
    app = VendeMasApp(db)
    
    print("-> VendeMás POS iniciado con éxito.")
    
    try:
        app.mainloop()
    except Exception as e:
        print(f"!!! Error crítico en el ciclo principal: {e}")

if __name__ == "__main__":
    bootstrap()