import customtkinter as ctk

# Configurar CTk lo antes posible — reduce el tiempo de carga visible
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

from src.logic.database_controller import POSDatabase
from src.logic.inventory_controller import InventoryController
from src.logic.sales_controller import SalesController
from src.logic.prediction_controller import PredictionController
from src.ui.main_window import VendeMasApp
from pathlib import Path


def bootstrap():
    """Configura el entorno e inicializa los servicios base."""

    base_path = Path(__file__).parent
    db_folder = base_path / "database"
    db_path   = db_folder / "pos.db"

    # 1. Persistencia de la carpeta de datos
    db_folder.mkdir(parents=True, exist_ok=True)

    # 2. Capa de datos
    db = POSDatabase(str(db_path))

    # 3. Datos de prueba (solo si la BD está vacía)
    if not db.obtener_productos():
        print("-> Base de datos vacía. Insertando productos de prueba...")
        db.crear_producto("Coca Cola 600ml",   "Refresco de cola",    "750105530001", 18.50, 50, "Bebidas")
        db.crear_producto("Papas Saladas 45g", "Snack de papa",       "750105530002", 15.00, 12, "Botanas")
        db.crear_producto("Leche Entera 1L",   "Lácteo pasteurizado", "750105530003", 24.50,  4, "Básicos")
        db.crear_producto("Chocolate Amargo",  "Barra 70% cacao",     "750105530004", 35.00, 25, "Dulces")

    # 4. Controllers
    inventory_ctrl  = InventoryController(db)
    sales_ctrl      = SalesController(db)
    prediction_ctrl = PredictionController(db)

    # 5. Ventana principal
    app = VendeMasApp(
        inventory_ctrl  = inventory_ctrl,
        sales_ctrl      = sales_ctrl,
        prediction_ctrl = prediction_ctrl,
    )

    print("-> VendeMás POS iniciado con éxito.")

    try:
        app.mainloop()
    except Exception as e:
        print(f"!!! Error crítico en el ciclo principal: {e}")
    finally:
        db.close()
        print("-> Conexión a la base de datos cerrada.")


if __name__ == "__main__":
    bootstrap()