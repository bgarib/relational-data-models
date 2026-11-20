"""Turn a MySQL Workbench .mwb model into MySQL DDL and a Mermaid ER diagram."""
import sys, zipfile, xml.etree.ElementTree as ET
def kid(el, key): return next((c for c in el if c.get("key") == key), None)
def txt(el, key):
    c = kid(el, key); return c.text if c is not None else None
def load(path):
    root = ET.fromstring(zipfile.ZipFile(path).read("document.mwb.xml"))
    tables, colname, tabname = [], {}, {}
    for t in root.iter("value"):
        if t.get("struct-name") != "db.mysql.Table": continue
        tabname[t.get("id")] = txt(t, "name")
        cols = []
        for c in kid(t, "columns"):
            colname[c.get("id")] = txt(c, "name")
            typ = (txt(c, "simpleType") or txt(c, "userType") or "").split(".")[-1].upper()
            ln, pr, sc = int(txt(c, "length")), int(txt(c, "precision")), int(txt(c, "scale"))
            ep = txt(c, "datatypeExplicitParams")
            if ep: typ += ep
            elif ln > 0: typ += f"({ln})"
            elif pr > 0: typ += f"({pr},{sc})" if sc >= 0 else f"({pr})"
            cols.append(dict(id=c.get("id"), name=txt(c, "name"), type=typ, notnull=txt(c, "isNotNull") == "1"))
        pk, uniq = [], []
        for ix in kid(t, "indices") or []:
            cs = [txt(ic, "referencedColumn") for ic in kid(ix, "columns")]
            if txt(ix, "isPrimary") == "1": pk = cs
            elif txt(ix, "unique") == "1" or txt(ix, "indexType") == "UNIQUE": uniq.append((txt(ix, "name"), cs))
        fks = []
        for fk in kid(t, "foreignKeys") or []:
            fks.append(dict(name=txt(fk, "name"), cols=[l.text for l in kid(fk, "columns")],
                            ref=txt(fk, "referencedTable"), refcols=[l.text for l in kid(fk, "referencedColumns")],
                            on_delete=txt(fk, "deleteRule") or "NO ACTION"))
        tables.append(dict(id=t.get("id"), name=txt(t, "name"), cols=cols, pk=pk, uniq=uniq, fks=fks))
    return tables, colname, tabname
def ddl(tables, colname, tabname):
    order, done = [], set()
    def visit(t):
        if t["id"] in done: return
        done.add(t["id"])
        for f in t["fks"]:
            dep = next((x for x in tables if x["id"] == f["ref"]), None)
            if dep and dep is not t: visit(dep)
        order.append(t)
    for t in sorted(tables, key=lambda x: x["name"]): visit(t)
    out = []
    for t in order:
        lines = [f"  {c['name']} {c['type']}{' NOT NULL' if c['notnull'] else ''}" for c in t["cols"]]
        if t["pk"]: lines.append(f"  PRIMARY KEY ({', '.join(colname[i] for i in t['pk'])})")
        for n, cs in t["uniq"]: lines.append(f"  UNIQUE KEY {n} ({', '.join(colname[i] for i in cs)})")
        for f in t["fks"]:
            lines.append(f"  CONSTRAINT {f['name']} FOREIGN KEY ({', '.join(colname[i] for i in f['cols'])}) "
                         f"REFERENCES {tabname[f['ref']]} ({', '.join(colname[i] for i in f['refcols'])})"
                         + (f" ON DELETE {f['on_delete']}" if f['on_delete'] not in ("NO ACTION", "RESTRICT") else ""))
        out.append(f"CREATE TABLE {t['name']} (\n" + ",\n".join(lines) + "\n);\n")
    return "\n".join(out)
def mermaid(tables, colname, tabname):
    out = ["erDiagram"]
    for t in sorted(tables, key=lambda x: x["name"]):
        fkcols = {i for f in t["fks"] for i in f["cols"]}
        out.append(f"    {t['name']} {{")
        for c in t["cols"]:
            tag = ",".join(k for k, v in (("PK", c["id"] in t["pk"]), ("FK", c["id"] in fkcols)) if v)
            out.append(f"        {c['type'].split('(')[0].lower()} {c['name']}{' ' + tag if tag else ''}")
        out.append("    }")
    for t in tables:
        for f in t["fks"]:
            ident = set(f["cols"]) <= set(t["pk"])
            out.append(f"    {tabname[f['ref']]} ||--o{{ {t['name']} : \"{', '.join(colname[i] for i in f['cols'])}\"")
    return "\n".join(out)
if __name__ == "__main__":
    tb = load(sys.argv[1])
    open(sys.argv[2], "w").write(ddl(*tb)); open(sys.argv[3], "w").write(mermaid(*tb))
