# TOOLS.MD — Índice de Herramientas Disponibles

> Registrá acá cada herramienta/integración que configures. Es lo que define qué puede hacer tu asistente.

## Herramientas configuradas
| Herramienta | Archivo / nota | Estado |
|-------------|----------------|--------|
| _(ej. Google Workspace CLI `gws`)_ | — | Pendiente |
| _(ej. GitHub)_ | — | Pendiente |

_Agregá filas a medida que sumes herramientas._

---

## Skills (capacidades reutilizables)

Las **skills** son módulos que le dan a tu asistente habilidades específicas (redactar, analizar, generar PDFs, transcribir, etc.). Se instalan en `.claude/skills/` **dentro de este repo** (no global), así viajan con el proyecto.

**Regla:** instalá las skills SIEMPRE en el repo, nunca global.
```bash
npx skills find <query>                            # Buscar skills
npx skills add owner/repo@skill -a claude-code -y   # Instalar en este repo (.claude/skills/)
npx skills list                                    # Listar instaladas
```
Tras instalar una skill, registrala en la tabla de arriba.

> Catálogo de skills de la comunidad: https://skills.sh

---

## Integraciones por MCP (opcional)

Claude Code puede conectarse a servicios externos vía **MCP** (Model Context Protocol): Google Workspace, Notion, bases de datos, navegador, etc. Cada MCP que conectes amplía lo que el asistente puede hacer. Documentá acá los que actives (qué hacen, con qué cuenta, IDs relevantes).

### Google Workspace (recomendado para asistentes ejecutivos)
- CLI `gws` (`@googleworkspace/cli`) o el conjunto de skills `gws-*` para Gmail, Drive, Sheets, Calendar, Docs, Tasks.
- Requiere autenticación OAuth con tu cuenta de Google.

---

## Herramientas del usuario (sin integración directa)
- _(Apps que usás pero que el asistente no controla todavía. Ej: tu CRM, tu banca, etc.)_

---
_Última actualización: completar._
