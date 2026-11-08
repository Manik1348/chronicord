import os
import re
from datetime import datetime

from ..i18n import _

RE_USER = re.compile(r"<@!?(\d+)>")
RE_ROLE = re.compile(r"<@&(\d+)>")
RE_CHAN = re.compile(r"<#(\d+)>")
RE_EMOJI = re.compile(r"<(a?):(\w+):(\d+)>")
RE_TIME = re.compile(r"<t:(-?\d+)(?::[tTdDfFR])?>")
RE_CMD = re.compile(r"</([^:>]+):\d+>")

LOCAL_TZ = datetime.now().astimezone().tzinfo
HIDDEN_NAME = "Скрытый пользователь"

STICKER_EXT = {1: "png", 2: "png", 3: "json", 4: "gif"}


def snow_ts(sid):
    return ((int(sid) >> 22) + 1420070400000) // 1000


def ts_snow(ts):
    return str(max(0, (int(ts) * 1000 - 1420070400000) << 22))


class Anonymizer:

    def __init__(self, rules=None):
        self.rules = {str(k): v for k, v in (rules or {}).items()}
        self._alias = {}

    def rule(self, uid):
        return self.rules.get(str(uid))

    def excluded(self, uid):
        r = self.rule(uid)
        return bool(r and r.get("mode") == "exclude")

    def alias_id(self, uid):
        if uid not in self._alias:
            self._alias[uid] = "anon-%d" % (len(self._alias) + 1)
        return self._alias[uid]

    def apply(self, uid, name):
        r = self.rule(uid)
        if not r:
            return uid, name, True
        if r.get("mode") == "rename" and r.get("name"):
            return self.alias_id(uid), r["name"], bool(r.get("keep_avatar"))
        return self.alias_id(uid), _(HIDDEN_NAME), False


class Ctx:

    def __init__(self, client, guild_id, roles, chans, anon=None):
        self.client = client
        self.guild = guild_id
        self.roles = roles
        self.chans = chans
        self.anon = anon or Anonymizer()
        self.nicks = {}
        self.media = []

    def raw_name(self, u):
        uid = u.get("id")
        if u.get("bot") or not uid:
            return u.get("username") or "unknown"
        if uid not in self.nicks:
            nick = (u.get("member") or {}).get("nick")
            if nick is None and self.client is not None:
                try:
                    nick = self.client.get("/guilds/%s/members/%s" % (self.guild, uid)).get("nick")
                except Exception as e:
                    if type(e).__name__ == "Cancelled":
                        raise
                    nick = None
            self.nicks[uid] = nick
        return self.nicks[uid] or u.get("global_name") or u.get("username") or "unknown"

    def user(self, u, want_avatar=True):
        uid = u.get("id")
        hook = bool(u.get("_webhook"))
        name = u.get("username", "unknown") if hook else self.raw_name(u)
        uid2, name, show_av = self.anon.apply(uid, name)
        o = {"id": uid2, "n": name}
        if u.get("bot") or hook:
            o["bot"] = 1
        if hook:
            o["wh"] = 1
        if want_avatar and show_av and u.get("avatar") and uid:
            ext = "gif" if u["avatar"].startswith("a_") else "png"
            rel = "avatars/%s_%s.%s" % (uid, u["avatar"][:12], ext)
            self.media.append(("https://cdn.discordapp.com/avatars/%s/%s.%s?size=128"
                               % (uid, u["avatar"], ext), rel))
            o["av"] = rel
        return o

    def mention_name(self, uid, mentions):
        for u in mentions:
            if u.get("id") == uid:
                return self.user(u, want_avatar=False)["n"]
        return self.anon.apply(uid, "unknown")[1]


def emoji_rel(eid, animated):
    return "emoji/%s.%s" % (eid, "gif" if animated else "png")


def emoji_url(eid, animated):
    return "https://cdn.discordapp.com/emojis/%s.%s?size=96" % (eid, "gif" if animated else "png")


def text(s, m, ctx, em=None):
    if not s:
        return ""
    mentions = m.get("mentions") or []
    s = RE_USER.sub(lambda x: "@" + ctx.mention_name(x.group(1), mentions), s)
    s = RE_ROLE.sub(lambda x: "@" + ctx.roles.get(x.group(1), _("роль")), s)
    s = RE_CHAN.sub(lambda x: "#" + ctx.chans.get(x.group(1), _("канал")), s)

    def emo(x):
        an, name, eid = x.group(1) == "a", x.group(2), x.group(3)
        if em is not None and not any(e["id"] == eid for e in em):
            em.append({"id": eid, "n": name, "an": 1 if an else 0, "file": emoji_rel(eid, an)})
            ctx.media.append((emoji_url(eid, an), emoji_rel(eid, an)))
        return ":%s:" % name
    s = RE_EMOJI.sub(emo, s)
    s = RE_TIME.sub(lambda x: datetime.fromtimestamp(int(x.group(1)), LOCAL_TZ).strftime("%d.%m.%Y %H:%M"), s)
    s = RE_CMD.sub(lambda x: "/" + x.group(1), s)
    return s


def att_file(a):
    ext = os.path.splitext(a.get("filename") or "")[1].lower()
    if not re.fullmatch(r"\.[a-z0-9]{1,8}", ext):
        ext = ""
    return a["id"] + ext


