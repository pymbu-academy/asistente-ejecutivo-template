---
type: Reference
title: "Perfil local de OKF v0.2"
description: "Cómo se organiza y mantiene esta base de conocimiento: el estándar que sigue, los tipos que usa, el presupuesto de contexto y cómo se busca."
tags: [asistente, okf, memoria]
aliases: [formato, frontmatter, schema, convenciones del wiki]
durable: true   # define convenciones, no datos: no caduca
status: stable
generated: { by: claude-code, at: 2026-09-16T00:00:00Z }
sources:
  - id: okf-spec
    resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
    title: Open Knowledge Format (OKF) v0.2
---

# Perfil local de OKF v0.2

`Memory/` es un **Knowledge Bundle** conforme a
[Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).[^okf-spec]
Este archivo no repite la spec: define las decisiones que OKF deja abiertas.

[^okf-spec]: Open Knowledge Format (OKF) v0.2

## 1. Qué manda

| Tema | Autoridad |
|---|---|
| Formato de los documentos, frontmatter, links, `index.md` | la spec de OKF |
| Qué `type` usamos, qué carpetas, cuándo algo es obsoleto | este archivo |
| Presupuesto de contexto y cómo se busca | este archivo, §5 y §6 |
| Proceso de trabajo (git, secretos, idioma) | [../CLAUDE.md](../CLAUDE.md) |

Ante un conflicto con la spec, **gana la spec** y se corrige este archivo.

## 2. Archivos reservados

- **`index.md`** — el mapa del bundle. **Se genera, no se escribe a mano:**
  `python3 Tools/kb/kb.py index --write`. Hay dos: el de la raíz (se carga al arrancar, agrupado
  por tema) y `projects/index.md` (las fichas de proyecto, fuera del arranque).
- **`Sessions/`** — el log de cada día. Es el histórico: se busca con `kb.py find --log`.

Todo otro `.md` es un documento y **debe** llevar frontmatter con `type`.

## 3. Tipos y carpetas

| Carpeta | `type` | Qué va |
|---|---|---|
| `entities/` | `Entity` | personas, clientes, empresas, áreas del negocio |
| `concepts/` | `Concept` | cómo funciona algo: un cálculo, un sistema, un proceso |
| `rules/` | `Rule` | reglas imperativas ("SIEMPRE", "NUNCA") |
| `reference/` | `Reference` | hechos estables: branding, IDs, listas, tablas de consulta |
| `projects/` | `Project` | ficha de cada carpeta de `Projects/` |
| `Sessions/` | `Session` | log de un día de trabajo |

**Nunca mezclar reglas y datos** en el mismo documento.

## 4. Frontmatter

Obligatorio: `type`. Recomendado siempre: `title`, `description`, `tags`, `aliases`, `status`,
`generated`. Además, según el caso:

- **`verified: { by: human:<usuario>, at: ... }`** — **sólo** cuando el usuario confirmó el
  contenido. Nunca de oficio: es la única señal que separa lo que el asistente dedujo de lo que
  una persona validó. Sin `verified`, el documento es `unverified` y así se lee.
- **`stale_after`** — en todo documento cuyo dato caduca: precios, saldos, estados, conteos,
  credenciales. Instante ISO 8601.
- **`sources`** — cuando el contenido salió de algo consultable (una API, un archivo, una página).
  `last_modified` de la fuente **sólo si se puede medir**: una fecha inventada rompe el chequeo que
  la usa.
- **`resource`** — la URI del activo que la página *describe* (un repo, una planilla, un
  dashboard). Las reglas y los conceptos abstractos no llevan.
- **`snapshot_as_of`** — un registro congelado a una fecha de corte. No caduca: su fecha es parte
  del dato. Excluyente con `stale_after`.
- **`durable: true`** — este contenido define convenciones y no decae. Se usa poco.
- **`status: deprecated`** + `deprecation_reason` — para lo que dejó de ser cierto. **No se borra
  ni se reescribe en prosa**: se marca, conserva sus links y deja de contestar.
- **Footnotes** — el label es la clave de unión contra `sources[].id`. Dos fuentes no comparten
  `id`.

Actores en `generated.by` y `verified.by`: `claude-code` (con versión cuando se sabe),
`human:<usuario>`, `process:<rutina>`.

### Proyectos

Cada carpeta de `Projects/` lleva su ficha en `Memory/projects/` con
`resource: Projects/<nombre>/`, o el buscador no la encuentra. La ficha es un puntero —qué es,
dónde está, qué documentos tiene—, no una copia de su documentación.

## 5. Presupuesto de contexto

> **Lo que se carga al iniciar una sesión no supera ~25.000 tokens.**

Entra solo: `CLAUDE.md`, `User/user.md`, `Agent/agent.md`, `Tools/tools.md`, `Memory/index.md`,
**y dos cosas que el repo no controla**: el índice de la auto-memoria (`Agent/memory/MEMORY.md`) y
las descripciones de las skills instaladas. `python3 Tools/kb/kb.py budget` mide las siete.

Nada más entra solo. Todo lo demás **se busca**.

## 6. Buscar antes de contestar

```bash
python3 Tools/kb/kb.py find "<términos>"     # wiki + auto-memoria + fichas de Tools/
python3 Tools/kb/kb.py find "<t>" --log      # incluye las sesiones
python3 Tools/kb/kb.py show <ruta>           # una página con su estado de confianza
```

`find` pondera `aliases` > título > descripción y tags > cuerpo. **Si una búsqueda razonable no
encuentra una página que existe, la solución es agregarle un `alias`**, no acordarse del nombre del
archivo.

## 7. Destilación: del log al wiki

1. `Sessions/` es el **log**, no la memoria de largo plazo.
2. Por cada bloque de trabajo: **¿qué documento del wiki cambia esto?** Si ninguno, queda en el log.
3. Si un dato vale, se **promueve** a `entities/`, `concepts/`, `rules/` o `reference/`.
4. **Una sola fuente de verdad**: si un dato ya vive en un documento, los demás lo enlazan.
5. **Promoción con retiro**: cuando una memoria pasa a regla, la memoria se queda con el *caso* y la
   regla con el *procedimiento*. Si no, la lección queda escrita dos veces y se desincroniza.

Se mide por bloque, sobre 14 días: el piso es que la mitad de los bloques enlace una página del wiki
o escriba una memoria (chequeo 11 de `lint`).

## 8. Temas del índice

El `index.md` agrupa por **tema**, no por carpeta: una línea por página crece para siempre en la
capa que tiene presupuesto. Los temas y sus tags viven en `Tools/kb/temas.json` y se adaptan al
negocio del usuario. Cada página lleva en `tags` al menos uno de esos tags, o queda en "Sin tema".

## 9. Tamaño de las páginas

Partir una página cuando pasa de **280 líneas** *y* tiene **3 o más secciones sustanciales** sobre
temas distintos. Una colección de ítems parecidos (entradas por fecha, por cliente) no se parte.

## 10. Mantenimiento

```bash
python3 Tools/kb/kb.py index --write   # regenerar los índices
python3 Tools/kb/kb.py lint            # conformancia, vencidas, huérfanas, links rotos, destilación
python3 Tools/kb/kb.py budget          # costo del arranque
```

## 11. Qué NO es parte del bundle

`Agent/memory/` (la auto-memoria) y las fichas de `Tools/` **se buscan con `find`** pero quedan
fuera de la conformancia OKF y del `index.md`: tienen otro frontmatter, o ninguno.
