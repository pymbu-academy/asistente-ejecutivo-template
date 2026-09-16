---
type: Rule
title: "Onboarding — la primera sesión con el asistente"
description: "Qué hace el asistente la primera vez que se abre: entrevista al usuario, completa su perfil y su forma de trabajar, adapta los temas del wiki y deja el primer registro."
tags: [asistente, sesion]
aliases: [onboarding, primera vez, primera sesion, configurar el asistente, es mi primera vez]
durable: true
status: stable
generated: { by: claude-code, at: 2026-09-16T00:00:00Z }
---

# Onboarding — la primera sesión

Se usa **sólo** cuando `User/user.md` todavía tiene marcadores `{{...}}`. Antes de cualquier otra
cosa, el asistente se configura entrevistando al usuario.

## 1. Presentarse

Dos líneas: es un asistente ejecutivo personal que vive en este repo, aprende sobre el usuario y su
trabajo, y mantiene una base de conocimiento que mejora con el tiempo.

## 2. Entrevistar — de a una o dos preguntas, nunca un formulario

- **Quién es:** nombre, rol, a qué se dedica.
- **Su trabajo o empresa:** qué hace, productos o servicios, clientes, equipo.
- **Qué quiere lograr con el asistente:** los casos de uso concretos (finanzas, contenido,
  organización, análisis, automatización…) y las tareas que repite.
- **Herramientas que usa:** Google Workspace, Notion, Excel, CRM, redes.
- **Cómo quiere que lo traten:** idioma, tono, nivel de detalle, y **qué acciones requieren su
  confirmación** (enviar mails, gastar, publicar).

## 3. Completar los archivos mientras responde

| Archivo | Qué va |
|---|---|
| `User/user.md` | el perfil completo, sin marcadores |
| `Agent/agent.md` | tono, forma de decidir y límites, según lo que pidió |
| `Tools/kb/temas.json` | **los temas de SU negocio** — son las secciones del índice del wiki |
| `Memory/entities/<su-empresa>.md` | la primera página del wiki, con frontmatter (ver `Memory/schema.md` §4) |
| `Memory/reference/mi-voz.md` | 2-3 fragmentos escritos por él (un post, un mail). Si no quiere darlos ahora, se ofrece más adelante |

## 4. Verificar la instalación

- **`bash setup.sh`** — si no se corrió: instala las skills y enlaza la memoria del asistente al repo.
  `python3 Tools/kb/kb.py lint` lo confirma en el chequeo 9.
- **La hora:** el hook toma la zona de la computadora. Confirmar con el usuario que la hora que se
  inyecta es la suya.
- **Google Workspace es opcional.** Antes de mandarlo al login, `command -v gws`:
  - Está → `gws auth setup --login` (ver `Tools/gws.md`).
  - No está → ofrecer `npm install -g @googleworkspace/cli` y, si no aparece en el PATH, agregar
    `$(npm prefix -g)/bin`. Recién ahí el login.
  - No usa Google → perfecto, el asistente funciona igual. No insistir.

## 5. Backup en la nube

Explicar que la memoria se respalda subiendo el repo a GitHub, y preguntar: *«¿Querés que suba los
cambios solo, avisándote, o que te pida confirmación cada vez?»*. Guardar la respuesta en
`User/user.md`. 🔒 **El repo remoto tiene que ser privado.**

## 6. Cerrar

1. Crear `Memory/Sessions/session-YYYY-MM-DD.md` con el resumen del onboarding (formato en
   [proceso-de-sesion.md](proceso-de-sesion.md)).
2. `python3 Tools/kb/kb.py index --write` y `python3 Tools/kb/kb.py lint`.
3. Con autorización, el primer commit y push.
