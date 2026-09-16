---
type: Rule
title: "Proceso de sesión — el arranque, el registro y el cierre"
description: "Formato del log de sesión, qué se actualiza después de cada bloque de trabajo, y el checklist de cierre. El CLAUDE.md dice CUÁNDO; esto dice CÓMO."
tags: [asistente, sesion, memoria]
aliases: [proceso de sesion, como escribir la sesion, bloque de sesion, checklist de cierre, destilacion, como cerrar la sesion]
durable: true
status: stable
generated: { by: claude-code, at: 2026-09-16T00:00:00Z }
---

# Proceso de sesión

El [`CLAUDE.md`](../../CLAUDE.md) se carga siempre y dice **cuándo** pasa cada cosa. Este archivo
tiene el **cómo**, y se busca cuando toca hacerlo.

## 1. El archivo del día

`Memory/Sessions/session-YYYY-MM-DD.md`. Si es nuevo, arranca con frontmatter:

```markdown
---
type: Session
title: "Sesión YYYY-MM-DD"
description: "<una línea con lo principal del día>"
tags: [sesion]
status: stable
generated: { by: claude-code, at: YYYY-MM-DDTHH:MM:SSZ }
---
```

⚠️ **La fecha sale del reloj que inyecta el hook**, no de la fecha del prompt: una sesión larga
cruza la medianoche.

## 2. El bloque de trabajo

```markdown
## [YYYY-MM-DD] <tipo>: <titular>
```

Tipos: `ingest` · `feature` · `fix` · `update` · `audit` · `research` · `cleanup`.

- **El titular dice qué cambió, no qué se hizo.** «El total del reporte sumaba dos veces el IVA»
  sirve; «trabajo en el reporte» no.
- **La primera línea del bloque contesta sola**: qué se encontró o qué cambió, y contra qué se
  verificó. `find --log` devuelve las primeras líneas que coinciden; si el bloque abre con
  narrativa, el resultado no dice nada.

## 3. Después de cada bloque — la destilación

Una pregunta: **¿qué página del wiki cambia esto?**

- Ninguna → es log, y ahí queda.
- Alguna → **actualizarla ahora**, no "después".

Al tocar una página:

- Actualizá su `generated.at` al momento real de la edición.
- Toda página nueva arranca con frontmatter completo (ver [`../schema.md`](../schema.md) §4) y con
  al menos un tag de `Tools/kb/temas.json`.
- 🛑 `verified` se pone **sólo** si el usuario confirmó el contenido en el momento.
- 🛑 Lo que dejó de ser cierto se marca `status: deprecated` con `deprecation_reason`: no se borra.
- Si se creó, borró o renombró una página: `python3 Tools/kb/kb.py index --write`.

### Memorias del asistente (`Agent/memory/`)

Claude Code guarda ahí lo que aprende (errores, preferencias, decisiones). `setup.sh` enlaza esa
carpeta al repo para que se versione.

- **`feedback`** (método, reglas, errores que no hay que repetir) → **sí** va con una línea en
  `MEMORY.md`: su valor es aparecer sin que nadie la busque.
- **`reference` / `project`** (datos de una herramienta o un proyecto) → **no** hace falta línea:
  se recuperan con `kb.py find`.
- El hook `memoria-indice.sh` mantiene el índice debajo de las 200 líneas. No hay que avisarle al
  usuario: es higiene automática.

## 4. Qué más se actualiza

| Si pasó esto | Actualizá |
|---|---|
| Configuraste una herramienta o descubriste cómo usarla | `Tools/tools.md` (índice) o su ficha en `Tools/` |
| Cambió el perfil del usuario | `User/user.md` |
| Creaste una carpeta en `Projects/` | su ficha en `Memory/projects/` (`type: Project`) |

## 5. Cierre

```bash
python3 Tools/kb/kb.py index --write
python3 Tools/kb/kb.py lint
git add -A && git commit -m "<resumen claro>" && git push     # según la preferencia del usuario
```

Los avisos del `lint` van al log del día como un bloque `audit:`. Dos guardas verifican que el
trabajo quedó escrito, y las dos avisan sin bloquear: el hook `session-log-guard.sh` (al cerrar y al
compactar) y el chequeo 10 del `lint`.

**Por qué:** un mensaje de commit no es memoria de largo plazo. No aparece en `kb.py find` y nadie lo
lee tres meses después.
