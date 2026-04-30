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
    """

    # Umbrales de clasificación (días restantes)
    UMBRAL_CRITICO = 4
    UMBRAL_RIESGO  = 10

    # Ventana de análisis (días hacia atrás desde hoy)
    VENTANA_DIAS   = 30

    def __init__(self, db_manager):
        self.db = db_manager
        self._cache_predicciones: list[ProductoPrediction] | None = None

    def limpiar_cache(self):
        self._cache_predicciones = None

    # Predicción principal

    def calcular_predicciones(self, use_cache=True) -> list[ProductoPrediction]:
        """
        Genera la predicción de agotamiento usando agregaciones SQL.
        """
        if use_cache and self._cache_predicciones is not None:
            return self._cache_predicciones

        productos = self.db.obtener_productos()
        ventas_totales = self.db.obtener_agregados_ventas(self.VENTANA_DIAS)
        hoy = datetime.now()

        predicciones = []
        for prod in productos:
            id_prod   = prod[0]
            nombre    = prod[1]
            categoria = prod[6] or "—"
            stock     = prod[5]

            total_vendido = ventas_totales.get(id_prod, 0)
            venta_diaria  = round(total_vendido / self.VENTANA_DIAS, 2)

            if venta_diaria <= 0:
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

        self._cache_predicciones = sorted(predicciones, key=lambda p: (
            {"CRÍTICO": 0, "RIESGO": 1, "ESTABLE": 2, "SIN MOVIMIENTO": 3}.get(p.estado, 4),
            p.dias_restantes if p.dias_restantes is not None else 9999
        ))
        return self._cache_predicciones

    # Resumen optimizado
    def obtener_resumen(self) -> dict:
        """Calcula el resumen usando el cache si está disponible."""
        predicciones = self.calcular_predicciones(use_cache=True)
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