"""
seed_data.py — Simulador de datos para VendeMás POS
Genera productos y ventas de los últimos 2 meses con patrones realistas.

Uso:
    python seed_data.py            # inserta datos (conserva los existentes)
    python seed_data.py --reset    # limpia la BD primero y luego inserta
"""

import sqlite3
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Configuración

# Raíz del proyecto = tres niveles arriba de src/utils/seed_data.py
DB_PATH     = Path(__file__).parent.parent.parent / "database" / "pos.db"
DIAS_ATRAS  = 60          # ventana de simulación (2 meses)
SEED        = 42          # reproducibilidad

random.seed(SEED)

# Catálogo de productos de muestra
# (nombre, descripcion, codigo, precio, stock_inicial, categoria, ventas_diarias_promedio)
# ventas_diarias_promedio controla qué tan rápido se mueve cada producto

PRODUCTOS = [
    # Bebidas — alta rotación
    ("Coca Cola 600ml",       "Refresco de cola",         "750105530001", 18.50,  80, "Bebidas",  3.5),
    ("Pepsi 600ml",           "Refresco de cola",         "750105530002", 17.50,  60, "Bebidas",  2.8),
    ("Agua Purificada 1.5L",  "Agua natural",             "750105530003", 12.00,  90, "Bebidas",  5.0),
    ("Jugo de Naranja 1L",    "Jugo natural de naranja",  "750105530004", 28.00,  35, "Bebidas",  1.5),
    ("Cerveza 355ml",         "Cerveza clara",            "750105530005", 22.00,  40, "Bebidas",  2.0),

    # Botanas — rotación media
    ("Papas Fritas 45g",      "Snack de papa",            "750105530006", 15.00,  50, "Botanas",  2.2),
    ("Chicharrón 30g",        "Botana de cerdo",          "750105530007", 12.00,  45, "Botanas",  1.8),
    ("Galletas Saladas 200g", "Galleta de trigo",         "750105530008", 22.00,  30, "Botanas",  1.0),
    ("Cacahuates 100g",       "Cacahuate japonés",        "750105530009", 18.00,  25, "Botanas",  0.8),
    ("Palomitas 50g",         "Palomitas de microondas",  "750105530010", 14.00,  20, "Botanas",  0.6),

    # Básicos — rotación alta y constante
    ("Leche Entera 1L",       "Lácteo pasteurizado",      "750105530011", 24.50,  60, "Básicos",  4.0),
    ("Huevo 12pz",            "Huevo blanco",             "750105530012", 38.00,  40, "Básicos",  3.2),
    ("Tortillas 1kg",         "Tortilla de maíz",         "750105530013", 20.00,  70, "Básicos",  6.0),
    ("Azúcar 1kg",            "Azúcar estándar",          "750105530014", 28.00,  35, "Básicos",  1.5),
    ("Aceite 1L",             "Aceite vegetal",           "750105530015", 42.00,  20, "Básicos",  0.8),

    # Dulces — rotación media-baja
    ("Chocolate Amargo 90g",  "Barra 70% cacao",          "750105530016", 35.00,  30, "Dulces",   0.9),
    ("Gomitas 100g",          "Dulce de goma",            "750105530017", 18.00,  40, "Dulces",   1.4),
    ("Paleta de Limón",       "Paleta helada",            "750105530018", 10.00,  50, "Dulces",   2.5),
    ("Chicles 10pz",          "Chicle de menta",          "750105530019",  8.00,  35, "Dulces",   1.1),

    # Lácteos — rotación media
    ("Yogurt Natural 500g",   "Yogurt sin azúcar",        "750105530020", 32.00,  25, "Lácteos",  1.2),
    ("Queso Fresco 400g",     "Queso artesanal",          "750105530021", 48.00,  15, "Lácteos",  0.7),
    ("Crema 200g",            "Crema ácida",              "750105530022", 22.00,  20, "Lácteos",  0.9),

    # Sin movimiento — para probar ese estado en predicción
    ("Vitaminas C 500mg",     "Suplemento vitamínico",    "750105530023", 95.00,   8, "Otros",    0.0),
    ("Filtro de Agua",        "Filtro purificador",       "750105530024",180.00,   3, "Otros",    0.0),
]


# Funciones de apoyo

def conectar(db_path: Path) -> sqlite3.Connection:
    """
    Conecta a la BD. Si no existe, la crea con las tablas necesarias
    usando POSDatabase — misma lógica que la app principal.
    """
    # Asegurar que la carpeta database/ existe
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # POSDatabase crea las tablas en su __init__ si no existen
    from src.logic.database_controller import POSDatabase
    POSDatabase(str(db_path))          # crea tablas si hacen falta

    return sqlite3.connect(str(db_path))


