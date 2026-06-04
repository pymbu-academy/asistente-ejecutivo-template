#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Ejecuta un comando con TODAS tus credenciales del .env cargadas.
#
#  Sirve para cualquier cosa que necesite secretos del .env:
#   - Conexiones MCP (cada server del .mcp.json lo usa como "command").
#   - Scripts o apps que corras y necesiten una API key, token, etc.
#       Ej:  ./with-env.sh python mi_script.py
#            ./with-env.sh node app.js
#
#  Carga el .env, expande ${VAR} en los argumentos, y ejecuta el comando.
#  Así Claude Code funciona con 'claude' normal, sin wrapper de arranque.
# ─────────────────────────────────────────────────────────────
set -a
[ -f .env ] && . ./.env      # carga TODAS tus credenciales del .env
set +a

# Expande ${VAR} dentro de un string usando las vars ya cargadas (bash puro).
expand() {
  local s="$1" out="" before var
  while [[ "$s" == *'${'*'}'* ]]; do
    before="${s%%\$\{*}"; s="${s#*\$\{}"
    var="${s%%\}*}";      s="${s#*\}}"
    out+="$before${!var}"
  done
  printf '%s' "$out$s"
}

args=(); for a in "$@"; do args+=("$(expand "$a")"); done
exec "${args[@]}"
