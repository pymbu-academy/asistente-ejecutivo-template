# SCHEMA.MD — Convenciones de la base de conocimiento

Este archivo define **cómo se organiza y mantiene** el wiki de este repositorio.
Es la "constitución" del wiki: si vas a crear, mover o renombrar una página, leé primero acá.

Inspirado en el modelo de Karpathy para knowledge bases: 3 capas (raw sources / wiki / schema), un `index.md` que cataloga todo, un log cronológico (`Sessions/`), y un wiki de **páginas-entidad y páginas-concepto cruzadas con wikilinks**.

---

## 1. Estructura de directorios
```
Memory/
├── memory.md          ← MÍNIMO: identidad del repo + punteros.
├── index.md           ← Catálogo de TODAS las páginas, 1 línea cada una.
├── schema.md          ← Este archivo.
├── Sessions/          ← Log cronológico (1 archivo por día, prefijo parseable).
├── entities/          ← Páginas-entidad (personas, clientes, áreas, unidades).
├── concepts/          ← Páginas-concepto (cómo funciona un cálculo/proceso/sistema).
├── rules/             ← Reglas de operación, separadas de los datos.
└── reference/         ← Datos de referencia (IDs, listas, constantes, branding).
```

**Raw sources (NO se modifican desde el wiki):** tus planillas, documentos, sistemas externos, sitios. El wiki los referencia pero no los reescribe.

## 2. Convenciones de archivos
- **Nombres en kebab-case**, descriptivos. Ej: `mi-empresa.md`, `flujo-de-caja.md`.
- **Encabezado**: cada página arranca con `# <Título>` + opcional una línea de descripción.
- **Pie**: cada página termina con `_Actualizado: YYYY-MM-DD_`.
- **Tamaño objetivo**: <200 líneas por página. Si crece, partir en sub-páginas.

## 3. Cross-references (wikilinks)
Referenciar otras páginas con paths relativos desde la raíz del wiki:
```
Ver detalle en [entities/mi-empresa.md](entities/mi-empresa.md).
La regla está en [rules/operacion.md](rules/operacion.md).
```
**Regla:** toda entidad mencionada en 2+ páginas debe tener su propia página y enlazarse. No repetir datos (single source of truth).

## 4. Qué va en cada carpeta
- **`entities/`** — una página por cosa concreta (persona, cliente, área). Identidad + estado actual + notas + enlaces a sesiones.
- **`concepts/`** — una página por cómo funciona algo (un cálculo, un proceso). Definición + cómo se aplica + dónde se materializa.
- **`rules/`** — reglas **imperativas** ("SIEMPRE X", "NUNCA Y"), separadas de los datos.
- **`reference/`** — hechos estables tipo lookup-table (IDs, listas, constantes).
- **`Sessions/`** — un archivo por día. Cada entrada con **prefijo parseable**:
  ```
  ## [2026-01-15] feature: configuré el reporte semanal
  ```
  Tipos válidos: `ingest`, `feature`, `fix`, `update`, `audit`, `research`, `cleanup`.
  Las sesiones son el LOG, no la memoria de largo plazo: si un dato es valioso, **promovelo** a entity/concept/rule/reference.

## 5. `memory.md` queda MÍNIMO
Solo: identidad del proyecto + punteros a `index.md` y páginas críticas + datos muy estables. NO un dump de todo.

## 6. `index.md` — el catálogo
Lista todas las páginas con 1 línea cada una, agrupadas por carpeta. Se actualiza cada vez que se crea/borra/renombra una página. Es la primera página que se lee al iniciar sesión.

## 7. Workflow de ingestión / actualización
Cuando se aprende algo nuevo:
1. Identificar el tipo (entity / concept / rule / reference / session-log).
2. Si ya hay página, **actualizarla** (no duplicar). Marcar fecha al pie.
3. Si no hay, **crearla** según las convenciones y agregarla al `index.md`.
4. Cruzar referencias con wikilinks en ambas direcciones.
5. Anotar en la sesión del día con el prefijo parseable.

## 8. Lint — chequeos periódicos
Cada tanto, revisar:
- **Orphans**: páginas sin enlaces entrantes.
- **Contradicciones**: misma propiedad con valores distintos en dos páginas.
- **Claims stale**: datos con fecha vieja que pueden estar desactualizados.
- **Sesiones huérfanas**: sessions muy cortas que quedaron a medias.

## 9. Reglas duras
- **NUNCA mezclar reglas y datos** en la misma página. Reglas en `rules/`, datos en `entities/`/`reference/`.
- **Single source of truth**: un dato vive en una página; las demás lo enlazan.
- **El humano cura, el asistente mantiene**: el asistente se ocupa del bookkeeping.
- **Versioná todo**: el wiki es markdown en git.

---
_Adaptá estas convenciones a tu caso, pero mantené la disciplina: es lo que hace que la memoria escale._
