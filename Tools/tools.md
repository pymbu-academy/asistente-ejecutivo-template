# TOOLS.MD — Índice de Herramientas Disponibles

> Registrá acá cada herramienta/integración que configures. Es lo que define qué puede hacer tu asistente.

## ✅ Incluidas en esta plantilla (corré `bash setup.sh`)
| Herramienta | Archivo / nota | Estado |
|-------------|----------------|--------|
| **`find-skills`** | Descubre e instala nuevas skills on-demand. El asistente la ofrece cuando una tarea puede mejorar con una skill (ver `CLAUDE.md`). | Se instala con `setup.sh` |
| Google Workspace CLI (`gws`) + skills `gws-*` (20) | Gmail, Drive, Sheets, Calendar, Docs, Tasks, workflows | [gws.md](gws.md) · requiere tu login de Google |
| Office: `pdf` · `docx` · `xlsx` · `pptx` | Crear/leer/editar PDF, Word, Excel y PowerPoint (archivos locales, sin cuentas) | Se instalan con `setup.sh` |
| Marketing: `copywriting` · `social-content` | Escribir copy persuasivo y crear contenido para redes | Se instalan con `setup.sh` |

> 💡 Gracias a **`find-skills`**, no hace falta preinstalar todo: el asistente puede sumar el resto de capacidades (Slack, Notion, facturación, análisis de datos, diseño, estrategia de contenido, email marketing…) cuando una tarea lo amerita, siempre preguntándote antes.

> Tras correr `setup.sh`, completá el login: `gws auth setup --login` (ver `gws.md`).

## Cómo agregar más
| Herramienta | Archivo / nota | Estado |
|-------------|----------------|--------|
| _(ej. GitHub)_ | — | Pendiente |

---

## Skills (capacidades reutilizables)
Las **skills** le dan a tu asistente habilidades específicas. Se instalan en `.claude/skills/` **dentro de este repo** (no global), así viajan con el proyecto. Esta plantilla ya trae un `skills-lock.json` con un set base (Google Workspace + PDF).

```bash
npx skills experimental_install              # restaura las del skills-lock.json (lo hace setup.sh)
npx skills find <query>                       # buscar más skills
npx skills add owner/repo@skill -a claude-code -y   # instalar una nueva en este repo
npx skills list                              # listar instaladas
```
**Regla:** instalá las skills SIEMPRE en el repo (`-a claude-code`), nunca global. Tras instalar, registrala arriba.

> Catálogo de la comunidad: https://skills.sh

---

## Integraciones por MCP (opcional)
Claude Code puede conectarse a servicios externos vía **MCP** (Model Context Protocol): Notion, bases de datos, navegador, etc. Documentá acá los que actives (qué hacen, con qué cuenta, IDs relevantes).

---

## Herramientas del usuario (sin integración directa)
- _(Apps que usás pero que el asistente no controla todavía. Ej: tu CRM, tu banca, etc.)_

---
_Última actualización: completar a medida que sumes herramientas._
