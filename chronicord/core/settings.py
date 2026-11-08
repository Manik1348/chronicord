import json
import os

from .. import APP_NAME

try:
    import keyring
except Exception:
    keyring = None

DIR = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~/.config"), APP_NAME)
PATH = os.path.join(DIR, "settings.json")

DEFAULTS = {
    "out_dir": os.path.join(os.path.expanduser("~"), "Documents", "Chronicord"),
    "formats": ["json", "html"],
    "attachments": True, "avatars": True, "emoji": True, "stickers": True,
    "threads": True, "private_threads": False, "server_assets": False,
    "remember_token": False,
    "profiles": {},
    "anon_rules": {},
}


def load():
    s = dict(DEFAULTS)
    try:
        with open(PATH, encoding="utf-8") as f:
            s.update(json.load(f))
    except (OSError, ValueError):
        pass
    return s


def save(s):
    os.makedirs(DIR, exist_ok=True)
    data = {k: v for k, v in s.items() if k != "token"}
    tmp = PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, PATH)


def get_token():
    if keyring is None:
        return ""
    try:
        return keyring.get_password(APP_NAME, "bot_token") or ""
    except Exception:
        return ""


def set_token(token):
    if keyring is None:
        return False
    try:
        if token:
            keyring.set_password(APP_NAME, "bot_token", token)
        else:
            keyring.delete_password(APP_NAME, "bot_token")
        return True
    except Exception:
        return False
