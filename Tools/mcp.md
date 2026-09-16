# MCP — conectar servicios externos

Claude Code puede conectarse a servicios externos vía **MCP** (Model Context Protocol): Notion, GitHub, bases de datos, navegador, etc. **Todo se maneja local en este repo; los secretos nunca se versionan.**

### Cómo se reparten las capas
| Archivo | Qué tiene | ¿Se versiona? |
|---|---|---|
| **`.env`** | Tus credenciales reales (tokens, API keys, secrets) | ❌ No (gitignored) |
| **`.mcp.json`** | Las conexiones MCP (usan `./with-env.sh`) — **sin tokens** | ❌ No (gitignored) |
| **`Tools/tools.md`** | Qué MCP y herramientas hay, y para qué — **sin secretos** | ✅ Sí |
| `.env.example` · `.mcp.json.example` · `with-env.sh` | Plantillas y helper, sin valores | ✅ Sí |

### Cómo conectar un MCP nuevo
1. `cp .env.example .env` (si no lo tenés). Agregá la variable que pide el servicio y pegá tu token. Ej: `GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...`
2. `cp .mcp.json.example .mcp.json` (si no lo tenés) y agregá el server, siempre con `"command": "./with-env.sh"` + los `args` del server. **Nunca un token.**
3. Arrancá con **`claude`** normal. El helper `with-env.sh` carga tu `.env` y el server toma su token solo. **Sin wrapper ni pasos extra.**
4. **Registrá el MCP en la tabla de `Tools/tools.md`** (qué hace, con qué cuenta) — sin el token.

> 💡 **El `.env` y `with-env.sh` sirven para TODO, no solo MCP.** Si un script o app tuya necesita una API key (ej. `OPENAI_API_KEY`), la ponés en el `.env` y corrés el comando con `./with-env.sh python mi_script.py` — el script lee la credencial del entorno, sin hardcodearla. *(Excepción: herramientas con su propio login, como `gws` con OAuth, usan su mecanismo.)*
