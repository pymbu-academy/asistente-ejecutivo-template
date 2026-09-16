#!/usr/bin/env bash
# Mantiene Agent/memory/MEMORY.md por debajo del tope de lectura (~200 líneas).
#
# Por qué existe: cada memoria nueva agrega un puntero al índice, y el índice se lee hasta ~200
# líneas: pasado eso se corta en silencio. Esto lo compacta antes de que moleste, sin que nadie
# tenga que acordarse. Sólo saca punteros de memorias de consulta (`reference`/`project`), que
# se recuperan con `kb.py find`. Las de método (`feedback`) no se tocan nunca.
set -uo pipefail

DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
SALIDA="$(python3 "$DIR/Tools/kb/memidx.py" --apply 2>&1)"
COD=$?

# Silencio cuando no hizo falta. Sólo habla si compactó o si no pudo.
if [ -n "$SALIDA" ]; then
  if [ $COD -ne 0 ]; then echo "🛑 $SALIDA" >&2; else echo "🧹 $SALIDA"; fi
fi
exit 0   # nunca bloquea: es higiene, no una compuerta
