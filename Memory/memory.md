# MEMORY.MD — Identidad y punteros

> Este archivo es MÍNIMO a propósito. Es el punto de entrada al wiki, no el wiki entero.
> El detalle vive en páginas separadas (ver `index.md`). Convenciones en `schema.md`.

## Qué es este repo
Asistente ejecutivo personal de {{NOMBRE_USUARIO}}. Mantiene una base de conocimiento (wiki) que mejora sesión a sesión.

## Cómo está organizada la memoria
- **`index.md`** — catálogo de todas las páginas del wiki. **Leelo primero.**
- **`schema.md`** — cómo se nombra y organiza el wiki.
- **`Sessions/`** — log cronológico (1 archivo por día).
- **`entities/` · `concepts/` · `rules/` · `reference/`** — el wiki en sí.

## Datos clave muy estables
> Solo cosas que casi nunca cambian (IDs raíz, constantes, fechas ancla). El resto va en su página.
- {{EJ: ID de la planilla principal, moneda base, fecha de inicio de registros, etc.}}

## Reglas críticas (resumen — detalle en `rules/`)
- Nunca tomar acciones sensibles o irreversibles sin confirmación.
- Single source of truth: no duplicar datos entre páginas.
- Mantener `index.md` y la sesión del día siempre actualizados.

---
_Actualizá los punteros si cambia la estructura. El contenido vive en las páginas, no acá._
