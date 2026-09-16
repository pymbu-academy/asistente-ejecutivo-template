#!/usr/bin/env bash
# Hook de SessionStart: sincroniza el repo con GitHub al iniciar o retomar la sesión.
# Seguro por diseño: sólo hace fast-forward. Nunca fuerza, nunca mergea, nunca toca cambios
# locales sin subir. Si no puede, avisa y sigue (exit 0): no bloquea la sesión.

cd "${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}" || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0
git remote get-url origin >/dev/null 2>&1 || exit 0     # sin remoto todavía: nada que sincronizar

FETCH_ERR=$(git fetch --quiet origin 2>&1)
if [ $? -ne 0 ]; then
  if echo "$FETCH_ERR" | grep -qiE "repository not found|authentication failed|could not read username|permission denied|403"; then
    echo "[git-pull] El fetch falló por AUTENTICACIÓN, no por red: revisá tu login de GitHub (gh auth status). NO estás sincronizado hasta resolverlo."
  else
    echo "[git-pull] No pude hacer fetch (¿sin internet?). Sigo con la versión local."
  fi
  exit 0
fi

LOCAL=$(git rev-parse @ 2>/dev/null || echo "")
REMOTE=$(git rev-parse '@{u}' 2>/dev/null || echo "")
[ -z "$REMOTE" ] && exit 0                                # la rama no sigue a ninguna remota
[ "$LOCAL" = "$REMOTE" ] && exit 0                        # al día: silencio

if git merge-base --is-ancestor "$LOCAL" "$REMOTE" 2>/dev/null; then
  if git pull --ff-only --quiet 2>/dev/null; then
    echo "[git-pull] Repo actualizado desde GitHub."
  else
    echo "[git-pull] Hay cambios en GitHub pero el pull falló (¿archivos sin commitear?). Revisalo antes de seguir."
  fi
else
  echo "[git-pull] Tu copia local y la de GitHub se separaron. NO hice pull automático: resolvelo antes de seguir."
fi
exit 0
