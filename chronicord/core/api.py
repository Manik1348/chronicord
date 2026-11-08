import json
import os
import threading
import time
import urllib.error
import urllib.request

from .. import VERSION, REPO_URL
from ..i18n import _

API = "https://discord.com/api/v10"
CDN = "https://cdn.discordapp.com"
MEDIA = "https://media.discordapp.net"
UA = "DiscordBot (%s, %s)" % (REPO_URL, VERSION)


class Cancelled(Exception):
    pass


class ApiError(Exception):
    def __init__(self, status, body="", code=None):
        super().__init__("HTTP %s %s" % (status, body[:200]))
        self.status = status
        self.code = code


class Client:
    def __init__(self, token, cancel=None, log=None):
        self._token = token.strip()
        if self._token.lower().startswith("bot "):
            self._token = self._token[4:].strip()
        self.cancel = cancel or threading.Event()
        self.log = log or (lambda s: None)

    def __repr__(self):
        return "<Client>"

    def sleep(self, sec):
        if self.cancel.wait(max(0.0, sec)):
            raise Cancelled()

    def check(self):
        if self.cancel.is_set():
            raise Cancelled()

    def get(self, path):
        self.check()
        url = API + path
        for attempt in range(10):
            req = urllib.request.Request(url, headers={
                "Authorization": "Bot " + self._token, "User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.loads(r.read().decode("utf-8"))
                    if r.headers.get("X-RateLimit-Remaining") == "0":
                        self.sleep(float(r.headers.get("X-RateLimit-Reset-After") or 1))
                    return data
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", "replace")
                if e.code == 429:
                    try:
                        wait = float(json.loads(body).get("retry_after", 2))
                    except Exception:
                        wait = 2.0
                    self.sleep(wait + 0.3)
                    continue
                if e.code >= 500:
                    self.sleep(3 * (attempt + 1))
                    continue
                code = None
                try:
                    code = json.loads(body).get("code")
                except Exception:
                    pass
                raise ApiError(e.code, body, code)
            except OSError:
                self.log(_("Связь прервалась, повтор…"))
                self.sleep(5 * (attempt + 1))
        raise ApiError(0, _("нет связи с Discord"))


def download(url, path, cancel=None):
    if os.path.exists(path):
        return os.path.getsize(path)
    if not url:
        return -1
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".part"
    for attempt in range(5):
        if cancel is not None and cancel.is_set():
            raise Cancelled()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
                while True:
                    b = r.read(65536)
                    if not b:
                        break
                    f.write(b)
            os.replace(tmp, path)
            return os.path.getsize(path)
        except urllib.error.HTTPError as e:
            if e.code in (400, 403, 404, 410, 415):
                break
            time.sleep(3)
        except OSError:
            time.sleep(3 * (attempt + 1))
    if os.path.exists(tmp):
        try:
            os.remove(tmp)
        except OSError:
            pass
    return -1
