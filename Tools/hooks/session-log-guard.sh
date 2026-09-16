#!/usr/bin/env bash
# Guarda del log de sesión. Corre en SessionEnd y en PreCompact.
#
# Por qué existe: los mensajes de commit NO son memoria de largo plazo — no aparecen en
# `kb.py find` y nadie los lee meses después. Un día con muchos commits y ningún bloque en el
# log es trabajo que se pierde para cualquier búsqueda futura. La regla está en AGENTS.md; esto
# la verifica en el momento de cerrar.
#
# No bloquea nunca (exit 0): avisa. Bloquear al cerrar dejaría la sesión trabada.
cd "${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}" || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

HOY=$(date +%Y-%m-%d)
SES="Memory/Sessions/session-${HOY}.md"
COMMITS=$(git log --since="${HOY} 00:00" --format=%s 2>/dev/null | grep -c . || true)
[ "${COMMITS:-0}" -eq 0 ] && exit 0          # día sin commits: nada que registrar

BLOQUES=0
[ -f "$SES" ] && BLOQUES=$(grep -c '^## \[' "$SES" 2>/dev/null || true)
BLOQUES=${BLOQUES:-0}

# Un bloque suele cubrir varios commits. El problema es que no haya casi ninguno.
if [ "$BLOQUES" -eq 0 ] || [ "$COMMITS" -gt $((BLOQUES * 6)) ]; then
  cat >&2 <<MSG

⚠️  EL TRABAJO DE HOY NO QUEDÓ REGISTRADO
    $COMMITS commits y $BLOQUES bloques en $SES

    Los mensajes de commit NO son memoria de largo plazo: no aparecen en
    'kb.py find' y nadie los va a leer dentro de tres meses.

    Antes de cerrar, escribí el bloque:
      ## [$HOY] <tipo>: <titular>
    (tipos: ingest · feature · fix · update · audit · research · cleanup)

    Y por cada bloque, la pregunta de destilación: ¿qué página del wiki cambia esto?
    Verificar con: python3 Tools/kb/kb.py lint

MSG
fi
exit 0
