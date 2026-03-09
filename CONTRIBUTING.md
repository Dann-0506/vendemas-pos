# Guía de Contribución - VendeMás POS

Esta guía establece los lineamientos técnicos y éticos para todos los colaboradores del proyecto.

## Configuración Inicial del Entorno
Antes de realizar cualquier cambio, verifica tu instalación:

1. **Verificar Python:** 
Ejecuta `python --version` (Windows) o `python3 --version` (Linux). Debe ser 3.11 o superior.
2. **Crear Entorno Virtual:** 
   - Windows: `python -m venv venv`
   - Linux: `python3 -m venv venv`
3. **Activar Entorno:**
   - Windows: `.\venv\Scripts\activate`
   - Linux: `source venv/bin/activate`
4. **Instalar Dependencias:** `pip install -r requirements.txt`

## 2. Flujo de Trabajo en Git
**Ramas (Branches):** Queda estrictamente prohibido realizar commits directos a la rama `main`[cite: 1523]. Se debe crear una rama por funcionalidad (ej. `feature/modulo-ventas`).
* **Pull Requests:** Todo cambio debe ser revisado por al menos un compañero antes de integrarse a `main`.
* [cite_start]**Codificación de Archivos:** Todos los archivos deben guardarse con codificación **UTF-8** para evitar errores de lectura entre sistemas.

## 3. Estándares de Código y Calidad
* **Nomenclatura:** - Python: `snake_case` para funciones y variables.
    - Clases: `PascalCase`.