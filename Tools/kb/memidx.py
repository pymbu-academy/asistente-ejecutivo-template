#!/usr/bin/env python3
"""Gobernador del índice de la auto-memoria (Agent/memory/MEMORY.md).

EL PROBLEMA QUE RESUELVE
------------------------
Claude Code le pide a cada sesión que, al escribir una memoria, agregue un puntero de una línea
en MEMORY.md. Pero el índice se carga entero al arrancar y se lee hasta ~200 líneas: pasado eso
se corta EN SILENCIO y se pierden las memorias del final. Con decenas de memorias nuevas por
semana, "una línea por memoria" contra un tope fijo termina desbordando. Un aviso no arregla una
tasa de crecimiento: hace falta un mecanismo.

QUÉ HACE
--------
Cuando el índice pasa el umbral, saca punteros — SÓLO los que sobran, con un criterio mecánico:

  * Una memoria `feedback` tiene que **dispararse sola**: su valor es verla ANTES de cometer el
    error, sin saber que hay que buscarla. Esas NUNCA se sacan.
  * Una memoria `reference` o `project` es de **consulta**: se necesita al tocar ese tema, y
    `kb.py find` busca en Agent/memory/. Sacarle el puntero no la pierde.

Sólo saca líneas **enteras** cuyos enlaces sean TODOS de consulta: en una línea mixta, el texto
que va después del «—» puede describir cualquiera de los enlaces, y quitar uno dejaría una
descripción huérfana. Tampoco toca la sección «Cómo trabajar» (las reglas del usuario): esas
mandan siempre, sea cual sea su `type`.

Es idempotente y no toca nada si el archivo está por debajo del umbral.

USO
---
    python3 Tools/kb/memidx.py --check     # sólo informa (exit 1 si está por encima del tope)
    python3 Tools/kb/memidx.py --apply     # compacta si hace falta
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUTOMEM = os.path.join(ROOT, "Agent", "memory")
INDEX = os.path.join(AUTOMEM, "MEMORY.md")

# El índice se lee hasta ~200 líneas. Se compacta bastante antes para que nunca se acerque.
TOPE_DURO = 200
UMBRAL = 170
OBJETIVO = 155

LINK = re.compile(r"\[([^\]]*)\]\(([^)]+\.md)\)")


def tipo_de(fname):
    """`metadata.type` de una memoria: feedback | reference | project | user."""
    p = os.path.join(AUTOMEM, fname)
    if not os.path.exists(p):
        return "ROTO"
    dentro = False
    for ln in open(p, encoding="utf-8", errors="replace"):
        s = ln.strip()
        if s == "---":
            if dentro:
                break
            dentro = True
            continue
        if dentro and re.match(r"^type\s*:", s):
            return s.split(":", 1)[1].strip()
    return "?"


# Las reglas del usuario se disparan siempre, sea cual sea el `type` de la memoria.
SECCION_INTOCABLE = re.compile(r"^##\s.*(cómo trabajar|como trabajar|reglas del usuario)", re.I)


def compactar(lineas, objetivo):
    """Saca líneas 100% de consulta hasta llegar al objetivo. Devuelve (nuevas, sacadas)."""
    # De ABAJO hacia arriba: las secciones de plataforma están al final y son las más
    # prescindibles, así las de método (arriba) se tocan últimas.
    protegida = [False] * len(lineas)
    prot = False
    for i, ln in enumerate(lineas):
        if ln.startswith("## "):
            prot = bool(SECCION_INTOCABLE.match(ln))
        protegida[i] = prot

    out = list(lineas)
    vivas = len(out)
    sacadas = []
    for i in range(len(out) - 1, -1, -1):
        if vivas <= objetivo:
            break
        ln = out[i]
        if protegida[i] or not ln.startswith("- "):
            continue
        links = LINK.findall(ln)
        if not links:
            continue
        tipos = [tipo_de(f) for _, f in links]
        # Sólo si TODOS los enlaces de la línea son de consulta. Una línea mixta se deja
        # entera: el gancho de después del «—» puede ser de cualquiera de los enlaces.
        if not all(t in ("reference", "project") for t in tipos):
            continue
        out[i] = None
        vivas -= 1
        sacadas += [f for _, f in links]
    return [l for l in out if l is not None], sacadas


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="informar sin tocar nada")
    g.add_argument("--apply", action="store_true", help="compactar si supera el umbral")
    a = ap.parse_args()

    if not os.path.exists(INDEX):
        print("memidx: no existe Agent/memory/MEMORY.md", file=sys.stderr)
        return 0                          # no es un error del repo: puede no estar enlazada

    lineas = open(INDEX, encoding="utf-8").read().split("\n")
    n = len(lineas)

    if a.check:
        estado = "OK" if n < UMBRAL else ("SOBRE EL TOPE" if n > TOPE_DURO else "por compactar")
        print(f"MEMORY.md {n} líneas (umbral {UMBRAL}, tope duro {TOPE_DURO}) — {estado}")
        return 1 if n > TOPE_DURO else 0

    if n < UMBRAL:
        return 0                          # silencio: no hay nada que hacer

    nuevas, sacadas = compactar(lineas, OBJETIVO)
    if not sacadas:
        print(f"⚠ memidx: {n} líneas y no quedan punteros de consulta que sacar. "
              f"Hay que fusionar entradas de método a mano.", file=sys.stderr)
        return 1

    open(INDEX, "w", encoding="utf-8").write("\n".join(nuevas))
    print(f"memidx: MEMORY.md {n} → {len(nuevas)} líneas; "
          f"{len(sacadas)} punteros de consulta salieron del índice "
          f"(siguen en disco y se buscan con `kb.py find`)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
