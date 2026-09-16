#!/usr/bin/env python3
"""kb.py — herramienta de la base de conocimiento (bundle OKF v0.2 en Memory/).

    kb.py find <términos> [--log] [--all] [-n N]   buscar (esto es lo que se usa siempre)
    kb.py show <ruta>                              ver un documento con su estado de confianza
    kb.py index [--write]                          regenerar Memory/index.md (OKF §8)
    kb.py lint                                     conformancia OKF + salud del wiki
    kb.py budget                                   medir el costo de contexto del arranque

Sin dependencias externas: sólo stdlib.
"""
import os
import re
import sys
import json
import argparse
import collections
import unicodedata
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEM = os.path.join(ROOT, "Memory")
# La memoria del asistente (Claude Code la escribe sola; en Codex se escribe por instrucción). Tiene la FORMA de OKF (índice + fichas + links [[ ]]) pero
# otro frontmatter (`name`/`description`/`metadata.type`), así que se indexa para BUSCAR y se
# deja afuera de la conformancia OKF y del index.md.
# Sin esto los punteros de MEMORY.md son callejones sin salida: la única forma de llegar a una
# memoria sería tener el índice entero en contexto, y el índice tiene techo.
AUTOMEM = os.path.join(ROOT, "Agent", "memory")
# Las fichas de herramientas. `Tools/tools.md` es un ÍNDICE residente y delgado; el detalle de
# cada herramienta vive en un .md que se BUSCA. Sin esto, lo que se saca del arranque se
# volvería imposible de encontrar.
TOOLS = os.path.join(ROOT, "Tools")
# Tope del índice de memorias, en LÍNEAS (ver chequeo 9). El harness lo lee hasta 200.
MEM_IDX_MAX = 200
MEM_IDX_WARN = 185
RESERVED = ("index.md", "log.md")
NOW = datetime.datetime.now(datetime.timezone.utc)

# Orden en que se presentan las carpetas en el índice.
SECTIONS = [
    ("entities", "entities/ — personas, clientes, unidades de negocio"),
    ("concepts", "concepts/ — cómo funciona algo"),
    ("rules", "rules/ — reglas operativas (imperativas)"),
    ("reference", "reference/ — datos de referencia"),
    ("computations", "computations/ — cálculos sancionados (Attested Computation)"),
    ("projects", "projects/ — fichas de los proyectos de Projects/"),
]

C = {"dim": "\033[2m", "red": "\033[31m", "yel": "\033[33m", "grn": "\033[32m",
     "bold": "\033[1m", "end": "\033[0m"}
if not sys.stdout.isatty():
    C = {k: "" for k in C}


# ---------------------------------------------------------------- frontmatter

def _comentario_fuera(v):
    """Quita un comentario YAML inline. La regla de YAML es que el `#` necesita espacio
    antes; sin eso, un hex `#F5C518` se perdería. No toca lo que está entre comillas."""
    if v[:1] in "\"'":
        return v
    i = v.find(" #")
    return v[:i] if i > 0 else v


def _scalar(v):
    v = _comentario_fuera(v.strip()).strip()
    if v.startswith("{") and v.endswith("}"):
        out = {}
        for part in re.split(r",\s*(?=[A-Za-z_][\w-]*\s*:)", v[1:-1]):
            if ":" in part:
                k, _, val = part.partition(":")
                out[k.strip()] = _scalar(val)
        return out
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip('"\'') for x in v[1:-1].split(",") if x.strip()]
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return v


