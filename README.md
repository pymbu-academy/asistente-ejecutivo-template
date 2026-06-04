# 🤖 Asistente Ejecutivo Personal

Plantilla para tener tu **propio asistente ejecutivo** que vive en un repositorio, aprende sobre vos y tu trabajo, y mantiene una base de conocimiento que mejora con el tiempo. Funciona con **[Claude Code](https://www.anthropic.com/claude-code)**.

No es un chatbot que olvida todo. Es un asistente con **memoria persistente**: cada sesión deja registro, y el conocimiento se acumula en un wiki versionado en git.

---

## ✨ Qué podés hacer con esto
- Tener un asistente que **conoce tu negocio/profesión** y tu forma de trabajar.
- Que **recuerde** decisiones, datos y contexto entre sesiones (no arranca de cero cada vez).
- Que te ayude con **análisis, documentos, finanzas, contenido, organización y automatización**.
- Que **crezca con vos**: vas sumando herramientas y capacidades sin perder el historial.

## 📋 Antes de empezar (requisitos)

Necesitás tener instalado/creado esto. Todo es gratis:

| Requisito | Para qué | Cómo conseguirlo |
|-----------|----------|------------------|
| **Cuenta de GitHub** | Crear tu copia con "Use this template" | [github.com](https://github.com) (registrarte) |
| **Git** | Clonar tu repo a la computadora | [git-scm.com/downloads](https://git-scm.com/downloads) |
| **Node.js 18+** | Instalar las skills y el CLI de Google (`setup.sh`) | [nodejs.org](https://nodejs.org) (versión LTS) |
| **Claude Code** | El asistente en sí | [anthropic.com/claude-code](https://www.anthropic.com/claude-code) |

**Opcional (recomendado):**
| Requisito | Para qué |
|-----------|----------|
| **Cuenta de Google + `gcloud`** | Que el asistente maneje tu Gmail, Drive, Sheets, Calendar (vía `gws`). Si no lo conectás, el asistente igual funciona con todo lo demás. |

> 💡 Si no sabés si tenés Git o Node, abrí una terminal y probá: `git --version` y `node --version`. Si responden con un número, ya los tenés.

## 🚀 Cómo empezar (5 minutos)

1. **Creá tu copia.** Clic en **"Use this template" → "Create a new repository"** (arriba a la derecha). Vas a tener tu propio repo, limpio y privado.
2. **Cloná tu repo** en tu computadora:
   ```bash
   git clone https://github.com/TU-USUARIO/TU-REPO.git
   cd TU-REPO
   ```
3. **Instalá Claude Code** (si no lo tenés): https://www.anthropic.com/claude-code
4. **Instalá las herramientas base** (Google Workspace + skills):
   ```bash
   bash setup.sh
   ```
   Después, conectá tu Google con `gws auth setup --login` (ver [`Tools/gws.md`](Tools/gws.md)). *Opcional pero recomendado para un asistente ejecutivo.*
5. **Configurá tus secretos** *(solo si vas a conectar servicios por MCP — GitHub, Notion, etc.)*:
   ```bash
   mkdir -p .claude && cp settings.local.example.json .claude/settings.local.json  # tus tokens (NUNCA se suben)
   cp .mcp.json.example .mcp.json                                                  # tus conexiones MCP (usan ${VAR})
   ```
   Pegá tus tokens en `.claude/settings.local.json`. Ver detalle en [`Tools/tools.md`](Tools/tools.md).
6. **Abrí Claude Code** en la carpeta (con `claude`) y escribí:
   > *Hola, es mi primera vez con este asistente.*

   El asistente va a **entrevistarte** y configurar todo solo (tu perfil, su personalidad, tu base de conocimiento). No tenés que editar archivos a mano.

   > Claude Code carga tus secretos solo (de `settings.local.json`) y los pasa a las conexiones MCP. **No hace falta ningún wrapper ni paso extra.**

## 🧠 Cómo está organizado
```
├── CLAUDE.md     ← Las reglas del asistente (incluye el onboarding)
├── Agent/        ← Personalidad (soul.md) y capacidades (agent.md)
├── Tools/        ← Qué herramientas tiene conectadas
├── User/         ← Tu perfil
├── Apps/         ← Apps, scripts y automatizaciones que crees
└── Memory/       ← La base de conocimiento (wiki + log de sesiones)
```
Más detalle en [`CLAUDE.md`](CLAUDE.md) y, sobre el wiki, en [`Memory/schema.md`](Memory/schema.md).

## 🔌 Herramientas opcionales
El asistente es más útil cuanto más conectás. Algunas ideas (ver [`Tools/tools.md`](Tools/tools.md)):
- **Google Workspace** (Gmail, Drive, Sheets, Calendar) vía la CLI `gws` o skills `gws-*`.
- **Skills** de la comunidad (redacción, PDFs, transcripciones, etc.) desde [skills.sh](https://skills.sh).
- **MCPs** para conectar tus apps (Notion, bases de datos, navegador…).

## 💡 Filosofía
La base de conocimiento sigue el modelo de [Karpathy para knowledge bases](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): **el humano cura y dirige, el asistente hace el bookkeeping**. Vos decidís qué importa; el asistente mantiene las páginas, los enlaces y el índice al día.

## ☁️ Backup en la nube
El asistente **respalda su memoria subiéndola a tu repo de git** (con tu autorización). Así, si le pasa algo a tu computadora, no perdés el contexto acumulado: lo recuperás clonando el repo de nuevo. En el onboarding elegís si lo hace automático (con aviso) o pidiéndote confirmación cada vez.

## 🔒 Privacidad y secretos
- Tus datos viven **solo en tu repo, que debe ser privado** (al crearlo con "Use this template", elegí *Private*). El asistente respalda tu información en la nube, así que el repo **tiene que ser privado**.
- **Tus secretos (tokens, API keys) viven solo en `.claude/settings.local.json`**, que nunca se sube al repo (`.claude/` está en `.gitignore`). Las conexiones MCP (`.mcp.json`) los referencian con `${VAR}` — jamás se escribe un token en un archivo versionado.
- Esta plantilla no incluye datos ni secretos de nadie: es solo la estructura.

---
_Plantilla open-source. Usala, modificala y hacela tuya._
