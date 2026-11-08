import json
import os
import re
import time
from datetime import datetime, timezone

from .. import VERSION
from ..i18n import _
from .api import ApiError, Cancelled, download
from .convert import Anonymizer, Ctx, convert, att_file as msg_att_file, snow_ts, ts_snow, LOCAL_TZ, STICKER_EXT
from . import render

PART_BYTES = 20 * 1024 * 1024
TEXT_TYPES = (0, 5)
THREAD_TYPES = (10, 11, 12)
FORUM_TYPES = (15, 16)
VOICE_TYPES = (2, 13)


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(path, data, indent=1):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    os.replace(tmp, path)


def safe_name(s, n=40):
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", s or "").strip(" ._")
    return s[:n] or "channel"


def mb(n):
    return _("%.1f МБ") % (n / 1048576)


class Exporter:

    def __init__(self, client, opt, log=print, progress=None):
        self.c = client
        self.opt = opt
        self.log = log
        self.progress = progress or (lambda **kw: None)
        self.anon = Anonymizer(opt.get("anon_rules"))
        self._active_threads = {}
        self._msg_threads = {}
        self.assets = os.path.join(opt["out_dir"], "assets")


    def guilds(self):
        return self.c.get("/users/@me/guilds")

    def guild_tree(self, gid):
        chans = self.c.get("/guilds/%s/channels" % gid)
        return sorted(chans, key=lambda c: (c.get("position", 0), c["id"]))

    def members(self, gid, cap=10000):
        out, after = [], "0"
        while len(out) < cap:
            batch = self.c.get("/guilds/%s/members?limit=1000&after=%s" % (gid, after))
            if not batch:
                break
            out.extend(batch)
            after = batch[-1]["user"]["id"]
            if len(batch) < 1000:
                break
        return out

    def threads_of(self, gid, ch):
        res = {}
        if gid not in self._active_threads:
            try:
                self._active_threads[gid] = self.c.get("/guilds/%s/threads/active" % gid).get("threads", [])
            except ApiError as e:
                self.log(_("  Не удалось получить активные ветки (%s).") % e.status)
                self._active_threads[gid] = []
        n_active = 0
        for t in self._active_threads[gid]:
            if t.get("parent_id") == ch["id"]:
                res[t["id"]] = t
                n_active += 1
        kinds = ["public"] + (["private"] if self.opt.get("private_threads") and ch.get("type") not in FORUM_TYPES else [])
        n_arch = 0
        for kind in kinds:
            before = None
            while True:
                q = "/channels/%s/threads/archived/%s?limit=100" % (ch["id"], kind)
                if before:
                    q += "&before=" + before
                try:
                    r = self.c.get(q)
                except ApiError as e:
                    if kind == "private":
                        self.log(_("  Закрытые ветки #%s недоступны (нужно право «Управлять ветками»).") % ch.get("name"))
                    else:
                        self.log(_("  Не удалось получить архивные ветки #%s (%s). Проверь право «Читать историю сообщений».")
                                 % (ch.get("name"), e.status))
                    break
                ts = r.get("threads", [])
                for t in ts:
                    if t["id"] not in res:
                        n_arch += 1
                    res[t["id"]] = t
                if not r.get("has_more") or not ts:
                    break
                before = (ts[-1].get("thread_metadata") or {}).get("archive_timestamp")
                if not before:
                    break
        self.log(_("  Веток найдено: %d (активных %d, архивных %d)") % (len(res), n_active, n_arch))
        return res


    def run(self, selection):
        os.makedirs(self.opt["out_dir"], exist_ok=True)
        started = time.time()
        for item in selection:
            g = item["guild"]
            chans = self.c.get("/guilds/%s/channels" % g["id"])
            roles = {r["id"]: r["name"] for r in self.c.get("/guilds/%s/roles" % g["id"])}
            names = {c["id"]: c["name"] for c in chans}
            ctx = Ctx(self.c, g["id"], roles, names, self.anon)
            if item.get("server_assets"):
                self.server_assets(g)
            for ch in item["channels"]:
                self.c.check()
                want = self.opt.get("threads") or ch.get("type") in FORUM_TYPES
                threads = self.threads_of(g["id"], ch) if want else {}
                self._msg_threads = {}
                if ch.get("type") not in FORUM_TYPES:
                    self.export_channel(ch, g, ctx, threads=threads, render_now=False)
                    if want:
                        extra = {k: v for k, v in self._msg_threads.items() if k not in threads}
                        if extra:
                            self.log(_("  + ещё веток по сообщениям: %d") % len(extra))
                            threads.update(extra)
                d = self.chan_dir(ch)
                for t in load_json(os.path.join(d, "meta.json"), {}).get("threads") or []:
                    if want and t.get("id") not in threads:
                        threads[t["id"]] = {"id": t["id"], "name": t.get("n", ""), "type": 11}
                tl = sorted(threads.values(), key=lambda t: int(t["id"]))
                for t in tl:
                    names[t["id"]] = t.get("name", "")
                os.makedirs(d, exist_ok=True)
                save_json(os.path.join(d, "meta.json"), self.base_meta(ch, g, threads=tl))
                if ch.get("type") in FORUM_TYPES:
                    self.log(_("\n#%s — форум, веток: %d") % (ch.get("name"), len(tl)))
                self.render(d)
                for t in tl:
                    self.export_channel(t, g, ctx, parent=ch)
        render.render_root(self.opt["out_dir"], self.opt.get("lang", "ru"))
        self.log(_("\nВсё. Время: %d мин. Файлы — в папке %s") % ((time.time() - started) // 60, self.opt["out_dir"]))

    def chan_dir(self, ch):
        return os.path.join(self.opt["out_dir"], "%s_%s%s" % (safe_name(ch.get("name")), ch["id"], self.opt.get("tag", "")))

    def base_meta(self, ch, g, parent=None, threads=None):
        meta = {"exporter": "chronicord", "version": VERSION, "guild_id": g["id"], "guild": g["name"],
                "channel_id": ch["id"], "channel": ch.get("name", ""), "type": ch.get("type", 0),
                "from": self.opt.get("from_s"), "to": self.opt.get("to_s"), "limit": self.opt.get("limit"),
                "assets": "../assets",
                "exported": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        if parent:
            meta["parent_id"] = parent["id"]
            meta["parent"] = parent.get("name", "")
            meta["parent_dir"] = os.path.basename(self.chan_dir(parent))
        if threads:
            meta["threads"] = [{"id": t["id"], "n": t.get("name", ""), "dir": os.path.basename(self.chan_dir(t))}
                               for t in threads]
        return meta

    def render(self, d):
        fm = set(self.opt.get("formats") or ())
        if fm - {"json"}:
            render.render_channel(d, fm, self.opt.get("lang", "ru"))

    def export_channel(self, ch, g, ctx, parent=None, threads=None, render_now=True):
        o = self.opt
        d = self.chan_dir(ch)
        media = os.path.join(d, "media")
        os.makedirs(d, exist_ok=True)
        save_json(os.path.join(d, "meta.json"), self.base_meta(ch, g, parent, sorted((threads or {}).values(), key=lambda t: int(t["id"]))))
        st_path = os.path.join(d, "state.json")
        st = load_json(st_path, {"after": "0", "part": 1, "count": 0, "atts": 0, "att_bytes": 0,
                                 "media_after": "0", "media_ok": 0, "media_fail": 0, "media_bytes": 0})
        st.setdefault("assets_ok", 0)
        dl = bool(o.get("attachments") or o.get("avatars") or o.get("emoji") or o.get("stickers"))
        label = (_("  ↳ ветка «%s»") % ch.get("name")) if parent else (_("\n#%s") % ch.get("name"))
        self.log(_("%s — %s") % (label, _("продолжаю") if st["after"] != "0" else _("начинаю")))

        start = "0"
        if o.get("from_ts"):
            start = ts_snow(o["from_ts"] - 1)

        def cur(key):
            return st[key] if st[key] != "0" else start

        if dl and int(cur("media_after")) < int(cur("after")):
            self.log(_("  докачиваю медиа для ранее выгруженных сообщений…"))
            self._pass(ch, ctx, st, st_path, d, media, write=False, dl=True,
                       after=cur("media_after"), until=int(st["after"]))
        if o.get("messages", True):
            self._pass(ch, ctx, st, st_path, d, media, write=True, dl=dl, after=cur("after"))

        self.log(_("  Готово: %d сообщений, вложений %d (%s по данным Discord).")
                 % (st["count"], st["atts"], mb(st["att_bytes"])))
        if dl:
            self.log(_("  Скачано вложений: %d (%s), недоступно: %d.") % (st["media_ok"], mb(st["media_bytes"]), st["media_fail"]))
        if render_now:
            self.render(d)

    def _pass(self, ch, ctx, st, st_path, d, media, write, dl, after, until=None):
        o = self.opt
        only = o.get("only_users")
        done_run, stop = 0, False
        empty_check = empty_count = 0
        last_print = 0
        conv_opt = {"avatars": o.get("avatars"), "emoji": o.get("emoji"), "stickers": o.get("stickers")}
        backlog = None
        first = True
        while True:
            if backlog is not None:
                batch, backlog = backlog[:100], backlog[100:]
            else:
                try:
                    batch = self.c.get("/channels/%s/messages?limit=100&after=%s" % (ch["id"], after))
                except ApiError as e:
                    if e.status == 403 or e.code == 50001:
                        self.log(_("  Нет доступа. Дай боту права «Просмотр канала» и «Читать историю сообщений»."))
                        return
                    raise
                if not batch and first and write and st["count"] == 0:
                    backlog = self._fallback(ch, after)
                    if backlog:
                        batch, backlog = backlog[:100], backlog[100:]
            first = False
            if not batch:
                break
            batch.sort(key=lambda m: int(m["id"]))
            lines, last_id = [], None
            for m in batch:
                if (o.get("to_ts") and snow_ts(m["id"]) > o["to_ts"]) or \
                        (o.get("limit") and done_run >= o["limit"]) or \
                        (until is not None and int(m["id"]) > until):
                    stop = True
                    break
                done_run += 1
                last_id = m["id"]
                if m.get("thread") and m["thread"].get("id"):
                    self._msg_threads[m["thread"]["id"]] = m["thread"]
                au = m.get("author") or {}
                if self.anon.excluded(au.get("id")) or (only and au.get("id") not in only):
                    continue
                ctx.media = []
                msg = convert(m, ctx, conv_opt)
                if write:
                    lines.append(json.dumps(msg, ensure_ascii=False, separators=(",", ":")))
                    st["count"] += 1
                    for a in m.get("attachments") or []:
                        st["atts"] += 1
                        st["att_bytes"] += a.get("size", 0)
                    if msg["k"] == 0 and empty_check < 300:
                        empty_check += 1
                        if not (msg.get("c") or msg.get("att") or msg.get("emb") or msg.get("st") or msg.get("pl")):
                            empty_count += 1
                if dl:
                    if o.get("attachments"):
                        for a in m.get("attachments") or []:
                            size = download(a.get("url", ""), os.path.join(media, msg_att_file(a)), self.c.cancel)
                            if size >= 0:
                                st["media_ok"] += 1
                                st["media_bytes"] += size
                            else:
                                st["media_fail"] += 1
                        for snap in m.get("message_snapshots") or []:
                            for a in (snap.get("message") or {}).get("attachments") or []:
                                download(a.get("url", ""), os.path.join(media, msg_att_file(a)), self.c.cancel)
                    for url, rel in ctx.media:
                        p = os.path.join(self.assets, *rel.split("/"))
                        if not os.path.exists(p) and download(url, p, self.c.cancel) >= 0:
                            st["assets_ok"] += 1
            if last_id is None:
                break
            if write and lines:
                path = os.path.join(d, "part-%04d.jsonl" % st["part"])
                if os.path.exists(path) and os.path.getsize(path) >= PART_BYTES:
                    st["part"] += 1
                    path = os.path.join(d, "part-%04d.jsonl" % st["part"])
                with open(path, "a", encoding="utf-8", newline="\n") as f:
                    f.write("\n".join(lines) + "\n")
            after = last_id
            if write:
                st["after"] = after
            if dl:
                st["media_after"] = after
            save_json(st_path, st)
            if stop:
                break
            if write and empty_check >= 300 and empty_count > 200:
                self.log(_("  ВНИМАНИЕ: у сообщений пустой текст. Включи боту Message Content Intent"
                         " (Developer Portal → Bot), удали папку %s и запусти заново.") % os.path.basename(d))
                return
            now = time.time()
            day = datetime.fromtimestamp(snow_ts(after), LOCAL_TZ).strftime("%d.%m.%Y")
            self.progress(channel=ch.get("name"), count=st["count"], day=day, media=st["media_ok"])
            if now - last_print > 5:
                last_print = now
                self.log(_("  %s сообщений, дошли до %s") % (format(st["count"], ",").replace(",", " "), day)
                         if write else _("  вложения: %d скачано (%s), дошли до %s") % (st["media_ok"], mb(st["media_bytes"]), day))


    def _fallback(self, ch, after):
        try:
            newest = self.c.get("/channels/%s/messages?limit=100" % ch["id"])
        except ApiError:
            newest = []
        if not newest:
            mc = ch.get("message_count") or ch.get("total_message_sent")
            self.log(_("  Discord вернул 0 сообщений%s. Если сообщения там есть — у бота нет права «Читать историю сообщений». "
                       "Для веток это право берётся из родительского канала/форума: проверь его настройки прав (и категории).")
                     % ((_(" (по данным Discord в ветке: %d)") % mc) if mc else ""))
            return []
        self.log(_("  Обычная загрузка вернула 0 сообщений, загружаю в обратном порядке…"))
        out = list(newest)
        while len(newest) == 100:
            oldest = min(newest, key=lambda m: int(m["id"]))["id"]
            if int(oldest) <= int(after):
                break
            newest = self.c.get("/channels/%s/messages?limit=100&before=%s" % (ch["id"], oldest))
            out.extend(newest)
        return sorted((m for m in out if int(m["id"]) > int(after)), key=lambda m: int(m["id"]))

    def server_assets(self, g):
        d = os.path.join(self.opt["out_dir"], "server-assets", "%s_%s" % (safe_name(g["name"]), g["id"]))
        self.log(_("\nЭмодзи и стикеры сервера «%s»…") % g["name"])
        manifest = {"guild": g["name"], "guild_id": g["id"], "emoji": [], "stickers": []}
        try:
            emojis = self.c.get("/guilds/%s/emojis" % g["id"])
        except ApiError:
            emojis = []
        for e in emojis:
            an = bool(e.get("animated"))
            fn = "%s_%s.%s" % (safe_name(e.get("name"), 32), e["id"], "gif" if an else "png")
            download("https://cdn.discordapp.com/emojis/%s.%s?size=128" % (e["id"], "gif" if an else "png"),
                     os.path.join(d, "emoji", fn), self.c.cancel)
            manifest["emoji"].append({"id": e["id"], "name": e.get("name"), "animated": an, "file": "emoji/" + fn})
        try:
            stickers = self.c.get("/guilds/%s/stickers" % g["id"])
        except ApiError:
            stickers = []
        for s in stickers:
            f = s.get("format_type", 1)
            ext = STICKER_EXT.get(f, "png")
            fn = "%s_%s.%s" % (safe_name(s.get("name"), 32), s["id"], ext)
            host = "https://media.discordapp.net" if f == 4 else "https://cdn.discordapp.com"
            download("%s/stickers/%s.%s" % (host, s["id"], ext), os.path.join(d, "stickers", fn), self.c.cancel)
            manifest["stickers"].append({"id": s["id"], "name": s.get("name"), "format": f,
                                         "description": s.get("description"), "tags": s.get("tags"),
                                         "file": "stickers/" + fn})
        os.makedirs(d, exist_ok=True)
        save_json(os.path.join(d, "manifest.json"), manifest)
        self.log(_("  эмодзи: %d, стикеров: %d → %s") % (len(emojis), len(stickers), d))