def atts(m):
    out = []
    for a in m.get("attachments") or []:
        x = {"id": a["id"], "fn": a.get("filename", ""), "sz": a.get("size", 0), "file": att_file(a)}
        for k, kk in (("width", "w"), ("height", "h"), ("content_type", "ct")):
            if a.get(k):
                x[kk] = a[k]
        out.append(x)
    return out


def embeds(m, ctx, em):
    out = []
    for e in m.get("embeds") or []:
        x = {}
        if e.get("title"): x["t"] = text(e["title"], m, ctx, em)
        if e.get("description"): x["d"] = text(e["description"], m, ctx, em)
        if (e.get("author") or {}).get("name"): x["au"] = e["author"]["name"]
        if (e.get("footer") or {}).get("text"): x["ft"] = e["footer"]["text"]
        if e.get("url"): x["u"] = e["url"]
        if e.get("color") is not None: x["col"] = e["color"]
        img = (e.get("image") or e.get("thumbnail") or {}).get("url")
        if img: x["img"] = img
        if e.get("fields"):
            x["f"] = [[text(f.get("name", ""), m, ctx, em), text(f.get("value", ""), m, ctx, em)]
                      for f in e["fields"]]
        if x:
            out.append(x)
    return out


def reaction(r, ctx, dl_emoji):
    e = r.get("emoji") or {}
    if not e.get("id"):
        return {"e": e.get("name") or "?", "n": r.get("count", 0)}
    an = bool(e.get("animated"))
    o = {"e": ":%s:" % (e.get("name") or "emoji"), "n": r.get("count", 0), "id": e["id"], "an": 1 if an else 0}
    if dl_emoji:
        o["file"] = emoji_rel(e["id"], an)
        ctx.media.append((emoji_url(e["id"], an), o["file"]))
    return o


def poll(p, ctx, dl_emoji):
    res = {}
    for c in ((p.get("results") or {}).get("answer_counts") or []):
        res[c.get("id")] = c.get("count", 0)
    ans = []
    for a in p.get("answers") or []:
        md = a.get("poll_media") or {}
        x = {"t": md.get("text") or "", "n": res.get(a.get("answer_id"), 0)}
        e = md.get("emoji") or {}
        if e.get("id"):
            x["e"] = ":%s:" % e.get("name", "emoji")
            if dl_emoji:
                x["file"] = emoji_rel(e["id"], bool(e.get("animated")))
                ctx.media.append((emoji_url(e["id"], bool(e.get("animated"))), x["file"]))
        elif e.get("name"):
            x["e"] = e["name"]
        ans.append(x)
    o = {"q": (p.get("question") or {}).get("text") or "", "ans": ans}
    if p.get("allow_multiselect"): o["multi"] = 1
    if p.get("expiry"): o["exp"] = p["expiry"]
    if (p.get("results") or {}).get("is_finalized"): o["fin"] = 1
    return o


def convert(m, ctx, opt):
    a = dict(m.get("author") or {})
    if m.get("webhook_id"):
        a["_webhook"] = True
    em = [] if opt.get("emoji") else None
    o = {"id": m["id"], "ts": snow_ts(m["id"]), "k": m.get("type", 0),
         "a": ctx.user(a, want_avatar=opt.get("avatars", True))}
    c = text(m.get("content", ""), m, ctx, em)
    if c: o["c"] = c
    if m.get("edited_timestamp"): o["ed"] = 1
    if m.get("pinned"): o["pin"] = 1
    ref = m.get("message_reference") or {}
    if m.get("type") == 19 and ref.get("message_id"): o["rp"] = ref["message_id"]
    fw = []
    for snap in m.get("message_snapshots") or []:
        sm = snap.get("message") or {}
        f = {"c": text(sm.get("content", ""), sm, ctx, em)}
        if atts(sm): f["att"] = atts(sm)
        fw.append(f)
    if fw: o["fwd"] = fw
    x = atts(m)
    if x: o["att"] = x
    x = embeds(m, ctx, em)
    if x: o["emb"] = x
    stk = []
    for s in m.get("sticker_items") or []:
        f = s.get("format_type", 1)
        y = {"id": s.get("id"), "n": s.get("name") or "sticker", "f": f}
        if opt.get("stickers") and s.get("id"):
            ext = STICKER_EXT.get(f, "png")
            y["file"] = "stickers/%s.%s" % (s["id"], ext)
            host = "https://media.discordapp.net" if f == 4 else "https://cdn.discordapp.com"
            ctx.media.append(("%s/stickers/%s.%s" % (host, s["id"], ext), y["file"]))
        stk.append(y)
    if stk:
        o["st"] = [s["n"] for s in stk]
        o["stk"] = stk
    x = [reaction(r, ctx, opt.get("emoji")) for r in m.get("reactions") or []]
    if x: o["rx"] = x
    if m.get("poll"):
        o["pl"] = poll(m["poll"], ctx, opt.get("emoji"))
        if o["pl"]["q"]:
            o["poll"] = o["pl"]["q"]
    if m.get("thread"):
        o["th"] = {"id": m["thread"].get("id"), "n": m["thread"].get("name", "")}
    if em:
        o["em"] = em
    return o
