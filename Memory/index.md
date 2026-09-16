---
okf_version: "0.2"
---

# Índice del bundle

Mapa por TEMA de las páginas del wiki (OKF §8). **Generado** por `python3 Tools/kb/kb.py index --write` — no editar a mano.

> Esto dice **qué existe y dónde mirar**, no qué dice cada página. Para el contenido: `python3 Tools/kb/kb.py find "<términos>"`, que además busca el cuerpo, la auto-memoria de `Agent/memory/` y las fichas de `Tools/`.

> Marcas: `✓` confirmado por el usuario · `⚠` vencida (verificar contra la fuente) · `ˢⁿᵃᵖ` foto congelada a una fecha · `ᴼᴮˢ` obsoleta.

## Contenido
*qué se publica, en qué formato y con qué voz* — 1 páginas

- **datos** — [Mi voz — muestra de escritura para humanizer](reference/mi-voz.md)

## Herramientas y automatización
*las herramientas conectadas: cómo están armadas y qué las rompe* — 1 páginas

- **reglas** — [La documentación de un sistema ajeno se lee entera, antes de construir](rules/documentacion-primero.md)

## El asistente
*cómo trabaja el asistente: memoria, contexto, reglas de operación, git* — 3 páginas

- **reglas** — [Onboarding — la primera sesión con el asistente](rules/onboarding.md) · [Proceso de sesión — el arranque, el registro y el cierre](rules/proceso-de-sesion.md)
- **raíz** — [Perfil local de OKF v0.2](schema.md)

## Proyectos

Las 0 fichas de `Projects/` tienen **su propio índice**, que NO se carga al arrancar: [projects/index.md](projects/index.md).

## Fuera del bundle

* [../Tools/tools.md](../Tools/tools.md) — índice de herramientas; el detalle de cada una se busca.
* [../User/user.md](../User/user.md) — perfil del usuario.
* [../Agent/agent.md](../Agent/agent.md) — rol y estilo del asistente.
* [Sessions/](Sessions/) — log crudo por día: se busca con `find --log`, no se lee entero.
