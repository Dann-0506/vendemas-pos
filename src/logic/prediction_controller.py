from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class ProductoPrediction:
    """Resultado de la predicción para un producto."""
    id_producto:   int
    nombre:        str
    categoria:     str
    stock_actual:  int
    venta_diaria:  float        # promedio de unidades vendidas por día
    dias_restantes: int | None  # None si no hay historial de ventas
    fecha_agotamiento: str      # fecha estimada o "Sin datos"
    estado:        str          # "CRÍTICO" | "RIESGO" | "ESTABLE" | "SIN MOVIMIENTO"


class PredictionController:
    """
    Algoritmo predictivo de agotamiento de inventario.
    Calcula cuántos días le quedan a cada producto
    basándose en el historial real de ventas.
    No importa customtkinter.
    """

    # Umbrales de clasificación (días restantes)
    UMBRAL_CRITICO = 4
    UMBRAL_RIESGO  = 10

    # Ventana de análisis (días hacia atrás desde hoy)
    VENTANA_DIAS   = 30

    def __init__(self, db_manager):
        self.db = db_manager

    # Predicción principal

    def calcular_predicciones(self) -> list[ProductoPrediction]:
        """
        Genera la predicción de agotamiento para todos los productos.
        Usa el historial de ventas de los últimos VENTANA_DIAS días.
        """
        productos = self.db.obtener_productos()
        ventas    = self.db.obtener_ventas()
        hoy       = datetime.now()

        # Agrupar ventas por id_producto dentro de la ventana de análisis
        # Estructura de venta: (id_venta, id_producto, cantidad, precio, total, fecha)
        ventas_por_producto: dict[int, float] = {}
        for venta in ventas:
            try:
                fecha_venta = datetime.strptime(venta[5][:10], "%Y-%m-%d")
            except (ValueError, IndexError):
                continue
            if (hoy - fecha_venta).days <= self.VENTANA_DIAS:
                id_prod = venta[1]
                ventas_por_producto[id_prod] = (
                    ventas_por_producto.get(id_prod, 0) + venta[2]
                )

        predicciones = []
        for prod in productos:
            # prod: (id, nombre, descripcion, codigo_barras, precio, stock, categoria, activo)
            id_prod   = prod[0]
            nombre    = prod[1]
            categoria = prod[6] or "—"
            stock     = prod[5]

            total_vendido = ventas_por_producto.get(id_prod, 0)
            venta_diaria  = round(total_vendido / self.VENTANA_DIAS, 2)

            if venta_diaria <= 0:
                # Sin ventas en la ventana de análisis
                predicciones.append(ProductoPrediction(
                    id_producto        = id_prod,
                    nombre             = nombre,
                    categoria          = categoria,
                    stock_actual       = stock,
                    venta_diaria       = 0.0,
                    dias_restantes     = None,
                    fecha_agotamiento  = "Sin datos",
                    estado             = "SIN MOVIMIENTO"
                ))
                continue

            dias_rest = int(stock / venta_diaria)
            fecha_ago = (hoy + timedelta(days=dias_rest)).strftime("%d %b %Y")
            estado    = self._clasificar(dias_rest)

            predicciones.append(ProductoPrediction(
                id_producto        = id_prod,
                nombre             = nombre,
                categoria          = categoria,
                stock_actual       = stock,
                venta_diaria       = venta_diaria,
                dias_restantes     = dias_rest,
                fecha_agotamiento  = fecha_ago,
                estado             = estado
            ))

        # Ordenar: críticos primero, luego por días restantes ascendente
        return sorted(predicciones, key=lambda p: (
            {"CRÍTICO": 0, "RIESGO": 1, "ESTABLE": 2, "SIN MOVIMIENTO": 3}
            .get(p.estado, 4),
            p.dias_restantes if p.dias_restantes is not None else 9999
        ))

    # Resumen

    def obtener_resumen(self) -> dict:
        """
        Devuelve conteos por estado para las tarjetas de resumen.
        """
        predicciones = self.calcular_predicciones()
        conteos = {"CRÍTICO": 0, "RIESGO": 0, "ESTABLE": 0, "SIN MOVIMIENTO": 0}
        for p in predicciones:
            conteos[p.estado] = conteos.get(p.estado, 0) + 1

        return {
            "en_riesgo":     conteos["CRÍTICO"] + conteos["RIESGO"],
            "criticos":      conteos["CRÍTICO"],
            "estables":      conteos["ESTABLE"],
            "sin_movimiento": conteos["SIN MOVIMIENTO"],
            "dias_analizados": self.VENTANA_DIAS,
        }

    # Helpers privados

    def _clasificar(self, dias_restantes: int) -> str:
        if dias_restantes <= self.UMBRAL_CRITICO:
            return "CRÍTICO"
        if dias_restantes <= self.UMBRAL_RIESGO:
            return "RIESGO"
        return "ESTABLE"