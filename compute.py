"""Join webref IDL surface x MDN BCD support -> per-spec / per-vendor coverage.
Offline. Run: python compute.py  (self-checks at the end)
"""
import json, os, re, glob

D = r"D:\w3c\Hackthon\task1\data"
WEBREF = os.path.join(D, "webref", "webref-main", "ed")
VENDORS = ["chrome", "safari", "firefox"]

bcd = json.load(open(os.path.join(D, "bcd.json"), encoding="utf8"))
api = bcd["api"]
META = {"bcd": bcd["__meta"]["version"]}

CMT = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)
BLOCK = re.compile(r"(?:partial\s+)?(?:interface|namespace)\s+(?:mixin\s+)?(\w+)[^{;]*\{")
ATTR = re.compile(r"attribute\s+[\w<>?\[\],.\s]+?\s(\w+)\s*;")
OP = re.compile(r"[\w<>?\[\],.\s]+?\s(\w+)\s*\([^)]*\)\s*;")
CONST = re.compile(r"\bconst\s+[\w<>?\[\],.\s]+?\s(\w+)\s*=")


def body_members(txt):
    out, i = [], 0
    while True:
        m = BLOCK.search(txt, i)
        if not m:
            break
        depth, j = 1, m.end()
        while j < len(txt) and depth:
            depth += {"{": 1, "}": -1}.get(txt[j], 0)
            j += 1
        body, i = txt[m.end():j - 1], j
        for kind, rx in (("attr", ATTR), ("op", OP), ("const", CONST)):
            for mm in rx.finditer(body):
                out.append((m.group(1), kind, mm.group(1)))
    return out


def support(entry):
    """shipped by default in that engine? 'preview'/'behind flag' = no"""
    if not isinstance(entry, dict):
        return False
    v = entry.get("version_added")
    if v is False or v is None or v == "" or v == "preview":
        return False
    return not entry.get("flags")          # flag-gated = not shipped


def look(iface, kind, name):
    e = api.get(iface)
    if not isinstance(e, dict):
        return None
    cands = [name] if kind == "const" else [name, name + "_static", name + "_event"]
    for c in cands:
        node = e.get(c)
        if isinstance(node, dict) and "__compat" in node:
            sup = node["__compat"].get("support", {})

            def norm(x):
                x = x or {}
                if isinstance(x, list):
                    x = x[0] if x else {}
                return support(x)
            return tuple(norm(sup.get(v)) for v in VENDORS)
    return None


specs, seen, all_ifaces = [], {}, set()
DECL = re.compile(r"(?:partial\s+)?(?:interface|namespace)\s+(?:mixin\s+)?(\w+)[^{;]*\{")
declared, allfeat = set(), set()
for f in sorted(glob.glob(os.path.join(WEBREF, "idl", "*.idl"))):
    sn = os.path.basename(f)[:-4]
    txt = CMT.sub(" ", open(f, encoding="utf8", errors="replace").read())
    declared.update(DECL.findall(txt))
    hp = os.path.join(WEBREF, "headings", sn + ".json")
    hd = json.load(open(hp, encoding="utf8")) if os.path.exists(hp) else {}
    spec = hd.get("spec") or {}
    feats, ifaces = {}, set()
    for iface, kind, name in body_members(txt):
        all_ifaces.add(iface)
        allfeat.add((iface, name))
        if iface not in api:
            continue                       # not in BCD: cannot score, excluded
        ifaces.add(iface)
        if (iface, name) in feats:
            continue
        s = look(iface, kind, name)
        if s is not None:
            feats[(iface, name)] = s
    if not feats:
        continue
    seen.update({k: v for k, v in feats.items() if k not in seen})
    b = [0, 0, 0, 0]                       # shipped by 0 / 1 / 2 / 3 engines
    thin = []
    for (i, n), s in feats.items():
        b[sum(s)] += 1
        if sum(s) <= 1:
            who = "none" if not sum(s) else VENDORS[[j for j, x in enumerate(s) if x][0]]
            thin.append(f"{i}.{n} · {who}")
    specs.append({"sn": sn, "title": spec.get("title") or sn, "url": spec.get("url", ""),
                  "n": len(feats), "b": b, "thin": sorted(thin)[:30]})

g = [0, 0, 0, 0]
per = {v: 0 for v in VENDORS}
sole = {v: [] for v in VENDORS}
for (iface, name), s in seen.items():
    n = sum(s)
    g[n] += 1
    for i, v in enumerate(VENDORS):
        if s[i]:
            per[v] += 1
            if n == 1:
                sole[v].append(f"{iface}.{name}")

out = {"meta": dict(META, specs=len(specs), interfaces=len({i for i, _ in seen}),
                    features=len(seen), buckets=g, perVendor=per,
                    bcdInterfaces=len(api), webrefInterfaces=len(all_ifaces),
                    declared=len(declared), declaredMembers=len(allfeat),
                    interfacesWithRecord=len({i for i in all_ifaces if i in api}),
                    soleN={v: len(sole[v]) for v in VENDORS}),
       "sole": {v: sole[v][:200] for v in VENDORS},
       "specs": specs}
json.dump(out, open(r"D:\w3c\Hackthon\task1\coverage.json", "w", encoding="utf8"), ensure_ascii=False)

assert sum(g) == len(seen) and len(specs) > 200 and g[3] > 1000, (len(specs), g)
assert all(sum(s["b"]) == s["n"] for s in specs)
print("specs", len(specs), "| features", len(seen), "| buckets", g, "| perVendor", per, "| sole", out["meta"]["soleN"])
print("all-three share: %.1f%%" % (100 * g[3] / len(seen)))
print("file %.0f KB" % (os.path.getsize(r"D:\w3c\Hackthon\task1\coverage.json") / 1024))
