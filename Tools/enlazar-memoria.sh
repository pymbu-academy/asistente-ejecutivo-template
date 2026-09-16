#!/usr/bin/env bash
# Enlaza la auto-memoria de Claude Code a Agent/memory/ para que se VERSIONE.
#
# Claude Code guarda lo que el asistente aprende en ~/.claude/projects/<ruta-del-repo>/memory.
# Esa carpeta es de la computadora, no del repo: sin este enlace, lo aprendido no viaja con
# `git push` y se pierde con el disco. Idempotente: se puede correr las veces que haga falta.
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESTINO="$RAIZ/Agent/memory"
CLAVE="$(printf '%s' "$RAIZ" | sed 's/[^A-Za-z0-9]/-/g')"
ENLACE="$HOME/.claude/projects/$CLAVE/memory"

mkdir -p "$DESTINO" "$(dirname "$ENLACE")"

if [ -L "$ENLACE" ]; then
  if [ "$(cd "$ENLACE" && pwd -P)" = "$(cd "$DESTINO" && pwd -P)" ]; then
    echo "✓ La memoria del asistente ya está enlazada al repo."
    exit 0
  fi
  echo "⚠ $ENLACE apunta a otro lado; lo reemplazo por Agent/memory."
  rm "$ENLACE"
elif [ -d "$ENLACE" ]; then
  # Ya había memorias fuera del repo: se traen antes de enlazar, sin pisar las del repo.
  n=$(find "$ENLACE" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')
  if [ "$n" -gt 0 ]; then
    for f in "$ENLACE"/*.md; do
      [ -e "$DESTINO/$(basename "$f")" ] || cp "$f" "$DESTINO/"
    done
    echo "↪ Traje $n memorias que estaban fuera del repo."
  fi
  mv "$ENLACE" "$ENLACE.respaldo-$(date +%Y%m%d%H%M%S)"
fi

ln -s "$DESTINO" "$ENLACE"
echo "✓ Memoria del asistente enlazada: $ENLACE → Agent/memory"