def parse_front(text):
    """Parser tolerante del subconjunto de YAML que usamos. Devuelve (dict, cuerpo)."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    raw, body = text[4:end], text[end + 4:].lstrip("\n")
    fm, key, stack = {}, None, None
    for line in raw.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        s = line.strip()
        if indent == 0 and re.match(r"^[A-Za-z_][\w-]*\s*:", s):
            key, _, val = s.partition(":")
            key = key.strip()
            if val.strip():
                fm[key] = _scalar(val)
                stack = None
            else:
                fm[key] = []
                stack = fm[key]
        elif isinstance(stack, list) and s.startswith("- "):
            item = s[2:].strip()
            if ":" in item and not item.startswith("{"):
                d = {}
                k2, _, v2 = item.partition(":")
                d[k2.strip()] = _scalar(v2)
                stack.append(d)
            else:
                stack.append(_scalar(item))
        elif isinstance(stack, dict) and ":" in s:
            k2, _, v2 = s.partition(":")
            stack[k2.strip()] = _scalar(v2)
        elif isinstance(stack, list) and not stack and ":" in s:
            # Mapping en bloque:  metadata:\n  type: feedback
            # El parser asumía que un valor vacío SIEMPRE abre una lista, así que un mapping
            # indentado quedaba como [] y sus claves eran invisibles. Así se perdía el
            # `metadata.type` de las 254 memorias, y cualquier `generated:` escrito en bloque.
            d = {}
            k2, _, v2 = s.partition(":")
            d[k2.strip()] = _scalar(v2)
            fm[key] = d
            stack = d
        elif isinstance(stack, list) and stack and isinstance(stack[-1], dict) and ":" in s:
            k2, _, v2 = s.partition(":")
            stack[-1][k2.strip()] = _scalar(v2)
    return fm, body


def dt(v):
    if not v:
        return None
    try:
        d = datetime.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None
    # Una fecha escrita sin zona ("2026-12-04") sale naive, y compararla con NOW —que es
    # aware— tira TypeError y tumba el linter entero. El schema permite la fecha sola, así
    # que se asume UTC en vez de exigir el timestamp completo.
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    return d


def tier(fm):
    """Tier de confianza según OKF §5.3."""
    v = fm.get("verified")
    if not v:
        return "unverified"
    entries = v if isinstance(v, list) else [v]
    for e in entries:
        by = str(e.get("by", "") if isinstance(e, dict) else e)
        if by.startswith("human:"):
            return "human-reviewed"
    return "machine-confirmed"


# ---------------------------------------------------------------- carga

class Doc:
    __slots__ = ("path", "rel", "fm", "body", "text")

    def __init__(self, path, root=None):
        self.path = path
        if root is None:
            if path.startswith(AUTOMEM + os.sep):
                root = AUTOMEM
            elif path.startswith(TOOLS + os.sep):
                root = TOOLS
            else:
                root = MEM
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        # Las memorias se muestran con su prefijo para que se vea de dónde salen: un
        # `Agent/memory/foo.md` en los resultados no se confunde con una página del wiki.
        if root == AUTOMEM:
            self.rel = f"Agent/memory/{rel}"
        elif root == TOOLS:
            self.rel = f"Tools/{rel}"
        else:
            self.rel = rel
        raw = open(path, encoding="utf-8", errors="replace").read()
        self.fm, self.body = parse_front(raw)
        self.fm = self.fm or {}
        self.text = raw

    # --- atajos
    @property
    def is_memory(self):
        return self.rel.startswith("Agent/memory/")

    @property
    def is_tool(self):
        return self.rel.startswith("Tools/")

    @property
    def type(self):
        # La auto-memoria declara su tipo en `metadata.type` (user/feedback/project/reference),
        # no en el `type` de OKF.
        t = self.fm.get("type")
        if not t:
            md = self.fm.get("metadata")
            if isinstance(md, dict):
                t = md.get("type")
        if not t and self.rel.startswith("Tools/"):
            t = "Tool"          # las fichas de herramienta son markdown pelado, sin frontmatter
        return t or ""

    @property
    def title(self):
        return self.fm.get("title") or os.path.basename(self.rel)[:-3]

    @property
    def desc(self):
        return self.fm.get("description", "")

    @property
    def status(self):
        # Una memoria no tiene `status` de OKF: si dejó de ser cierta, lo declara en
        # `metadata.status`. Sin esto una memoria equivocada no se podía jubilar — sólo
        # borrar, que es peor porque se pierde el caso que la originó.
        s = self.fm.get("status")
        if not s:
            md = self.fm.get("metadata")
            if isinstance(md, dict):
                s = md.get("status")
        return s or "stable"

    @property
    def gen_at(self):
        g = self.fm.get("generated")
        if isinstance(g, dict) and g.get("at"):
            return dt(g.get("at"))
        # Las memorias no llevan `generated`: su fecha es `metadata.modified`. Sin esto
        # salían con edad "?" en cada búsqueda y no había forma de ver cuál estaba vieja.
        md = self.fm.get("metadata")
        if isinstance(md, dict) and md.get("modified"):
            return dt(md.get("modified"))
        # Las fichas de Tools/ no llevan frontmatter: su frescura es la del archivo.
        if self.rel.startswith("Tools/") and os.path.exists(self.path):
            return datetime.datetime.fromtimestamp(
                os.path.getmtime(self.path), datetime.timezone.utc)
        return None

    @property
    def snapshot(self):
        """Registro congelado a una fecha de corte: no caduca, es historia."""
        return bool(self.fm.get("snapshot_as_of"))

    @property
    def stale(self):
        if self.snapshot:
            return False
        s = dt(self.fm.get("stale_after"))
        return bool(s and NOW >= s)

    @property
    def tier(self):
        return tier(self.fm)

    @property
    def is_session(self):
        return self.rel.startswith("Sessions/")


def load(include_sessions=True, include_memory=False, include_tools=False):
    """El bundle OKF. `include_memory` suma la auto-memoria y `include_tools` las fichas de
    herramientas: los dos sólo para BUSCAR — los chequeos de conformancia y el index.md los
    dejan afuera a propósito (ver AUTOMEM / TOOLS)."""
    docs = []
    for dp, _, fs in os.walk(MEM):
        for f in sorted(fs):
            if not f.endswith(".md") or f in RESERVED:
                continue
            p = os.path.join(dp, f)
            d = Doc(p, root=MEM)
            if not include_sessions and d.is_session:
                continue
            docs.append(d)
    if include_memory and os.path.isdir(AUTOMEM):
        for f in sorted(os.listdir(AUTOMEM)):
            # MEMORY.md es el índice de las memorias, no una memoria: listarlo en cada
            # búsqueda taparía la memoria concreta que se está buscando.
            if not f.endswith(".md") or f == "MEMORY.md":
                continue
            docs.append(Doc(os.path.join(AUTOMEM, f), root=AUTOMEM))
    if include_tools and os.path.isdir(TOOLS):
        for dp, dirs, fs in os.walk(TOOLS):
            dirs[:] = [x for x in dirs if x not in ("__pycache__", "node_modules")]
            for f in sorted(fs):
                # tools.md es el índice residente: ya está en contexto, listarlo en cada
                # búsqueda taparía la ficha concreta que se busca.
                if not f.endswith(".md") or f == "tools.md":
                    continue
                docs.append(Doc(os.path.join(dp, f), root=TOOLS))
    return docs


# ---------------------------------------------------------------- find

def fold(s):
    """Minúsculas sin acentos, para que 'atribución' matchee 'atribucion'."""
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")


STOP = {"de", "la", "el", "los", "las", "un", "una", "y", "o", "en", "del", "al",
        "que", "con", "por", "para", "se", "es", "lo", "su", "sus", "a"}


def cmd_find(args):
    phrase = fold(" ".join(args.terms)).strip()
    words = [w for w in re.split(r"[^\w]+", phrase) if w]
    terms = [w for w in words if w not in STOP and len(w) > 2] or words
    if not terms:
        sys.exit("kb.py find: hacen falta términos de búsqueda")
    docs = load(include_sessions=args.log, include_memory=not args.no_mem,
                include_tools=not args.no_mem)
    hits = []
    for d in docs:
        # Los campos NO valen lo mismo. Un `alias` existe con el único fin de rutear una
        # búsqueda: es una decisión deliberada de "esta página ES lo que buscás". Una
        # mención en el cuerpo es prosa. Sin esta jerarquía, buscar "servidor" devolvía
        # la página de monitoreo (5 menciones sueltas) antes que la del VPS, que lo
        # tiene como alias.
        alias = fold(" ".join(d.fm.get("aliases", []) or []))
        titulo = fold(d.title)
        meta = fold(" ".join([d.desc, d.rel, " ".join(d.fm.get("tags", []) or [])]))
        body = fold(d.body)
        score, matched = 0, 0
        for t in terms:
            n_al, n_ti = alias.count(t), titulo.count(t)
            n_me, n_bo = meta.count(t), body.count(t)
            if n_al or n_ti or n_me or n_bo:
                matched += 1
            score += (12 * min(n_al, 2) + 8 * min(n_ti, 2)
                      + 4 * min(n_me, 3) + min(n_bo, 6))
        if not matched:
            continue
        if len(words) > 1:                          # bonus por la frase completa
            score += (16 * min(alias.count(phrase), 1) + 12 * min(titulo.count(phrase), 1)
                      + 8 * min(meta.count(phrase), 2) + 6 * min(body.count(phrase), 3))
        score *= (1 + matched)                      # premia cubrir varios términos
        if d.status == "deprecated":
            score = score * 0.15 if args.all else 0
        if d.stale:
            score *= 0.5
        if d.tier == "human-reviewed":
            score *= 1.4
        if d.is_session:
            score *= 0.6                            # el log pesa menos que el wiki
        if d.is_tool:
            score *= 1.15      # una ficha de tool es densa y específica, como una memoria
        if d.is_memory:
            # Una memoria es UN hecho destilado: si matchea, el match es denso. Una página del
            # wiki es larga y puede matchear de pasada, y por volumen de cuerpo le ganaba a la
            # memoria que contesta exactamente la pregunta.
            score *= 1.3
        if score > 0:
            hits.append((score, d))

    hits.sort(key=lambda x: (-x[0], -(x[1].gen_at or datetime.datetime.min.replace(
        tzinfo=datetime.timezone.utc)).timestamp()))
    if not hits:
        print("sin resultados. Probá menos términos, o agregá un alias a la página "
              "que esperabas encontrar (ver Memory/schema.md §6).")
        return
    for score, d in hits[:args.n]:
        flags = []
        if d.status == "deprecated":
            flags.append(C["red"] + "OBSOLETA" + C["end"])
        if d.stale:
            flags.append(C["yel"] + "VENCIDA" + C["end"])
        if d.tier == "human-reviewed":
            flags.append(C["grn"] + "✓ humano" + C["end"])
        if d.snapshot:
            flags.append(C["dim"] + "snapshot " +
                         str(d.fm["snapshot_as_of"])[:10] + C["end"])
        age = f"{(NOW - d.gen_at).days}d" if d.gen_at else "?"
        shown = set()
        print(f"{C['bold']}{d.rel}{C['end']}  {C['dim']}[{d.type} · {age} · "
              f"{d.tier}]{C['end']}" + ("  " + " ".join(flags) if flags else ""))
        if d.desc:
            print(f"  {d.desc[:160]}")
        for t in ([phrase] if len(words) > 1 else []) + terms:
            for line in d.body.split("\n"):
                if t in fold(line) and line.strip():
                    if line.strip() not in shown:
                        shown.add(line.strip())
                        print(f"  {C['dim']}│{C['end']} {line.strip()[:150]}")
                    break
        print()
    if len(hits) > args.n:
        print(f"{C['dim']}… {len(hits) - args.n} más (usá -n){C['end']}")


def cmd_show(args):
    if os.path.isabs(args.path):
        p = args.path
    else:
        # `find` imprime las memorias como "Agent/memory/foo.md": ese mismo string tiene que
        # funcionar en `show`, o el resultado de una búsqueda no se puede abrir.
        rel = args.path
        for pref in ("Agent/memory/", "memory/"):
            if rel.startswith(pref):
                rel = rel[len(pref):]
                p = os.path.join(AUTOMEM, rel)
                break
        else:
            p = os.path.join(MEM, rel)
            if not os.path.exists(p) and os.path.exists(os.path.join(AUTOMEM, rel)):
                p = os.path.join(AUTOMEM, rel)
    if not os.path.exists(p):
        sys.exit(f"no existe: {p}")
    d = Doc(p)
    print(f"{C['bold']}{d.title}{C['end']}  {C['dim']}({d.rel}){C['end']}")
    print(f"tipo {d.type} · estado {d.status} · confianza {d.tier}"
          + (f" · escrito hace {(NOW - d.gen_at).days}d" if d.gen_at else ""))
    if d.snapshot:
        print(C["dim"] + "📷 SNAPSHOT congelado al " + str(d.fm["snapshot_as_of"])[:10]
              + " — es historia, no el estado actual" + C["end"])
    if d.stale:
        print(C["yel"] + "⚠ VENCIDA: pasó su stale_after — verificar antes de usar" + C["end"])
    if d.status == "deprecated":
        print(C["red"] + "⚠ OBSOLETA: no usar como fuente actual" + C["end"])
    print("-" * 70)
    print(d.body)


# ---------------------------------------------------------------- index (§8)

# El índice residente agrupa por TEMA, no por carpeta. Motivo: una línea por página crece
# para siempre en la capa que tiene presupuesto — con cientos de páginas son decenas de KB.
# Un tema describe igual de bien a 5 páginas que a 50, y deja de crecer con el inventario.
# El precio es la descripción por página (OKF §8 la pide con SHOULD, no MUST): se recupera
# entera con `kb.py find`, que además busca el cuerpo. Decisión local, ver Memory/schema.md §8.
# Los temas se configuran en Tools/kb/temas.json (el asistente los adapta al negocio del
# usuario en el onboarding). Si el archivo no existe, se usa este default.
TEMAS_DEFAULT = [
    ("Plata", ["finanzas", "precios", "pricing", "facturacion", "costos", "cobros", "impuestos"],
     "cuánto entra, cuánto sale, a qué precio y con qué margen"),
    ("El negocio", ["negocio", "oferta", "productos", "servicios", "ventas", "clientes",
                    "marketing"],
     "qué se vende, a quién, y cómo se entrega"),
    ("Contenido", ["contenido", "redes", "video", "blog", "email", "branding", "voz"],
     "qué se publica, en qué formato y con qué voz"),
    ("Herramientas y automatización", ["herramientas", "automatizacion", "integraciones",
                                       "mcp", "apis", "plataforma"],
     "las herramientas conectadas: cómo están armadas y qué las rompe"),
    ("Personas", ["personas", "equipo", "proveedores", "contactos"],
     "equipo, proveedores y contactos"),
    ("El asistente", ["asistente", "memoria", "contexto", "git", "okf", "skills", "sesion"],
     "cómo trabaja el asistente: memoria, contexto, reglas de operación, git"),
]


def _cargar_temas():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temas.json")
    if not os.path.exists(p):
        return TEMAS_DEFAULT
    try:
        return [(t["nombre"], [str(x).lower() for x in t["tags"]], t["descripcion"])
                for t in json.load(open(p, encoding="utf-8"))]
    except (ValueError, KeyError, TypeError) as e:
        print(f"⚠ Tools/kb/temas.json inválido ({e}); uso los temas por defecto",
              file=sys.stderr)
        return TEMAS_DEFAULT


TEMAS = _cargar_temas()


def _tema(d):
    tags = {str(x).lower() for x in (d.fm.get("tags") or [])}
    carpeta = d.rel.split("/")[0] if "/" in d.rel else ""
    for nombre, claves, _ in TEMAS:
        if tags & set(claves):
            return nombre
    if carpeta == "rules":
        return TEMAS[-1][0]
    return "Sin tema asignado"


def _marca(d):
    if d.status == "deprecated":
        return "ᴼᴮˢ"
    if d.snapshot:
        return "ˢⁿᵃᵖ"
    if d.stale:
        return "⚠"
    if d.tier == "human-reviewed":
        return "✓"
    return ""


def cmd_index(args):
    docs = load(include_sessions=False)
    fichas = [d for d in docs if d.type == "Project"]
    resto = [d for d in docs if d.type != "Project"]

    out = ["---", 'okf_version: "0.2"', "---", "",
           "# Índice del bundle", "",
           "Mapa por TEMA de las páginas del wiki (OKF §8). **Generado** por "
           "`python3 Tools/kb/kb.py index --write` — no editar a mano.", "",
           "> Esto dice **qué existe y dónde mirar**, no qué dice cada página. Para el "
           "contenido: `python3 Tools/kb/kb.py find \"<términos>\"`, que además busca el "
           "cuerpo, la auto-memoria de `Agent/memory/` y las fichas de `Tools/`.", "",
           "> Marcas: `✓` confirmado por el usuario · `⚠` vencida (verificar contra la fuente) · "
           "`ˢⁿᵃᵖ` foto congelada a una fecha · `ᴼᴮˢ` obsoleta.", ""]

    porTema = collections.defaultdict(list)
    for d in resto:
        porTema[_tema(d)].append(d)

    orden = [x[0] for x in TEMAS] + ["Sin tema asignado"]
    for nombre in orden:
        grupo = porTema.get(nombre)
        if not grupo:
            continue
        linea = next((c for n, _, c in TEMAS if n == nombre), "páginas sin tag de tema")
        out.append(f"## {nombre}")
        out.append(f"*{linea}* — {len(grupo)} páginas")
        out.append("")
        for carpeta in ("rules", "concepts", "reference", "entities", "computations", ""):
            enCarpeta = sorted([d for d in grupo
                                if (d.rel.split("/")[0] if "/" in d.rel else "") == carpeta],
                               key=lambda x: x.title.lower())
            if not enCarpeta:
                continue
            etiqueta = {"rules": "reglas", "concepts": "cómo funciona",
                        "reference": "datos", "entities": "fichas",
                        "computations": "cálculos sellados", "": "raíz"}[carpeta]
            items = " · ".join(f"[{d.title}]({d.rel}){_marca(d)}" for d in enCarpeta)
            out.append(f"- **{etiqueta}** — {items}")
        out.append("")

    out += ["## Proyectos", "",
            f"Las {len(fichas)} fichas de `Projects/` tienen **su propio índice**, que NO se "
            "carga al arrancar: [projects/index.md](projects/index.md).", "",
            "## Fuera del bundle", "",
            "* [../Tools/tools.md](../Tools/tools.md) — índice de herramientas; el detalle "
            "de cada una se busca.",
            "* [../User/user.md](../User/user.md) — perfil del usuario.",
            "* [../Agent/agent.md](../Agent/agent.md) — rol y estilo del asistente.",
            "* [Sessions/](Sessions/) — log crudo por día: se busca con `find --log`, "
            "no se lee entero.", ""]

    text = "\n".join(out)

    # El índice de proyectos vive aparte, en su carpeta (OKF §8 permite un index.md por
    # directorio). Ahí SÍ van las descripciones enteras: no cuesta contexto, no es residente.
    sub = ["# Fichas de proyecto", "",
           "Una por carpeta de `Projects/`. **No se carga al arrancar** — se llega desde "
           "[../index.md](../index.md) o con `kb.py find`.", ""]
    for d in sorted(fichas, key=lambda x: x.title.lower()):
        sub.append(f"* [{d.title}]({os.path.basename(d.rel)}){_marca(d)} - {d.desc}")
    sub.append("")
    sub_text = "\n".join(sub)

    if args.write:
        open(os.path.join(MEM, "index.md"), "w", encoding="utf-8").write(text)
        pdir = os.path.join(MEM, "projects")
        if os.path.isdir(pdir):
            open(os.path.join(pdir, "index.md"), "w", encoding="utf-8").write(sub_text)
        print(f"index.md escrito: {len(text):,} B, {len(resto)} páginas en "
              f"{len(porTema)} temas")
        print(f"projects/index.md escrito: {len(sub_text):,} B, {len(fichas)} fichas "
              f"(fuera del arranque)")
        sin = porTema.get("Sin tema asignado")
        if sin:
            print(f"  ⚠ {len(sin)} páginas sin tema: agregales un tag de "
                  f"Memory/schema.md §8")
    else:
        print(text)


# ---------------------------------------------------------------- lint

def cmd_lint(args):
    docs = load(include_sessions=True)
    wiki = [d for d in docs if not d.is_session]
    problems = 0

    def head(t):
        print(f"\n{C['dim']}=== {t} ==={C['end']}")

    head("1. Conformancia OKF v0.2 (§11)")
    for d in docs:
        if not d.fm:
            print(f"  {C['red']}✗{C['end']} sin frontmatter parseable: {d.rel}")
            problems += 1
        elif not d.fm.get("type"):
            print(f"  {C['red']}✗{C['end']} sin 'type': {d.rel}")
            problems += 1
    print(f"  {len(docs)} documentos revisados")

    head("2. Documentos vencidos (stale_after)")
    for d in sorted(docs, key=lambda x: x.rel):
        if d.stale and d.status != "deprecated":
            print(f"  {C['yel']}⚠{C['end']} {d.rel} — venció "
                  f"{dt(d.fm['stale_after']).date()}")
            problems += 1

    head("3. La fuente cambió después de escribirse el documento")
    for d in docs:
        g = d.gen_at
        for s in (d.fm.get("sources") or []):
            lm = dt(s.get("last_modified")) if isinstance(s, dict) else None
            if g and lm and lm > g:
                print(f"  {C['yel']}⚠{C['end']} {d.rel} — fuente "
                      f"'{s.get('id', s.get('resource', '?'))}' cambió "
                      f"{(lm - g).days}d después")
                problems += 1

    head("4. Contenido que decae y no declara hasta cuándo vale")
    # Un ID de Drive no caduca; el ESTADO alrededor sí. Estas son las señales de que el
    # contenido se pone viejo solo: montos, afirmaciones de estado, conteos de un sistema
    # vivo, e infraestructura. Las fichas de proyecto quedan afuera: su frescura ya la
    # cubren `last_activity` y el `last_modified` de su fuente.
    DECAE = {
        "plata":  re.compile(r"(U\$S|US\$|\$U|USD|EUR|€|ARS|MXN|COP|CLP|PEN|UYU|\$)\s?\d"),
        "estado": re.compile(r"estado (al|actual)|vigente|encendid|activ[oa] desde|"
                             r"corriendo|en producci", re.I),
        "conteo": re.compile(r"\b\d{2,}(\.\d{3})?\s+(contactos|alumnos|workflows|"
                             r"suscript|sitios|posts|filas|miembros)", re.I),
        "infra":  re.compile(r"(https?://[\w.-]+\.(onrender|app\.n8n|myshopify)|"
                             r"\b\d+\.\d+\.\d+\.\d+\b|puerto \d+)"),
    }
    for d in wiki:
        if (d.status == "deprecated" or d.snapshot or d.type == "Project"
                or str(d.fm.get("durable", "")).lower() == "true"):
            continue
        hits = sorted(k for k, p in DECAE.items() if len(p.findall(d.body)) >= 2)
        n = len(hits)
        if hits and not d.fm.get("stale_after"):
            print(f"  {C['yel']}⚠{C['end']} {d.rel} — decae ({', '.join(hits)}) "
                  f"y no tiene stale_after")
            problems += 1

    head("4.b Footnotes que no resuelven a una fuente (§5.1)")
    # El label de la footnote ES la clave de unión contra sources[].id. Si no matchea,
    # la atribución no resuelve — y falla en silencio: el markdown se ve perfecto.
    # También se controlan los ids duplicados, que hacen ambigua la unión.
    for d in wiki + [x for x in docs if x.is_session]:
        ids = [s.get("id") for s in (d.fm.get("sources") or []) if isinstance(s, dict)]
        usados = set(re.findall(r"\[\^([\w-]+)\](?!:)", d.body))
        huerfanas = sorted(u for u in usados if u not in ids)
        dup = sorted({i for i in ids if i and ids.count(i) > 1})
        if huerfanas:
            print(f"  {C['yel']}⚠{C['end']} {d.rel} — footnote sin fuente: "
                  f"{', '.join(huerfanas)}")
            problems += len(huerfanas)
        if dup:
            print(f"  {C['yel']}⚠{C['end']} {d.rel} — ids de fuente duplicados: "
                  f"{', '.join(dup)} (la unión queda ambigua)")
            problems += len(dup)

    head("5. Huérfanas (0 enlaces entrantes desde otro documento)")
    inbound = {d.rel: 0 for d in wiki}
    link_re = re.compile(r"\]\((/?[\w./-]+\.md)")
    for d in docs:
        for m in link_re.findall(d.body):
            t = m.lstrip("/")
            if not m.startswith("/"):
                t = os.path.normpath(os.path.join(
                    os.path.dirname(d.rel), m)).replace(os.sep, "/")
            if t in inbound and t != d.rel:
                inbound[t] += 1
    # Los enlaces de AFUERA del bundle también cuentan. AGENTS.md, user.md, agent.md y las
    # fichas de Tools/ apuntan a reglas del wiki todo el tiempo, y sin esto una regla enlazada
    # sólo desde el AGENTS.md se reportaba como huérfana — que es lo contrario de la verdad:
    # es la MÁS leída.
    fuera_re = re.compile(r"Memory/([\w./-]+\.md)")
    externos = [os.path.join(ROOT, x) for x in
                ("AGENTS.md", "CLAUDE.md", "User/user.md", "Agent/agent.md")]
    for dp, dirs, fs in os.walk(TOOLS):
        dirs[:] = [x for x in dirs if x not in ("__pycache__", "node_modules")]
        externos += [os.path.join(dp, f) for f in fs if f.endswith(".md")]
    for f in externos:
        if not os.path.exists(f):
            continue
        for m in fuera_re.findall(open(f, encoding="utf-8", errors="replace").read()):
            if m in inbound:
                inbound[m] += 1
    # No cuentan como huérfanos: los documentos de la raíz del bundle (son la puerta de
    # entrada, se llega desde AGENTS.md) ni los deprecated (OKF §5.4: se conservan por los
    # links y la historia, no se les exige que alguien los siga enlazando).
    # Las fichas de proyecto tampoco: son un INVENTARIO (una por carpeta real en disco),
    # no conocimiento que otra página debería citar. El chequeo 8 garantiza lo inverso —
    # que no falte ninguna — y `find` las alcanza igual.
    ROOT_DOCS = {d.rel for d in wiki if "/" not in d.rel}
    DEPREC = {d.rel for d in wiki if d.status == "deprecated"}
    INVENTARIO = {d.rel for d in wiki if d.type == "Project"}
    for rel, n in sorted(inbound.items()):
        if n == 0 and rel not in ROOT_DOCS | DEPREC | INVENTARIO:
            print(f"  {C['yel']}⚠{C['end']} {rel}")
            problems += 1

    head("6. Links rotos dentro del bundle")
    have = {d.rel for d in docs} | set(RESERVED) | {
        f"{p}/{r}" for d in docs if "/" in d.rel
        for p in [d.rel.split("/")[0]] for r in RESERVED}
    for d in docs:
        for m in link_re.findall(d.body):
            if m.startswith("http"):
                continue
            t = m.lstrip("/") if m.startswith("/") else os.path.normpath(
                os.path.join(os.path.dirname(d.rel), m)).replace(os.sep, "/")
            if t.startswith("..") or t in have:
                continue
            if not os.path.exists(os.path.join(MEM, t)):
                print(f"  {C['yel']}⚠{C['end']} {d.rel} → {m}")
                problems += 1

    head("7. Páginas multi-tema (>280 líneas y 3+ temas distintos, schema §9)")
    # El largo solo no sirve: una auditoría de 455 líneas es UN artefacto y partirla la
    # destruye, mientras que 223 líneas con 17 entradas cortas es una tabla de lookup sana.
    # Lo que molesta al recuperar es tener que atravesar temas ajenos, así que la señal es
    # "3+ secciones SUSTANCIALES distintas" — y no cuenta si son una colección de ítems
    # parecidos (demos por semana, lecturas por fecha), donde partir es fragmentar.
    for d in wiki:
        n = d.body.count("\n")
        # 280 y no 200: un rulebook coherente (una lista de precios, un procedimiento) tiene
        # secciones que son PASOS de un mismo procedimiento, y partirlo obliga a leer
        # tres páginas para contestar una pregunta. 200 era demasiado ajustado.
        if n <= 280:
            continue
        idx = [m.start() for m in re.finditer(r"^## ", d.body, re.M)] + [len(d.body)]
        heads = [d.body[a:b].split("\n")[0].strip() for a, b in zip(idx, idx[1:])]
        big = [h for h, (a, b) in zip(heads, zip(idx, idx[1:]))
               if d.body[a:b].count("\n") >= 40]
        if len(big) < 3:
            continue
        prefixes = collections.Counter(h[:22] for h in heads)
        if prefixes.most_common(1)[0][1] >= 3:      # colección de ítems parecidos
            continue
        print(f"  {C['yel']}⚠{C['end']} {d.rel} — {n} líneas en "
              f"{len(big)} secciones sustanciales")
        problems += 1

    head("8. Proyectos sin ficha en el bundle")
    # Una carpeta de Projects/ sin ficha es invisible para `find`: existe en disco y no
    # se puede encontrar.
    proj_dir = os.path.join(ROOT, "Projects")
    if os.path.isdir(proj_dir):
        fichas = {str(d.fm.get("resource", "")).rstrip("/")
                  for d in wiki if d.type == "Project"}
        for a in sorted(os.listdir(proj_dir)):
            if a.startswith(".") or not os.path.isdir(os.path.join(proj_dir, a)):
                continue
            if f"Projects/{a}" not in fichas:
                print(f"  {C['yel']}⚠{C['end']} Projects/{a} — sin ficha en "
                      f"Memory/projects/ (invisible para `find`)")
                problems += 1

    head("9. La memoria del asistente vive en el repo")
    # Claude Code escribe sus memorias en ~/.claude/projects/<repo>/memory. Ese path es de la
    # máquina, no del repo: si no está enlazado a Agent/memory, lo aprendido no se versiona y se
    # pierde con el disco. `bash setup.sh` crea el enlace. Con Codex no hace falta: las memorias se
    # escriben directo en Agent/memory/.
    destino = os.path.join(ROOT, "Agent", "memory")
    clave = re.sub(r"[^A-Za-z0-9]", "-", ROOT)
    esperado = os.path.expanduser(f"~/.claude/projects/{clave}/memory")
    base = os.path.expanduser("~/.claude/projects")
    enlace = None
    if os.path.isdir(base):
        for nom in os.listdir(base):
            cand = os.path.join(base, nom, "memory")
            if os.path.islink(cand) and os.path.realpath(cand) == os.path.realpath(destino):
                enlace = cand
                break
    hay_claude = os.path.isdir(os.path.expanduser("~/.claude"))
    if not enlace and not hay_claude:
        print(f"  {C['dim']}sin Claude Code en esta máquina: no hay enlace que verificar "
              f"(con Codex las memorias se escriben directo en Agent/memory/){C['end']}")
    elif not enlace:
        print(f"  {C['red']}✗{C['end']} la auto-memoria NO está enlazada al repo — lo que "
              f"aprenda el asistente no se versiona. Correr `bash setup.sh` (crea {esperado})")
        problems += 1
    if os.path.isdir(destino) and (enlace or not hay_claude):
        n = len([f for f in os.listdir(destino) if f.endswith(".md") and f != "MEMORY.md"])
        print(f"  {C['grn']}✓{C['end']} {'enlazada · ' if enlace else ''}{n} memorias")
        p_idx = os.path.join(destino, "MEMORY.md")
        if os.path.exists(p_idx):
            idx_l = sum(1 for _ in open(p_idx, encoding="utf-8", errors="replace"))
            # El harness lee el índice hasta ~200 LÍNEAS. Lo mantiene solo el hook
            # memoria-indice.sh (Tools/kb/memidx.py): acá sólo se avisa si no hizo su trabajo.
            if idx_l > MEM_IDX_MAX:
                print(f"  {C['red']}✗{C['end']} MEMORY.md {idx_l} líneas — PASÓ el tope de "
                      f"{MEM_IDX_MAX} y el gobernador no lo bajó. Correr "
                      f"`python3 Tools/kb/memidx.py --apply` y revisar el hook")
                problems += 1
            else:
                print(f"  {C['grn']}✓{C['end']} MEMORY.md {idx_l} líneas de {MEM_IDX_MAX}")

    head("10. El trabajo de hoy, ¿quedó registrado?")
    # El chequeo de destilación mira si se tocaron páginas del wiki — y daría verde aunque el
    # log de sesión no exista. Un día con muchos commits y ningún bloque es trabajo que quedó en
    # los mensajes de commit y no en la memoria de largo plazo.
    import subprocess
    hoy = datetime.datetime.now().date().isoformat()   # fecha LOCAL: el log se nombra así
    ses = os.path.join(MEM, "Sessions", f"session-{hoy}.md")
    commits = subprocess.run(
        ["git", "-C", ROOT, "log", f"--since={hoy} 00:00", "--format=%s"],
        capture_output=True, text=True).stdout.strip()
    n_com = len([l for l in commits.split("\n") if l.strip()])
    if not n_com:
        print(f"  {C['dim']}sin commits hoy{C['end']}")
    elif not os.path.exists(ses):
        print(f"  {C['red']}✗{C['end']} {n_com} commits hoy y NO existe {os.path.basename(ses)}")
        problems += 1
    else:
        cuerpo = open(ses, encoding="utf-8").read()
        n_blo = len(re.findall(r"^## \[", cuerpo, re.M))
        # Un bloque suele cubrir varios commits; el problema es que no haya casi ninguno.
        if n_blo == 0 or n_com > n_blo * 6:
            print(f"  {C['yel']}⚠{C['end']} {n_com} commits y sólo {n_blo} bloques en el log "
                  f"de sesión — hay trabajo que quedó sólo en los mensajes de commit")
            problems += 1
        else:
            print(f"  {C['grn']}✓{C['end']} {n_com} commits · {n_blo} bloques registrados")

    head("11. Destilación — ¿el trabajo se promueve, o queda enterrado en el log?")
    # Medirlo POR DÍA no sirve: bastaría UNA página tocada para que un día de 50 bloques diera
    # verde. Se mide por BLOQUE: cada
    # `## [fecha] tipo: titular` es una unidad de trabajo, y la pregunta de destilación es
    # "¿qué página del wiki cambia esto?". Un bloque que no enlaza ninguna página ni escribe
    # una memoria es conocimiento que quedó sólo en la narrativa del día.
    VENTANA = 14
    PISO = 50           # % de bloques que deben promover algo
    corte_b = NOW - datetime.timedelta(days=VENTANA)
    promueve = re.compile(r"\]\(\.\./(concepts|rules|reference|entities|projects|"
                          r"computations)/|\[\[[^\]]+\]\]")
    filas, tot_b, tot_p = [], 0, 0
    for d in docs:
        if not d.is_session or not d.gen_at or d.gen_at < corte_b:
            continue
        bloques = re.split(r"^## \[", d.body, flags=re.M)[1:]
        if not bloques:
            continue
        con = sum(1 for b in bloques if promueve.search(b))
        filas.append((d.rel, con, len(bloques)))
        tot_b += len(bloques)
        tot_p += con
    if not tot_b:
        print(f"  {C['dim']}sin sesiones en los últimos {VENTANA} días{C['end']}")
    else:
        pct = tot_p * 100 // tot_b
        peores = sorted(filas, key=lambda x: (x[1] * 100 // max(x[2], 1)))[:4]
        if pct < PISO:
            print(f"  {C['yel']}⚠{C['end']} {tot_p}/{tot_b} bloques ({pct}%) enlazan una "
                  f"página del wiki o escriben una memoria — el piso es {PISO}%")
            for rel, c, tot_ in peores:
                print(f"      {c:>3}/{tot_:<3} {rel.split('/')[-1]}")
            problems += 1
        else:
            print(f"  {C['grn']}✓{C['end']} {tot_p}/{tot_b} bloques ({pct}%) promueven algo "
                  f"al wiki o a la auto-memoria, en {VENTANA} días")

    head("12. Promoción sin retiro — la lección quedó escrita dos veces")
    # El patrón que más duplicación genera: una memoria enseña algo, después eso
    # se promueve a una regla del wiki (o a un hook) — y la memoria queda ENTERA. Se paga dos
    # veces y las dos copias se desincronizan. La memoria tiene que quedarse con el CASO (que
    # es lo que frena el error) y la regla con el PROCEDIMIENTO.
    TOPE_MEM = 1800
    mems = load(include_sessions=False, include_memory=True)
    mems = [d for d in mems if d.is_memory]
    ref_regla = re.compile(r"Memory/rules/([\w-]+\.md)")
    gordas = []
    for d in mems:
        reglas = set(ref_regla.findall(d.text))
        if reglas and len(d.text) > TOPE_MEM:
            gordas.append((len(d.text), d.rel, sorted(reglas)[0]))
    if gordas:
        for b, rel, regla in sorted(gordas, reverse=True):
            print(f"  {C['yel']}⚠{C['end']} {rel} — {b:,} B y el procedimiento ya vive en "
                  f"rules/{regla}")
            problems += 1
        print(f"  {C['dim']}   Dejá el caso concreto y el disparador; mandá el "
              f"procedimiento a la regla.{C['end']}")
    else:
        print(f"  {C['grn']}✓{C['end']} ninguna memoria repite entera una regla del wiki")

    head("13. Auto-memoria — fechas y jubilación")
    sin_fecha = [d for d in mems if not d.gen_at]
    consulta = [d for d in mems if d.type in ("reference", "project") and d.gen_at]
    viejas = sorted([d for d in consulta
                     if (NOW - d.gen_at).days > 180], key=lambda x: x.gen_at)
    if sin_fecha:
        print(f"  {C['yel']}⚠{C['end']} {len(sin_fecha)} memorias sin "
              f"`metadata.modified` — salen con edad '?' y no se pueden jubilar")
        for d in sin_fecha[:4]:
            print(f"      {d.rel}")
        problems += 1
    if viejas:
        print(f"  {C['dim']}{len(viejas)} memorias de consulta sin tocar hace +180 d "
              f"(candidatas a revisar, no es un error):{C['end']}")
        for d in viejas[:4]:
            print(f"      {(NOW - d.gen_at).days:>4}d  {d.rel}")
    if not sin_fecha and not viejas:
        print(f"  {C['grn']}✓{C['end']} {len(mems)} memorias, todas fechadas y frescas")

    print(f"\n{C['bold']}{problems} avisos.{C['end']}")
    return 1 if problems else 0


# ---------------------------------------------------------------- budget

# Lo que entra solo al arrancar: AGENTS.md (CLAUDE.md lo importa) y lo que manda leer.
STARTUP = ["AGENTS.md", "CLAUDE.md", "User/user.md", "Agent/agent.md",
           "Tools/tools.md", "Memory/index.md"]
LIMIT_TOK = 25000


def _desc_skills(d=None):
    """Bytes de las descripciones de skills. Claude Code y Codex cargan el nombre y la
    descripción de cada skill instalada en todas las sesiones: son residentes aunque no las pida
    nadie. Son las mismas en `.claude/skills/` y `.agents/skills/`, así que se cuentan una vez.
    Las ANIDADAS (`<subdir>/.claude/skills/`) no: se cargan la primera vez que se lee o edita un
    archivo de esa subcarpeta."""
    total, cuantas, gordas = 0, 0, []
    if d is None:
        d = os.path.join(ROOT, ".claude", "skills")
        if not os.path.isdir(d):
            d = os.path.join(ROOT, ".agents", "skills")
    if not os.path.isdir(d):
        return 0, 0, []
    for nom in sorted(os.listdir(d)):
        f = os.path.join(d, nom, "SKILL.md")
        if not os.path.exists(f):
            continue
        txt = open(f, encoding="utf-8", errors="replace").read()[:8000]
        m = re.search(r"^description:\s*(.*?)(?=^[A-Za-z_][\w-]*:|^---)", txt,
                      re.S | re.M)
        b = len(m.group(1).strip().encode()) if m else 0
        total += b + len(nom) + 2
        cuantas += 1
        if b > 400:
            gordas.append((b, nom))
    return total, cuantas, sorted(gordas, reverse=True)


def _skills_anidadas():
    """Las skills que viven en un `<subdir>/.claude/skills/` y NO entran al arranque."""
    fuera = []
    for dp, dirs, _ in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in ("node_modules", ".git")]
        if os.path.basename(dp) != "skills" or os.path.basename(os.path.dirname(dp)) != ".claude":
            continue
        rel = os.path.relpath(dp, ROOT)
        if rel == os.path.join(".claude", "skills"):
            continue                       # ésa es la de la raíz: sí es residente
        b, n, _ = _desc_skills(dp)
        if n:
            fuera.append((rel, n, b))
    return sorted(fuera)


def cmd_budget(args):
    """Mide TODO lo residente, no sólo los archivos que el repo controla: también el índice de
    la auto-memoria (lo carga el harness) y las descripciones de las skills instaladas (las carga
    el agente). Sin esos dos, el número subestima la carga real a la mitad."""
    filas, total = [], 0
    print(f"{C['bold']}Costo de contexto del arranque{C['end']}\n")
    for rel in STARTUP:
        pth = os.path.join(ROOT, rel)
        filas.append((os.path.getsize(pth) if os.path.exists(pth) else 0, rel, ""))

    idx = os.path.join(AUTOMEM, "MEMORY.md")
    if os.path.exists(idx):
        filas.append((os.path.getsize(idx), "Agent/memory/MEMORY.md",
                      "Claude Code lo carga solo; en Codex, AGENTS.md manda leerlo"))
    b_sk, n_sk, gordas = _desc_skills()
    if n_sk:
        filas.append((b_sk, f"descripciones de {n_sk} skills",
                      "las carga el agente en cada sesión"))

    for b, rel, nota in filas:
        total += b
        extra = f"  {C['dim']}({nota}){C['end']}" if nota else ""
        print(f"  {b:9,} B  {rel}{extra}")
    tok = total // 4
    print(f"  {'-' * 9}")
    print(f"  {total:9,} B  TOTAL ≈ {tok:,} tokens (estimado a 4 B/token)")
    ok = tok <= LIMIT_TOK
    color = C["grn"] if ok else C["red"]
    print(f"\n  {color}{'✓' if ok else '✗'} presupuesto {LIMIT_TOK:,} tokens — "
          f"{'dentro' if ok else 'EXCEDIDO'} ({tok * 100 // LIMIT_TOK}%){C['end']}")

    if gordas:
        print(f"\n{C['dim']}  Descripciones de skill por encima de 400 B "
              f"({len(gordas)}), las 5 peores:{C['end']}")
        for b, nom in gordas[:5]:
            print(f"  {b:9,} B  skills/{nom}")

    anidadas = _skills_anidadas()
    if anidadas:
        print(f"\n{C['dim']}  Skills ANIDADAS — no entran al arranque; se cargan la "
              f"primera vez\n  que lee o edita un archivo de esa carpeta:{C['end']}")
        for rel, cuantas, b in anidadas:
            print(f"  {b:9,} B  {cuantas} skills en {rel}")

    print(f"\n{C['dim']}  Fuera del arranque, a propósito (se busca con `kb.py find`):{C['end']}")
    fuera = [("Memory/ (wiki)", MEM, {"Sessions"}),
             ("Memory/Sessions/", os.path.join(MEM, "Sessions"), set()),
             ("Agent/memory/", AUTOMEM, set()),
             ("Tools/ (fichas)", TOOLS, set())]
    for nombre, base, saltar in fuera:
        b = 0
        for dp, dirs, fs in os.walk(base):
            dirs[:] = [x for x in dirs if x not in saltar | {"__pycache__", "node_modules"}]
            b += sum(os.path.getsize(os.path.join(dp, f))
                     for f in fs if f.endswith(".md"))
        print(f"  {b:9,} B  {nombre}")
    return 0 if ok else 1


# ---------------------------------------------------------------- cli

def main():
    ap = argparse.ArgumentParser(prog="kb.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("find", help="buscar en el bundle + la auto-memoria")
    f.add_argument("terms", nargs="+")
    f.add_argument("--log", action="store_true", help="incluir Sessions/")
    f.add_argument("--all", action="store_true", help="incluir obsoletas")
    f.add_argument("--no-mem", action="store_true",
                   help="sólo el wiki: NO buscar en Agent/memory/ ni en Tools/")
    f.add_argument("-n", type=int, default=6)
    f.set_defaults(fn=cmd_find)

    s = sub.add_parser("show", help="ver un documento")
    s.add_argument("path")
    s.set_defaults(fn=cmd_show)

    i = sub.add_parser("index", help="regenerar index.md")
    i.add_argument("--write", action="store_true")
    i.set_defaults(fn=cmd_index)

    sub.add_parser("lint", help="chequeo de salud").set_defaults(fn=cmd_lint)
    sub.add_parser("budget", help="costo del arranque").set_defaults(fn=cmd_budget)

    a = ap.parse_args()
    sys.exit(a.fn(a) or 0)


if __name__ == "__main__":
    main()
