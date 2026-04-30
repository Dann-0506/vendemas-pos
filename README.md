# VendeMás - Sistema POS con Análisis Predictivo

## Descripción
**VendeMás** es un sistema de Punto de Venta (POS) diseñado para optimizar la gestión comercial de tiendas de abarrotes y minisúper. El sistema integra una interfaz de usuario moderna con un potente módulo de análisis predictivo que estima cuándo se agotará el stock de cada producto basándose en el historial de ventas.

## Características Principales
- **Punto de Venta Eficiente:** Interfaz optimizada para el registro rápido de ventas con soporte para búsqueda por nombre o código de barras.
- **Gestión de Inventario:** Control completo de catálogo, precios y niveles de existencias en tiempo real.
- **Análisis Predictivo:** Algoritmo que calcula el agotamiento de stock, clasificando productos en estados de riesgo (Crítico, Riesgo, Estable) y estimando fechas de resurtido.
- **Arquitectura Robusta:** Diseño modular que garantiza la estabilidad del sistema y la integridad de los datos mediante transacciones atómicas.

## Arquitectura del Sistema
El sistema sigue un diseño modular para separar responsabilidades:
- **UI (src/ui):** Construida con `CustomTkinter`, ofreciendo una experiencia visual moderna y adaptativa.
- **Lógica (src/logic):** Controladores especializados para ventas, inventario y predicciones.
- **Persistencia (src/logic/database_controller.py):** Gestión de base de datos SQLite con optimizaciones mediante índices y manejo de concurrencia.
- **Utilidades (src/utils):** Centralización de constantes estéticas y configuraciones globales.

## Estructura del Proyecto
```text
VendeMas/
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias del proyecto
├── database/               # Almacenamiento de la base de datos SQLite
└── src/
    ├── logic/              # Controladores de negocio y persistencia
    ├── ui/                 # Vistas y componentes de la interfaz
    └── utils/              # Constantes y utilidades globales
```

## Requisitos y Configuración
- **Lenguaje:** Python 3.12.x
- **Entorno Virtual:** Se recomienda el uso de `venv`.
- **Dependencias:** Instalación mediante `pip install -r requirements.txt`.

### Ejecución
Para iniciar el sistema:
```bash
python3 main.py
```

## Ética Académica y Colaboradores
Este proyecto es un prototipo desarrollado por estudiantes del **Tecnológico Nacional de México** para la materia de **Arquitectura de Computadoras**.

- **Daniel Landero Arias**
- **Rafael Solano Alvarado**

*Este proyecto tiene fines exclusivamente académicos y de investigación técnica.*
