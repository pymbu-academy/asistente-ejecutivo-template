# TOOLS.MD — Índice de herramientas

> Índice corto: se carga en cada sesión. El detalle de cada herramienta vive en su ficha
> (`Tools/<herramienta>.md`) y se encuentra con `python3 Tools/kb/kb.py find "<herramienta>"`.

## Del asistente

| Herramienta | Para qué | Ficha |
|---|---|---|
| **`Tools/kb/kb.py`** | Buscar en la base de conocimiento (`find`, `show`), regenerar el índice (`index --write`), validar (`lint`) y medir el arranque (`budget`) | [../Memory/schema.md](../Memory/schema.md) |
| **Hooks** (`.claude/hooks/`) | Solos: `git pull` al arrancar · hora real en el contexto · aviso si el trabajo del día no quedó escrito · índice de memorias bajo el tope | [../Memory/rules/proceso-de-sesion.md](../Memory/rules/proceso-de-sesion.md) |
| **`with-env.sh`** | Correr cualquier comando con las credenciales del `.env` | [mcp.md](mcp.md) |

## Incluidas en la plantilla (`bash setup.sh`)

| Herramienta | Para qué | Nota |
|---|---|---|
| **`find-skills`** · **`skill-creator`** | Encontrar e instalar skills existentes · crear skills propias para procesos que se repiten | ver `CLAUDE.md` |
| Google Workspace CLI (`gws`) + skills `gws-*` | Gmail, Drive, Sheets, Calendar, Docs, Tasks | [gws.md](gws.md) · requiere tu login de Google |
| Office: `pdf` · `docx` · `xlsx` · `pptx` | Crear, leer y editar PDF, Word, Excel y PowerPoint | archivos locales, sin cuentas |
| Marketing: `copywriting` · `social-content` | Copy persuasivo y contenido para redes | |
| Escritura: `humanizer` | Saca las señales de escritura de IA y calibra con tu voz | muestra en `Memory/reference/mi-voz.md` |
| Diseño: `ui-ux-pro-max` | Estilos, paletas, tipografías y guías de UX para interfaces | |
| Finanzas: `invoice-generator` · `expense-report` | Facturas y control de gastos | ⚠️ no reemplaza la facturación electrónica oficial de tu país |

## Skills: comandos

```bash
npx skills find <query>                              # buscar
npx skills add owner/repo@skill -a claude-code -y    # instalar EN EL REPO (nunca global)
npx skills list                                      # listar instaladas
```
Catálogo: https://skills.sh

## MCP conectados

Cómo conectar uno nuevo sin exponer tokens: [mcp.md](mcp.md).

| MCP | Para qué | Cuenta / nota |
|---|---|---|
| _(ej. GitHub)_ | repos, issues, PRs | token en `.env` como `GITHUB_PERSONAL_ACCESS_TOKEN` |

## Herramientas del usuario sin integración

- _(Apps que usás pero el asistente no controla todavía: tu CRM, tu banco, etc.)_
