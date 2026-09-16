# 🤖 Asistente Ejecutivo Personal

Plantilla para tener tu **propio asistente ejecutivo** que vive en un repositorio, aprende sobre vos y tu trabajo, y mantiene una base de conocimiento que mejora con el tiempo. Funciona con **[Claude Code](https://www.anthropic.com/claude-code)** y con **[Codex](https://developers.openai.com/codex)**: las mismas instrucciones, la misma memoria y los mismos hooks sirven para los dos.

No es una sesión común de un agente que olvida todo al cerrar. Es un asistente con **memoria persistente**: cada sesión deja registro, el conocimiento se acumula en un wiki versionado en git, y **la memoria no se degrada cuando crece**: el asistente busca lo que necesita en vez de cargarlo todo.

---

## ✨ Qué podés hacer con esto
- Tener un asistente que **conoce tu negocio/profesión** y tu forma de trabajar.
- Que **recuerde** decisiones, datos y contexto entre sesiones (no arranca de cero cada vez).
- Que te ayude con **análisis, documentos, finanzas, contenido, organización y automatización**.
- Que **escriba con tu voz, no como un robot**: incluye un editor (`humanizer`) que saca el tono de IA y aprende tu estilo a partir de muestras tuyas.
- Que **crezca con vos**: suma herramientas cuando hacen falta y **crea las suyas** para los procesos que repetís, sin perder el historial.

## 🧰 Qué trae de fábrica (con `setup.sh`)
Apenas corrés el setup, tu asistente ya viene con **31 skills** listas:
- **Google Workspace** (20): Gmail, Drive, Sheets, Calendar, Docs, Tareas y workflows — vía la CLI `gws` (requiere tu login de Google, opcional).
- **Office** (4): crear/leer/editar **PDF, Word, Excel y PowerPoint** (archivos locales, sin cuentas).
- **Marketing y escritura** (3): `copywriting`, `social-content` y **`humanizer`** (que tus textos no suenen a IA y suenen a vos).
- **Diseño UI/UX** (1): **`ui-ux-pro-max`** — estilos, paletas, tipografías y guías de UX/accesibilidad para que lo que construyas (webs, dashboards, apps) se vea profesional en React, Next, Vue, Tailwind, HTML/CSS y más.
- **Finanzas** (2): facturas multi-moneda (`invoice-generator`) y control de gastos (`expense-report`).
- **Se amplía solo (2 formas):**
  - **`find-skills`** — cuando una tarea puede mejorar con una skill que ya existe, **te la ofrece y la instala** (no hace falta preinstalar todo).
  - **`skill-creator`** — cuando un proceso **siempre se hace igual**, el asistente lo **encapsula como una skill propia y reutilizable**, así no lo rehace a mano cada vez.

> Detalle completo y cómo sumar más: [`Tools/tools.md`](Tools/tools.md).

## 🧠 Una memoria que aguanta el crecimiento
Un asistente que "lee todo al arrancar" funciona bien la primera semana y empieza a fallar a los tres meses: el contexto se llena, se compacta y se pierde lo importante. Esta plantilla está armada para que eso no pase:

- **Busca, no carga.** Al arrancar lee sólo lo indispensable (con un tope medido de ~25.000 tokens). Todo lo demás lo encuentra con `Tools/kb/kb.py find` antes de contestar.
- **Sabe qué tan confiable es cada dato.** Cada página dice si la confirmaste vos, si está vencida o si quedó obsoleta — en formato [OKF](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md).
- **Se revisa sola.** `kb.py lint` detecta páginas vencidas, huérfanas, links rotos y trabajo que quedó sin registrar.
- **Lo que aprende se versiona.** Los errores que no tiene que repetir y tus preferencias quedan en `Agent/memory/`, dentro del repo.
- **Hooks que trabajan solos:** sincroniza con GitHub al arrancar, sabe la hora real (no la deduce), te avisa si el trabajo del día no quedó escrito y mantiene su índice de memorias bajo el límite.

## 📋 Antes de empezar (requisitos)

Necesitás tener instalado/creado esto. Todo es gratis:

| Requisito | Para qué | Cómo conseguirlo |
|-----------|----------|------------------|
| **Cuenta de GitHub** | Crear tu copia con "Use this template" | [github.com](https://github.com) (registrarte) |
| **Git** | Clonar tu repo a la computadora | [git-scm.com/downloads](https://git-scm.com/downloads) |
| **Node.js 18+** | Instalar las skills y el CLI de Google (`setup.sh`) | [nodejs.org](https://nodejs.org) (versión LTS) |
| **Python 3** | El buscador de la memoria y el reloj | En Mac: `xcode-select --install` · [python.org](https://www.python.org/downloads/) |
| **Claude Code** o **Codex** | El asistente en sí (uno de los dos, o ambos) | [Claude Code](https://www.anthropic.com/claude-code) · [Codex](https://developers.openai.com/codex) |

**Opcional (recomendado):**
| Requisito | Para qué |
|-----------|----------|
| **Cuenta de Google + `gcloud`** | Que el asistente maneje tu Gmail, Drive, Sheets, Calendar (vía `gws`). Si no lo conectás, el asistente igual funciona con todo lo demás. |

> 💡 Si no sabés si los tenés, abrí una terminal y probá: `git --version`, `node --version` y `python3 --version`. Si responden con un número, ya están.
>
> Claude Code necesita una cuenta de Claude con un plan que lo incluya; Codex, una cuenta de ChatGPT. Usalo **con tu propia cuenta**: es tu asistente personal.

## 🚀 Cómo empezar (5 minutos)

1. **Creá tu copia.** Clic en **"Use this template" → "Create a new repository"** (arriba a la derecha). 🔒 **Elegí _Private_**: ahí van a quedar datos tuyos y de tu negocio.
2. **Cloná tu repo** en tu computadora:
   ```bash
   git clone https://github.com/TU-USUARIO/TU-REPO.git
   cd TU-REPO
   ```
3. **Instalá tu agente** (si no lo tenés): [Claude Code](https://www.anthropic.com/claude-code) o [Codex](https://developers.openai.com/codex)
4. **Instalá las herramientas base** (skills, Google Workspace y el enlace de la memoria):
   ```bash
   bash setup.sh
   ```
   Después, conectá tu Google con `gws auth setup --login` (ver [`Tools/gws.md`](Tools/gws.md)). *Opcional pero recomendado para un asistente ejecutivo.*
5. **Configurá tus secretos** *(solo si vas a conectar servicios por MCP — GitHub, Notion, etc.)*:
   ```bash
   cp .env.example .env            # tus tokens/API keys (NUNCA se sube al repo)
   cp .mcp.json.example .mcp.json  # conexiones MCP para Claude Code (toman los tokens del .env)
   cp .codex/config.toml.example .codex/config.toml   # lo mismo, para Codex
   ```
   Pegá tus credenciales en el `.env`. Ver detalle en [`Tools/mcp.md`](Tools/mcp.md).
6. **Abrí tu agente** en la carpeta (`claude` o `codex`) y escribí:
   > *Hola, es mi primera vez con este asistente.*

   El asistente va a **entrevistarte** y configurar todo solo (tu perfil, su personalidad, tu base de conocimiento). No tenés que editar archivos a mano. También te va a pedir **un par de muestras de tu escritura** (un post, un email) para que después redacte **con tu voz** — quedan en `Memory/reference/mi-voz.md`.

   > Tus conexiones MCP toman las credenciales del `.env` solas (vía el helper `with-env.sh`). **Arrancás con `claude` o `codex` normal, sin wrapper ni paso extra.**

   > **Con Codex, dos pasos la primera vez:** aceptá **confiar en la carpeta** cuando te lo pregunte, y abrí **`/hooks`** para aprobar los hooks del asistente. Sin eso, Codex ignora la configuración del repo y los hooks no corren.

## 🗂️ Cómo está organizado
```
├── AGENTS.md          ← Las reglas del asistente (las lee Codex)
├── CLAUDE.md          ← Importa AGENTS.md (lo lee Claude Code)
├── User/user.md       ← Tu perfil
├── Agent/agent.md     ← Cómo se comporta
├── Agent/memory/      ← Lo que aprende (versionado)
├── Tools/             ← Herramientas, el buscador (kb/kb.py) y los hooks (hooks/)
├── Projects/          ← Apps, scripts, dashboards y material que crees
├── Memory/            ← La base de conocimiento (wiki + log de sesiones)
├── .claude/settings.json  ← declara los hooks para Claude Code
└── .codex/hooks.json      ← declara los mismos hooks para Codex
```
Más detalle en [`AGENTS.md`](AGENTS.md) y, sobre el wiki, en [`Memory/schema.md`](Memory/schema.md).

## 🔌 Herramientas opcionales
El asistente es más útil cuanto más conectás. Algunas ideas (ver [`Tools/tools.md`](Tools/tools.md)):
- **Google Workspace** (Gmail, Drive, Sheets, Calendar) vía la CLI `gws` o skills `gws-*`.
- **Skills** de la comunidad (redacción, PDFs, transcripciones, etc.) desde [skills.sh](https://skills.sh).
- **MCPs** para conectar tus apps (Notion, bases de datos, navegador…).

## 💡 Filosofía
**Vos decidís qué importa; el asistente hace el mantenimiento**: páginas, enlaces, índice y registro. La idea de partida es el [modelo de Karpathy para knowledge bases](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f); lo que se le sumó es lo que hace falta cuando la base crece: buscar en vez de cargar, marcar qué dato confirmaste vos y cuál venció, y chequeos que avisan antes de que la memoria se degrade.

## ☁️ Backup en la nube
El asistente **respalda su memoria subiéndola a tu repo de git** (con tu autorización). Así, si le pasa algo a tu computadora, no perdés el contexto acumulado: lo recuperás clonando el repo de nuevo. En el onboarding elegís si lo hace automático (con aviso) o pidiéndote confirmación cada vez.

## 🔒 Privacidad y secretos
- Tus datos viven **solo en tu repo, que debe ser privado** (al crearlo con "Use this template", elegí *Private*). El asistente respalda tu información en la nube, así que el repo **tiene que ser privado**.
- **Tus credenciales (tokens, API keys, secrets) viven solo en `.env`**, que nunca se sube al repo (está en `.gitignore`). Las conexiones MCP las toman de ahí — jamás se escribe un token en un archivo versionado. **Cada vez que un servicio pida una credencial, la ponés a mano en tu `.env`.**
- Esta plantilla no incluye datos ni secretos de nadie: es solo la estructura.

---
_Plantilla open-source. Usala, modificala y hacela tuya._
