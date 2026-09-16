#!/usr/bin/env bash
# Mantiene las mismas skills para Claude Code y para Codex.
#
# Las dos herramientas leen el mismo formato (SKILL.md) pero de carpetas distintas:
#   Codex        → .agents/skills/
#   Claude Code  → .claude/skills/
# Copia en las dos direcciones las skills que falten. No pisa ninguna que ya exista.
# Uso: bash Tools/sincronizar-skills.sh [--silencioso]
set -uo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || exit 0

copiadas=0
copiar() {
  local desde="$1" hacia="$2"
  [ -d "$desde" ] || return 0
  mkdir -p "$hacia"
  for d in "$desde"/*/; do
    [ -f "${d}SKILL.md" ] || continue
    local nom; nom=$(basename "$d")
    if [ ! -e "$hacia/$nom" ]; then
      cp -R "$d" "$hacia/$nom" && copiadas=$((copiadas + 1))
    fi
  done
}
copiar .agents/skills .claude/skills
copiar .claude/skills .agents/skills

if [ "${1:-}" != "--silencioso" ] || [ "$copiadas" -gt 0 ]; then
  echo "skills: $copiadas skills copiadas entre .agents/skills (Codex) y .claude/skills (Claude Code)."
fi
exit 0