def limpiar_datos(conn: sqlite3.Connection):
    """Elimina todos los productos y ventas existentes."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM venta")
    cursor.execute("DELETE FROM producto")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('producto','venta')")
    conn.commit()
    print("  BD limpiada.")


def insertar_productos(conn: sqlite3.Connection) -> dict[str, int]:
    """
    Inserta los productos del catálogo.
    Retorna un dict {codigo_barras: id_producto}.
    """
    cursor = conn.cursor()
    ids    = {}

    for nombre, desc, codigo, precio, stock, cat, _ in PRODUCTOS:
        # Verificar si ya existe
        cursor.execute("SELECT id_producto FROM producto WHERE codigo_barras = ?", (codigo,))
        row = cursor.fetchone()
        if row:
            ids[codigo] = row[0]
            continue

        cursor.execute("""
            INSERT INTO producto (nombre, descripcion, codigo_barras, precio, stock, categoria)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, desc, codigo, precio, stock, cat))
        ids[codigo] = cursor.lastrowid

    conn.commit()
    print(f"  {len(ids)} productos listos.")
    return ids


def simular_ventas(conn: sqlite3.Connection, ids: dict[str, int]):
    """
    Genera ventas diarias para los últimos DIAS_ATRAS días.
    Aplica variación aleatoria y patrones de fin de semana.
    """
    cursor = conn.cursor()
    hoy    = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    total_ventas = 0

    for nombre, _, codigo, precio, _, _, venta_diaria in PRODUCTOS:
        if venta_diaria == 0:
            continue  # productos sin movimiento — se omiten intencionalmente

        id_producto = ids[codigo]

        for dias in range(DIAS_ATRAS, 0, -1):
            fecha = hoy - timedelta(days=dias)

            # Variación por día de la semana: fines de semana +30%
            factor_dia = 1.3 if fecha.weekday() >= 5 else 1.0

            # Variación aleatoria ±40%
            factor_random = random.uniform(0.6, 1.4)

            # Cantidad esperada de ventas ese día
            cantidad_base = venta_diaria * factor_dia * factor_random

            # Convertir a entero — mínimo 0, máximo razonable
            cantidad = max(0, round(cantidad_base))

            if cantidad == 0:
                continue

            # Verificar stock suficiente antes de registrar
            cursor.execute("SELECT stock FROM producto WHERE id_producto = ?", (id_producto,))
            stock_actual = cursor.fetchone()[0]

            if stock_actual < cantidad:
                cantidad = stock_actual

            if cantidad == 0:
                continue

            total = round(precio * cantidad, 2)

            # Hora aleatoria del día para la venta
            hora  = random.randint(8, 20)
            mins  = random.randint(0, 59)
            fecha_str = fecha.replace(hour=hora, minute=mins).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO venta (id_producto, cantidad, precio_unitario, total, fecha)
                VALUES (?, ?, ?, ?, ?)
            """, (id_producto, cantidad, precio, total, fecha_str))

            # Descontar del stock
            cursor.execute("""
                UPDATE producto SET stock = stock - ? WHERE id_producto = ?
            """, (cantidad, id_producto))

            total_ventas += 1

    conn.commit()
    print(f"  {total_ventas} registros de venta generados ({DIAS_ATRAS} días).")


def imprimir_resumen(conn: sqlite3.Connection):
    """Muestra un resumen rápido de los datos insertados."""
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM producto")
    n_prod = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM venta")
    n_ventas = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM venta")
    total_mxn = cursor.fetchone()[0] or 0

    cursor.execute("SELECT MIN(fecha), MAX(fecha) FROM venta")
    fecha_min, fecha_max = cursor.fetchone()

    print()
    print("  ┌─────────────────────────────────────────┐")
    print(f"  │  Productos en catálogo : {n_prod:<15}│")
    print(f"  │  Registros de venta    : {n_ventas:<15}│")
    print(f"  │  Ingresos simulados    : ${total_mxn:>12,.2f}  │")
    print(f"  │  Período               : {fecha_min[:10]} →     │")
    print(f"  │                          {fecha_max[:10]}      │")
    print("  └─────────────────────────────────────────┘")
    print()

    # Productos con stock crítico tras la simulación
    cursor.execute("""
        SELECT nombre, stock FROM producto
        WHERE stock <= 5
        ORDER BY stock ASC
    """)
    criticos = cursor.fetchall()
    if criticos:
        print("  Productos con stock bajo después de la simulación:")
        for nombre, stock in criticos:
            print(f"    · {nombre:<30} stock: {stock}")
        print()


# Entry point 

def main():
    parser = argparse.ArgumentParser(description="Generador de datos de prueba para VendeMás POS")
    parser.add_argument("--reset", action="store_true",
                        help="Elimina todos los datos existentes antes de insertar")
    args = parser.parse_args()

    print()
    print("VendeMás POS — Generador de datos de prueba")
    print(f"BD: {DB_PATH}")
    print()

    try:
        conn = conectar(DB_PATH)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    if args.reset:
        print("→ Limpiando datos existentes...")
        limpiar_datos(conn)

    print("→ Insertando productos...")
    ids = insertar_productos(conn)

    print(f"→ Simulando {DIAS_ATRAS} días de ventas...")
    simular_ventas(conn, ids)

    print("→ Resumen:")
    imprimir_resumen(conn)

    conn.close()
    print("Listo. Abre VendeMás y ve a Predicción para ver los resultados.")
    print()


if __name__ == "__main__":
    main()