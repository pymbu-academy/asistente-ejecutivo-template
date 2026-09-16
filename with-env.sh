#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Ejecuta un comando con TODAS tus credenciales del .env cargadas.
#
#  Sirve para cualquier cosa que necesite secretos del .env:
#   - Conexiones MCP (cada server del .mcp.json lo usa como "command").
#   - Scripts o apps que necesiten una API key, token, etc.
#       Ej:  ./with-env.sh python mi_script.py
#            ./with-env.sh node app.js
#
#  Carga el .env de la RAÍZ DEL REPO (no el de la carpeta desde donde lo llames: si lo corrés
#  desde una subcarpeta, un .env relativo no se encontraría y las variables llegarían vacías,
#  que se ve igual que una credencial vencida). Expande ${VAR} en los argumentos y ejecuta.
# ─────────────────────────────────────────────────────────────
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
set -a
[ -f "$RAIZ/.env" ] && . "$RAIZ/.env"
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
