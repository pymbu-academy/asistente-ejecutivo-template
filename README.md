# 🤖 Asistente Ejecutivo Personal

Plantilla para tener tu **propio asistente ejecutivo** que vive en un repositorio, aprende sobre vos y tu trabajo, y mantiene una base de conocimiento que mejora con el tiempo. Funciona con **[Claude Code](https://www.anthropic.com/claude-code)**.

No es un chatbot que olvida todo. Es un asistente con **memoria persistente**: cada sesión deja registro, y el conocimiento se acumula en un wiki versionado en git.

---

## ✨ Qué podés hacer con esto
- Tener un asistente que **conoce tu negocio/profesión** y tu forma de trabajar.
- Que **recuerde** decisiones, datos y contexto entre sesiones (no arranca de cero cada vez).
- Que te ayude con **análisis, documentos, finanzas, contenido, organización y automatización**.
- Que **crezca con vos**: vas sumando herramientas y capacidades sin perder el historial.

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
5. **Abrí Claude Code en la carpeta** y escribí:
   > *Hola, es mi primera vez con este asistente.*

   El asistente va a **entrevistarte** y configurar todo solo (tu perfil, su personalidad, tu base de conocimiento). No tenés que editar archivos a mano.

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

## 🔒 Privacidad
Tus datos viven **solo en tu repo** (hacelo privado). Esta plantilla no incluye datos de nadie: es solo la estructura.

---
_Plantilla open-source. Usala, modificala y hacela tuya._
