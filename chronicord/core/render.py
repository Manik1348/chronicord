import csv
import glob
import html
import json
import os
from datetime import datetime

from .convert import LOCAL_TZ
from .viewer import CHANNEL_HTML, ROOT_HTML
from ..i18n import _, VIEWER

SYS = {1: "добавил участника", 2: "удалил участника", 3: "звонок", 4: "изменил название канала",
       6: "закрепил сообщение", 7: "присоединился к серверу", 8: "забустил сервер",
       9: "забустил сервер", 10: "забустил сервер", 11: "забустил сервер",
       18: "создал ветку", 21: "начальное сообщение ветки", 46: "результаты опроса"}


def iter_messages(d):
    for p in sorted(glob.glob(os.path.join(d, "part-*.jsonl"))):
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except ValueError:
                        pass


def fmt_ts(ts):
    return datetime.fromtimestamp(ts, LOCAL_TZ).strftime("%d.%m.%Y %H:%M")


def plain(m):
    parts = []
    if m.get("k") in SYS and not m.get("c"):
        parts.append("[%s]" % _(SYS[m["k"]]))
    if m.get("c"):
        parts.append(m["c"])
    for f in m.get("fwd") or []:
        parts.append(_("[переслано] ") + (f.get("c") or ""))
    for a in m.get("att") or []:
        parts.append(_("[файл: %s]") % a.get("fn"))
    for e in m.get("emb") or []:
        parts.append(_("[встраивание: %s]") % (e.get("t") or e.get("d") or e.get("u") or ""))
    for s in m.get("st") or []:
        parts.append(_("[стикер: %s]") % s)
    pl = m.get("pl")
    if pl:
        parts.append(_("[опрос: %s] ") % pl.get("q") + "; ".join(
            "%s%s — %d" % ((a.get("e") + " ") if a.get("e") else "", a.get("t"), a.get("n", 0)) for a in pl.get("ans", [])))
    if m.get("rx"):
        parts.append(_("[реакции: %s]") % " ".join("%s×%d" % (r["e"], r["n"]) for r in m["rx"]))
    if m.get("th"):
        parts.append(_("[ветка: %s]") % m["th"].get("n"))
    return "\n".join(parts)


def render_channel(d, formats, lang="ru"):
    meta = {}
    try:
        with open(os.path.join(d, "meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, ValueError):
        pass
    if "txt" in formats:
        with open(os.path.join(d, "messages.txt"), "w", encoding="utf-8") as f:
            f.write("%s / #%s\n\n" % (meta.get("guild", ""), meta.get("channel", "")))
            for m in iter_messages(d):
                f.write("[%s] %s%s\n%s\n\n" % (fmt_ts(m["ts"]), m["a"]["n"], _(" (ред.)") if m.get("ed") else "", plain(m)))
    if "csv" in formats:
        with open(os.path.join(d, "messages.csv"), "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["id", _("дата"), _("автор_id"), _("автор"), _("текст"), _("вложения"), _("реакции"), _("ответ_на")])
            for m in iter_messages(d):
                w.writerow([m["id"], fmt_ts(m["ts"]), m["a"].get("id"), m["a"]["n"], plain(m),
                            " ".join("media/" + a["file"] for a in m.get("att") or []),
                            " ".join("%s×%d" % (r["e"], r["n"]) for r in m.get("rx") or []), m.get("rp", "")])
    if "html" in formats:
        dd = os.path.join(d, "data")
        os.makedirs(dd, exist_ok=True)
        for old in glob.glob(os.path.join(dd, "part-*.js")):
            os.remove(old)
        n, batch, chunk = 0, [], 5000
        files = []

        def flush():
            name = "part-%04d.js" % (len(files) + 1)
            with open(os.path.join(dd, name), "w", encoding="utf-8") as f:
                f.write("CHR.push(")
                json.dump(batch, f, ensure_ascii=False, separators=(",", ":"))
                f.write(");\n")
            files.append("data/" + name)

        for m in iter_messages(d):
            batch.append(m)
            n += 1
            if len(batch) >= chunk:
                flush()
                batch = []
        if batch:
            flush()
        page = CHANNEL_HTML.replace("__TITLE__", html.escape("#%s — %s" % (meta.get("channel", ""), meta.get("guild", ""))))
        page = page.replace("__META__", json.dumps(meta, ensure_ascii=False).replace("</", "<\\/"))
        page = page.replace("__FILES__", json.dumps(files)).replace("__L__", json.dumps(VIEWER.get(lang, VIEWER["ru"]), ensure_ascii=False)).replace("__LANG__", lang)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(page)


def render_root(out, lang="ru"):
    items = []
    for mp in glob.glob(os.path.join(out, "*", "meta.json")):
        try:
            with open(mp, encoding="utf-8") as f:
                meta = json.load(f)
        except (OSError, ValueError):
            continue
        d = os.path.dirname(mp)
        st = {}
        try:
            with open(os.path.join(d, "state.json"), encoding="utf-8") as f:
                st = json.load(f)
        except (OSError, ValueError):
            pass
        items.append({"dir": os.path.basename(d), "guild": meta.get("guild"), "channel": meta.get("channel"),
                      "parent": meta.get("parent"), "count": st.get("count", 0),
                      "html": os.path.exists(os.path.join(d, "index.html")), "type": meta.get("type", 0)})
    items.sort(key=lambda x: (x["guild"] or "", x["parent"] or x["channel"] or "", x["parent"] is not None, x["channel"] or ""))
    L = VIEWER.get(lang, VIEWER["ru"])
    page = ROOT_HTML.replace("__ITEMS__", json.dumps(items, ensure_ascii=False).replace("</", "<\\/"))
    page = page.replace("__L__", json.dumps(L, ensure_ascii=False)).replace("__LANG__", lang).replace("__ARCHIVE__", L["archive"]).replace("__MADE__", L["made"])
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
