# TOOLS.MD — Índice de Herramientas Disponibles

> Registrá acá cada herramienta/integración que configures. Es lo que define qué puede hacer tu asistente.

## ✅ Incluidas en esta plantilla (corré `bash setup.sh`)
| Herramienta | Archivo / nota | Estado |
|-------------|----------------|--------|
| **`find-skills`** | Descubre e instala nuevas skills on-demand. El asistente la ofrece cuando una tarea puede mejorar con una skill (ver `CLAUDE.md`). | Se instala con `setup.sh` |
| Google Workspace CLI (`gws`) + skills `gws-*` (20) | Gmail, Drive, Sheets, Calendar, Docs, Tasks, workflows | [gws.md](gws.md) · requiere tu login de Google |
| Office: `pdf` · `docx` · `xlsx` · `pptx` | Crear/leer/editar PDF, Word, Excel y PowerPoint (archivos locales, sin cuentas) | Se instalan con `setup.sh` |
| Marketing: `copywriting` · `social-content` | Escribir copy persuasivo y crear contenido para redes | Se instalan con `setup.sh` |
| Escritura: `humanizer` | Saca las señales típicas de escritura de IA para que tus textos suenen humanos. El asistente lo aplica como paso final cuando escribís algo para publicar (posts, emails, copy), preservando tu voz. | Se instala con `setup.sh` |
| Finanzas: `invoice-generator` · `expense-report` | Facturas profesionales (multi-moneda + impuestos) y control de gastos/recibos | Se instalan con `setup.sh` |

> 💡 Gracias a **`find-skills`**, no hace falta preinstalar todo: el asistente puede sumar el resto de capacidades (Slack, Notion, contabilidad avanzada, análisis de datos, diseño, estrategia de contenido, email marketing…) cuando una tarea lo amerita, siempre preguntándote antes.
>
> ⚠️ Las skills de finanzas generan documentos y análisis (facturas, proformas, reportes de gastos), pero **no se integran con la facturación electrónica oficial** de tu país (DGI, AFIP, SAT, etc.). Para una factura legal usá tu sistema oficial.

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

Claude Code puede conectarse a servicios externos vía **MCP** (Model Context Protocol): Notion, GitHub, bases de datos, navegador, etc. **Todo se maneja local en este repo; los secretos nunca se versionan.**

### Cómo se reparten las capas
| Archivo | Qué tiene | ¿Se versiona? |
|---|---|---|
| **`.env`** | Tus credenciales reales (tokens, API keys, secrets) | ❌ No (gitignored) |
| **`.mcp.json`** | Las conexiones MCP (usan `./with-env.sh`) — **sin tokens** | ❌ No (gitignored) |
| **`Tools/tools.md`** (este archivo) | Qué MCP/herramientas hay y para qué — **sin secretos** | ✅ Sí |
| `.env.example` · `.mcp.json.example` · `with-env.sh` | Plantillas y helper, sin valores | ✅ Sí |

### Cómo conectar un MCP nuevo
1. `cp .env.example .env` (si no lo tenés). Agregá la variable que pide el servicio y pegá tu token. Ej: `GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...`
2. `cp .mcp.json.example .mcp.json` (si no lo tenés) y agregá el server, siempre con `"command": "./with-env.sh"` + los `args` del server. **Nunca un token.**
3. Arrancá con **`claude`** normal. El helper `with-env.sh` carga tu `.env` y el server toma su token solo. **Sin wrapper ni pasos extra.**
4. **Registrá el MCP en la tabla de abajo** (qué hace, con qué cuenta) — sin el token.

> 💡 **El `.env` y `with-env.sh` sirven para TODO, no solo MCP.** Si un script o app tuya necesita una API key (ej. `OPENAI_API_KEY`), la ponés en el `.env` y corrés el comando con `./with-env.sh python mi_script.py` — el script lee la credencial del entorno, sin hardcodearla. *(Excepción: herramientas con su propio login, como `gws` con OAuth, usan su mecanismo.)*

### MCP conectados (completá a medida que sumes)
| MCP | Para qué | Cuenta / nota |
|-----|----------|---------------|
| _(ej. GitHub)_ | gestión de repos, issues, PRs | token en `.env` como `GITHUB_TOKEN` |

---

## Herramientas del usuario (sin integración directa)
- _(Apps que usás pero que el asistente no controla todavía. Ej: tu CRM, tu banca, etc.)_

---
_Última actualización: completar a medida que sumes herramientas._
