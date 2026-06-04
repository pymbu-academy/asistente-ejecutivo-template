#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Arranca el Asistente Ejecutivo cargando tus secretos del .env
#  Uso:  ./iniciar.sh
#
#  Claude Code NO lee el .env por sí solo. Este wrapper exporta las
#  variables del .env al entorno y después abre Claude Code, para que
#  las conexiones MCP (.mcp.json, que usa ${VAR}) encuentren sus tokens.
# ─────────────────────────────────────────────────────────────
set -a                       # exporta automáticamente todo lo que se defina
[ -f .env ] && source .env   # carga tus secretos (si existe el .env)
set +a

if ! command -v claude >/dev/null 2>&1; then
  echo "⚠ No se encontró 'claude'. Instalá Claude Code: https://www.anthropic.com/claude-code"
  exit 1
fi

exec claude "$@"
