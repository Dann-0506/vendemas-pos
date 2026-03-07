# Guía de Contribución - VendeMás

Para mantener la integridad del proyecto y asegurar una colaboración efectiva entre Linux
y Windows, todos los miembros del equipo deben seguir estas reglas:

## Flujo de Trabajo (Git)
1. **No hacer commits a `main`:** Todo desarrollo nuevo debe hacerse en una rama descriptiva
(ej. `feature/interfaz-login`).
2. **Pull Requests:** Antes de integrar una rama a `main`, se debe solicitar una revisión para
asegurar que el código no afecte la arquitectura general.
3. **Mensajes de Commit:** Usar mensajes claros en español
(ej. "Añadida conexión inicial a Base de Datos").

## Compatibilidad Multiplataforma
- **Saltos de línea:** Configurar Git para manejar automáticamente los finales de línea 
para evitar errores de lectura.
- **Codificación:** Todo archivo de texto debe estar en **UTF-8**.
- **Rutas de archivos:** Usar siempre rutas relativas y el separador universal de archivos
en el código para asegurar que funcione en cualquier SO.

## Estándares de Código
* **Documentación:** Cada método o función importante debe incluir comentarios explicando su propósito.
* **Nomenclatura:** Usar `camelCase` para variables en Java y `snake_case` para Python.
