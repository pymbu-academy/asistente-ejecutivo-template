#!/usr/bin/env python3
"""Reloj — inyecta la fecha y hora REALES del usuario en el contexto del modelo.

Por qué existe: el modelo no tiene reloj. Deduce "hoy" de la fecha del prompt (que puede venir un
día atrasada) o de marcas de tiempo de logs y APIs, que suelen venir en UTC y corren la hora. Una
regla escrita ("mirá la hora antes de decir hoy") sólo se aplica si el modelo se acuerda. Esto no
depende de que se acuerde: el dato llega solo.

Eventos (ver .claude/settings.json para Claude Code y .codex/hooks.json para Codex):
  SessionStart      → al arrancar.
  UserPromptSubmit  → en cada mensaje del usuario.
  PreToolUse        → cada INTERVALO segundos, para trabajos largos sin mensajes de por medio.

Zona: la de la computadora. Para forzar otra, definir ASISTENTE_ZONA con un nombre IANA
(ej. America/Mexico_City) en el entorno.

Nunca bloquea ni falla: un hook de reloj que trabe una sesión sería peor que el problema.
"""
import datetime
import json
import os
import re
import sys
import tempfile
import time

INTERVALO = int(os.environ.get("ASISTENTE_HORA_INTERVALO", "900"))   # 15 min
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def _zona_del_sistema():
    """Nombre IANA de la zona de la compu (ej. America/Mexico_City), no la abreviatura (-06)."""
    try:
        destino = os.path.realpath("/etc/localtime")
        if "zoneinfo/" in destino:
            return destino.split("zoneinfo/", 1)[1]
    except OSError:
        pass
    return os.environ.get("TZ") or ""


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    evento = payload.get("hook_event_name") or ""
    sesion = re.sub(r"[^A-Za-z0-9._-]", "_", payload.get("session_id") or "sin-sesion")
    if not evento:
        return

    estado = os.path.join(tempfile.gettempdir(), "asistente-hora")
    os.makedirs(estado, exist_ok=True)
    stamp = os.path.join(estado, sesion + ".stamp")
    ahora = int(time.time())
    if evento == "PreToolUse" and os.path.exists(stamp):
        try:
            if ahora - int(open(stamp).read().strip() or 0) < INTERVALO:
                return
        except ValueError:
            pass

    zona = os.environ.get("ASISTENTE_ZONA")
    if zona:
        try:
            from zoneinfo import ZoneInfo
            local = datetime.datetime.now(ZoneInfo(zona))
        except Exception:
            local = datetime.datetime.now().astimezone()
    else:
        local = datetime.datetime.now().astimezone()
    utc = datetime.datetime.now(datetime.timezone.utc)

    off = local.utcoffset() or datetime.timedelta(0)
    mins = int(off.total_seconds() // 60)
    signo = "+" if mins >= 0 else "−"
    h, m = divmod(abs(mins), 60)
    utc_txt = f"UTC{signo}{h}" + (f":{m:02d}" if m else "")
    nombre = zona or _zona_del_sistema() or local.tzname() or "hora local"
    dia = DIAS[local.weekday()]
    fecha = local.strftime("%d/%m/%Y %H:%M")
    iso = local.strftime("%Y-%m-%d")

    if evento == "PreToolUse":
        texto = (f"⏰ HORA REAL ({nombre}, {utc_txt}): {dia} {fecha} (hoy es {iso}). "
                 f"En UTC: {utc.strftime('%d/%m %H:%M')}.")
    else:
        texto = (f"⏰ HORA REAL del usuario ({nombre}, {utc_txt}): {dia} {fecha}. Fecha de hoy: "
                 f"{iso}. En UTC: {utc.strftime('%d/%m %H:%M')}.\n"
                 "Toda referencia al momento —«hoy», «ayer», «es tarde», «en dos días», fechar un "
                 "mail, un archivo o el log de sesión, o decidir qué queda para mañana— se mide "
                 "contra ESTA hora. No contra la fecha del prompt ni contra marcas de tiempo de "
                 "logs o APIs, que suelen venir en UTC.")

    try:
        open(stamp, "w").write(str(ahora))
        for f in os.listdir(estado):                   # limpieza de sesiones viejas
            p = os.path.join(estado, f)
            if ahora - os.path.getmtime(p) > 2 * 86400:
                os.remove(p)
    except OSError:
        pass
    print(json.dumps({"hookSpecificOutput": {"hookEventName": evento,
                                             "additionalContext": texto}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
