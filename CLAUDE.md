@AGENTS.md

## Claude Code

- `Agent/memory/MEMORY.md` lo carga Claude Code solo: no hace falta leerlo al arrancar. `bash setup.sh`
  enlaza su memoria a `Agent/memory/` para que se versione (lo verifica el chequeo 9 de `kb.py lint`).
- Los hooks están declarados en `.claude/settings.json` y los scripts viven en `Tools/hooks/`.
