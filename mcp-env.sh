#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Helper interno para las conexiones MCP. NO lo corrés vos a mano:
#  lo usa cada server del .mcp.json para cargar tus credenciales del .env
#  antes de arrancar, así Claude Code funciona con 'claude' normal.
#
#  Uso (desde .mcp.json):
#    "command": "./mcp-env.sh",
#    "args": ["npx", "-y", "@modelcontextprotocol/server-github"]
# ─────────────────────────────────────────────────────────────
set -a                       # exporta todo lo que se defina
[ -f .env ] && . ./.env      # carga tus secretos del .env (si existe)
set +a
exec "$@"                     # arranca el server MCP real
