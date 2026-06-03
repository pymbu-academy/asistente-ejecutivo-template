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
azul "▶ Instalando skills en .claude/skills/ … (puede tardar 1-2 min)"
if [ -f skills-lock.json ]; then
  # experimental_install restaura desde el lock, pero las deja en .agents/skills/
  npx --yes skills experimental_install || amar "⚠ experimental_install falló; reintentá manualmente."
  # Claude Code busca las skills en .claude/skills/ → moverlas ahí y limpiar .agents/.
  if [ -d .agents/skills ]; then
    mkdir -p .claude/skills
    cp -R .agents/skills/. .claude/skills/
    rm -rf .agents                      # no dejar residuos: solo .claude/ para Claude Code
    n=$(find .claude/skills -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
    verde "✓ ${n} skills disponibles en .claude/skills/"
  else
    amar "⚠ No se encontró .agents/skills tras la instalación. Revisá el paso de skills."
  fi
else
  amar "⚠ No hay skills-lock.json; salto este paso."
fi
echo

# 3. Google Workspace CLI (gws) — OPCIONAL
azul "▶ Instalando Google Workspace CLI (gws) … (opcional)"
GWS_OK=0
if command -v gws >/dev/null 2>&1; then
  GWS_OK=1
  verde "✓ gws ya está instalado ($(gws --version 2>/dev/null | head -1))"
else
  # set -e está activo: envolvemos en 'if' para que un fallo de npm no aborte el script.
  if npm install -g @googleworkspace/cli >/tmp/gws-install.log 2>&1; then
    # Reverificar: instalado ≠ disponible en PATH.
    if command -v gws >/dev/null 2>&1; then
      GWS_OK=1
      verde "✓ gws instalado ($(gws --version 2>/dev/null | head -1))"
    else
      amar "⚠ gws se instaló pero NO está en el PATH."
      amar "  Agregá el bin global de npm a tu PATH. Suele ser:"
      amar "    export PATH=\"\$(npm prefix -g)/bin:\$PATH\""
      amar "  Agregalo a tu ~/.zshrc o ~/.bashrc y reabrí la terminal."
    fi
  else
    amar "⚠ No se pudo instalar gws (probablemente permisos de npm global)."
    amar "  Probá con sudo:   sudo npm install -g @googleworkspace/cli"
    amar "  O configurá un prefix de npm sin sudo: https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally"
    amar "  Detalle del error en: /tmp/gws-install.log"
  fi
fi
echo

# 4. Autenticación (solo si gws quedó disponible)
if [ "$GWS_OK" = "1" ]; then
  azul "▶ Google Workspace: falta tu login (personal, con TU cuenta de Google)"
  cat <<'TXT'
  La autenticación queda guardada de forma segura en tu computadora (no en el repo).
  Corré UNO de estos:

    gws auth setup --login     # 1ª vez: configura proyecto Google Cloud + login (requiere gcloud)
    gws auth login             # solo login OAuth (si ya tenés cliente configurado)

  Verificá con:  gws auth status   ·   Guía: Tools/gws.md
TXT
else
  amar "▶ Google Workspace quedó SIN instalar (es opcional)."
  amar "  El asistente funciona igual: Office (PDF/Word/Excel/PPT), marketing,"
  amar "  finanzas y find-skills no dependen de gws. Solo te perdés, por ahora,"
  amar "  las integraciones con Gmail/Drive/Sheets/Calendar."
  amar "  Cuando quieras, instalá gws (ver arriba) y corré 'gws auth setup --login'."
fi
echo
verde "✓ Setup base completo."
azul  "  Abrí Claude Code en esta carpeta y escribí: \"es mi primera vez\"."
