#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Setup del Asistente Ejecutivo
#  Instala las herramientas base: skills + Google Workspace CLI (gws).
#  Uso:  bash setup.sh
# ─────────────────────────────────────────────────────────────
set -e

azul()  { printf "\033[1;34m%s\033[0m\n" "$1"; }
verde() { printf "\033[1;32m%s\033[0m\n" "$1"; }
amar()  { printf "\033[1;33m%s\033[0m\n" "$1"; }

azul "▶ Setup del Asistente Ejecutivo"
echo

# 1. Requisitos: Node.js + npm
if ! command -v node >/dev/null 2>&1; then
  amar "⚠ No se encontró Node.js. Instalalo desde https://nodejs.org (v18+) y volvé a correr este script."
  exit 1
fi
verde "✓ Node.js $(node -v)"

# 2. Skills (capacidades reutilizables) desde skills-lock.json
azul "▶ Instalando skills (Google Workspace + PDF) en .claude/skills/ …"
if [ -f skills-lock.json ]; then
  npx --yes skills experimental_install || amar "⚠ Si falló, probá: npx skills experimental_install"
  verde "✓ Skills instaladas"
else
  amar "⚠ No hay skills-lock.json; salto este paso."
fi
echo

# 3. Google Workspace CLI (gws)
azul "▶ Instalando Google Workspace CLI (gws) …"
if command -v gws >/dev/null 2>&1; then
  verde "✓ gws ya está instalado ($(gws --version 2>/dev/null | head -1))"
else
  npm install -g @googleworkspace/cli && verde "✓ gws instalado" \
    || amar "⚠ No se pudo instalar gws global. Probá con sudo: sudo npm install -g @googleworkspace/cli"
fi
echo

# 4. Autenticación (cada usuario, con SU cuenta de Google)
azul "▶ Autenticación de Google Workspace"
cat <<'TXT'
  La autenticación es personal: se hace con TU cuenta de Google y queda
  guardada de forma segura en tu computadora (no se sube al repo).

  Para autenticarte, corré UNO de estos:

    gws auth setup --login     # configura un proyecto de Google Cloud y hace login (recomendado la 1ª vez; requiere gcloud)
    gws auth login             # solo login OAuth (si ya tenés un proyecto/cliente configurado)

  Verificá con:  gws auth status

  Guía completa de gws:  Tools/gws.md
TXT
echo
verde "✓ Setup base completo. Falta solo tu login de Google (paso 4)."
azul  "  Después, abrí Claude Code en esta carpeta y empezá a trabajar."
