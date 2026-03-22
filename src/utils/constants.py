# ─────────────────────────────────────────────────────────────────────────────
# src/utils/constants.py
# Tokens de diseño centralizados — modificar aquí afecta toda la app.
# ─────────────────────────────────────────────────────────────────────────────


# ── Paleta de colores principal ───────────────────────────────────────────────

PRIMARY  = "#007bff"   # Azul — acciones primarias, títulos
SUCCESS  = "#28a745"   # Verde — stock OK, confirmaciones
DANGER   = "#dc3545"   # Rojo — stock crítico, eliminar
WARNING  = "#e69500"   # Naranja — stock bajo, alertas
SECONDARY = "#6c757d"  # Gris — acciones secundarias (ej. botón Actualizar)

# ── Colores de superficie ─────────────────────────────────────────────────────

CARD    = "#ffffff"    # Fondo de tarjetas y paneles
BG      = "#f8f9fa"    # Fondo general de la app
BORDER  = "#dee2e6"    # Bordes de tarjetas, separadores
HDR_BG  = "#eef0f3"    # Fondo de encabezados de tabla

# ── Colores de texto ──────────────────────────────────────────────────────────

TEXT_PRIMARY   = "#111111"  # Texto principal
TEXT_SECONDARY = "#333333"  # Texto secundario
TEXT_MUTED     = "#555555"  # Texto atenuado
TEXT_HINT      = "#888888"  # Placeholders y etiquetas de ayuda

# ── Hover colors (versión oscurecida de cada color principal) ─────────────────

PRIMARY_HOVER   = "#0056b3"
SUCCESS_HOVER   = "#1e7e34"
DANGER_HOVER    = "#a71d2a"
SECONDARY_HOVER = "#545b62"

# ── Colores de acento por categoría (panel de ventas) ────────────────────────

CATEGORY_COLORS = {
    "Bebidas":  "#e3f2fd",
    "Botanas":  "#f3e5f5",
    "Básicos":  "#e8f5e9",
    "Dulces":   "#fff3e0",
    "Lácteos":  "#e0f7fa",
    "Otros":    "#f5f5f5",
}
CATEGORY_DEFAULT_ACCENT = "#f0f0f0"

# ── Umbrales de stock ─────────────────────────────────────────────────────────

STOCK_CRITICAL = 0    # badge rojo
STOCK_LOW      = 5    # badge naranja (stock < STOCK_LOW)

# ── Dimensiones y espaciado ───────────────────────────────────────────────────

CORNER_RADIUS_SM  = 6
CORNER_RADIUS_MD  = 8
CORNER_RADIUS_LG  = 12
CORNER_RADIUS_XL  = 16

BORDER_WIDTH      = 1
NAV_HEIGHT        = 80
ROW_PAD           = 16
TOOLBAR_HEIGHT    = 42
MODAL_WIDTH       = 500
MODAL_HEIGHT      = 640