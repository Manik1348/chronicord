import os
import sys
import threading
import traceback
from datetime import datetime, time as dtime

from PySide6.QtCore import Qt, QThread, Signal, QDate, QUrl, QLocale
from PySide6.QtGui import QDesktopServices, QIcon, QPalette, QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QTabWidget, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QComboBox, QHeaderView, QGroupBox, QDateEdit, QSpinBox, QFileDialog, QPlainTextEdit, QProgressBar,
    QMessageBox, QDialog, QListWidget, QListWidgetItem, QDialogButtonBox, QInputDialog, QRadioButton,
    QAbstractItemView, QTextBrowser)

from . import APP_NAME, VERSION, REPO_URL, i18n
from .i18n import _
from .core import settings
from .core.api import Client, ApiError, Cancelled
from .core.exporter import Exporter, TEXT_TYPES, FORUM_TYPES, VOICE_TYPES

ICON = {0: "#", 5: "📢", 15: "💬", 16: "🖼", 2: "🔊", 13: "🎙"}
MODES = [("rename", "Заменить ник"), ("hide", "Скрыть ник"), ("exclude", "Исключить сообщения")]

HELP = """<h3>Как подключить бота</h3><ol>
<li>Открой <a href="https://discord.com/developers/applications">discord.com/developers/applications</a> → <b>New Application</b>.</li>
<li>Вкладка <b>Bot</b> → <b>Reset Token</b> → скопируй токен и вставь в программу.</li>
<li>Там же включи <b>Message Content Intent</b> (без него текст сообщений будет пустым).
 Для выбора пользователей из списка включи ещё <b>Server Members Intent</b>.</li>
<li>Вкладка <b>OAuth2 → URL Generator</b>: scope <b>bot</b>, права <b>View Channels</b>, <b>Read Message History</b>
 (для закрытых архивных веток — ещё <b>Manage Threads</b>). Открой ссылку и добавь бота на сервер.</li></ol>
<h3>Безопасность</h3><p>Токен уходит только на discord.com. Программа не отправляет данные никуда ещё,
не собирает статистику и не требует токен твоего аккаунта (это запрещено правилами Discord).
Если включено «Запомнить», токен хранится в Диспетчере учётных данных Windows.</p>"""


def dark(app):
    app.setStyle("Fusion")
    p = QPalette()
    for role, c in ((QPalette.Window, "#2b2d31"), (QPalette.WindowText, "#dbdee1"), (QPalette.Base, "#1e1f22"),
                    (QPalette.AlternateBase, "#26282c"), (QPalette.Text, "#dbdee1"), (QPalette.Button, "#383a40"),
                    (QPalette.ButtonText, "#dbdee1"), (QPalette.Highlight, "#5865f2"), (QPalette.HighlightedText, "#ffffff"),
                    (QPalette.ToolTipBase, "#111214"), (QPalette.ToolTipText, "#dbdee1"), (QPalette.Link, "#00a8fc"),
                    (QPalette.PlaceholderText, "#80848e")):
        p.setColor(role, QColor(c))
    p.setColor(QPalette.Disabled, QPalette.Text, QColor("#6d6f78"))
    p.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#6d6f78"))
    app.setPalette(p)
    chk = resource("assets/check.png").replace("\\", "/")
    part = resource("assets/partial.png").replace("\\", "/")
    app.setStyleSheet("""
        QPushButton{padding:6px 14px;border-radius:4px;background:#4e5058}
        QPushButton:hover{background:#6d6f78} QPushButton:disabled{background:#3a3c42;color:#6d6f78}
        QPushButton#primary{background:#5865f2;color:white;font-weight:600} QPushButton#primary:hover{background:#4752c4}
        QPushButton#danger{background:#da373c;color:white}
        QGroupBox{border:1px solid #3f4147;border-radius:6px;margin-top:12px;padding-top:8px}
        QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 4px;color:#b5bac1}
        QCheckBox::indicator,QRadioButton::indicator,QTreeView::indicator{width:14px;height:14px;border:1px solid #80848e;border-radius:3px;background:#1e1f22}
        QRadioButton::indicator{border-radius:8px}
        QCheckBox::indicator:checked,QTreeView::indicator:checked{background:#23a55a;border-color:#23a55a;image:url(%CHK%)}
        QRadioButton::indicator:checked{background:#23a55a;border:3px solid #1e1f22;border-radius:8px}
        QTreeView::indicator:indeterminate{background:#4e5058;border-color:#80848e;image:url(%PART%)}
        QCheckBox::indicator:checked:disabled{background:#1a6e3e;border-color:#1a6e3e}
        QTreeView,QTableView,QListView{selection-background-color:#404249;selection-color:#ffffff}
        QTabBar::tab{padding:8px 18px} QLineEdit,QSpinBox,QDateEdit,QComboBox{padding:4px}
    """.replace("%CHK%", chk).replace("%PART%", part))


class Worker(QThread):
    log = Signal(str)
    fail = Signal(str)
    ok = Signal(object)
    prog = Signal(dict)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn
        self.cancel = threading.Event()

    def run(self):
        try:
            self.ok.emit(self.fn(self))
        except Cancelled:
            self.fail.emit("__cancelled__")
        except ApiError as e:
            if e.status == 401:
                self.fail.emit(_("Токен не подошёл. Проверь, что это токен бота из Developer Portal → Bot."))
            elif e.code == 50001 or e.status == 403:
                self.fail.emit(_("Нет доступа (%s). Проверь права бота.") % e.status)
            else:
                self.fail.emit(_("Ошибка Discord: %s") % e)
        except Exception as e:
            self.log.emit(traceback.format_exc())
            self.fail.emit(_("Ошибка: %s") % e)


class MembersDialog(QDialog):
    def __init__(self, parent, members):
        super().__init__(parent)
        self.setWindowTitle(_("Выбор пользователей"))
        self.resize(420, 520)
        lay = QVBoxLayout(self)
        self.q = QLineEdit(placeholderText=_("Поиск по нику или ID…"))
        self.lst = QListWidget()
        self.lst.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for uid, name in sorted(members.items(), key=lambda x: x[1].lower()):
            it = QListWidgetItem("%s   (%s)" % (name, uid))
            it.setData(Qt.UserRole, (uid, name))
            self.lst.addItem(it)
        self.q.textChanged.connect(self.filter)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        lay.addWidget(self.q)
        lay.addWidget(self.lst)
        lay.addWidget(QLabel(_("Ctrl/Shift — выбрать несколько")))
        lay.addWidget(bb)

    def filter(self, t):
        t = t.lower()
        for i in range(self.lst.count()):
            it = self.lst.item(i)
            it.setHidden(t not in it.text().lower())

    def chosen(self):
        return [it.data(Qt.UserRole) for it in self.lst.selectedItems()]


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.s = settings.load()
        self.worker = None
        self.guilds = []
        self.members = {}
        self.setWindowTitle(_("%s %s — архив чатов Discord") % (APP_NAME, VERSION))
        self.resize(980, 720)
        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)

        top = QHBoxLayout()
        self.token = QLineEdit(placeholderText=_("Токен бота (Developer Portal → Bot → Reset Token)"))
        self.token.setEchoMode(QLineEdit.Password)
        self.show_tok = QCheckBox(_("Показать"))
        self.show_tok.toggled.connect(lambda on: self.token.setEchoMode(QLineEdit.Normal if on else QLineEdit.Password))
        self.remember = QCheckBox(_("Запомнить"))
        self.remember.setToolTip(_("Хранить токен в Диспетчере учётных данных Windows"))
        self.remember.setChecked(self.s.get("remember_token", False))
        if self.remember.isChecked():
            self.token.setText(settings.get_token())
        self.btn_connect = QPushButton(_("Подключиться"), objectName="primary")
        self.btn_connect.clicked.connect(self.connect)
        hb = QPushButton(_("Как создать бота?"))
        hb.clicked.connect(self.help)
        self.lang = QComboBox()
        for code, name in i18n.LANGS:
            self.lang.addItem(name, code)
        self.lang.setCurrentIndex(max(0, self.lang.findData(i18n.LANG)))
        self.lang.currentIndexChanged.connect(self.change_lang)
        for w in (QLabel(_("Токен:")), self.token, self.show_tok, self.remember, self.btn_connect, hb,
                  QLabel(_("Язык:")), self.lang):
            top.addWidget(w)
        v.addLayout(top)
        self.status = QLabel(_("Не подключено"))
        v.addWidget(self.status)

        self.tabs = QTabWidget()
        v.addWidget(self.tabs, 1)
        self.tabs.addTab(self.tab_channels(), _("1. Каналы"))
        self.tabs.addTab(self.tab_users(), _("2. Пользователи"))
        self.tabs.addTab(self.tab_options(), _("3. Настройки"))
        self.tabs.addTab(self.tab_run(), _("4. Выгрузка"))


    def tab_channels(self):
        w = QWidget()
        v = QVBoxLayout(w)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([_("Сервер / канал"), "ID"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        v.addWidget(self.tree)
        h = QHBoxLayout()
        for text, state in ((_("Выбрать все"), Qt.Checked), (_("Снять все"), Qt.Unchecked)):
            b = QPushButton(text)
            b.clicked.connect(lambda _=False, st=state: self.check_all(st))
            h.addWidget(b)
        h.addStretch()
        h.addWidget(QLabel(_("Пункт «★ Эмодзи и стикеры» выгружает весь набор сервера.")))
        v.addLayout(h)
        return w

    def tab_users(self):
        w = QWidget()
        v = QVBoxLayout(w)
        g1 = QGroupBox(_("Чьи сообщения выгружать"))
        l1 = QVBoxLayout(g1)
        self.r_all = QRadioButton(_("Всех пользователей"))
        self.r_only = QRadioButton(_("Только выбранных:"))
        self.r_all.setChecked(True)
        self.only_list = QListWidget()
        self.only_list.setMaximumHeight(120)
        h = QHBoxLayout()
        for text, fn in ((_("Добавить по ID"), self.only_add_id), (_("Выбрать из участников"), self.only_pick),
                         (_("Удалить"), lambda: [self.only_list.takeItem(self.only_list.row(i)) for i in self.only_list.selectedItems()])):
            b = QPushButton(text)
            b.clicked.connect(fn)
            h.addWidget(b)
        h.addStretch()
        for x in (self.r_all, self.r_only, self.only_list):
            l1.addWidget(x)
        l1.addLayout(h)
        v.addWidget(g1)

        g2 = QGroupBox(_("Замена и скрытие ников (применяется к автору, упоминаниям @ник и ответам)"))
        l2 = QVBoxLayout(g2)
        self.anon = QTableWidget(0, 5)
        self.anon.setHorizontalHeaderLabels([_("ID пользователя"), _("Имя"), _("Действие"), _("Новый ник"), _("Оставить аватар")])
        self.anon.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.anon.verticalHeader().hide()
        l2.addWidget(self.anon)
        h = QHBoxLayout()
        for text, fn in ((_("Добавить по ID"), self.anon_add_id), (_("Выбрать из участников"), self.anon_pick),
                         (_("Удалить строку"), self.anon_del)):
            b = QPushButton(text)
            b.clicked.connect(fn)
            h.addWidget(b)
        h.addStretch()
        l2.addLayout(h)
        l2.addWidget(QLabel(_("ID скопируешь в Discord: Настройки → Расширенные → Режим разработчика, затем ПКМ по пользователю → «Копировать ID».\n"
                            "У скрытых и переименованных пользователей ID в архиве тоже заменяется (anon-1, anon-2…).")))
        v.addWidget(g2, 1)
        for uid, r in (self.s.get("anon_rules") or {}).items():
            self.anon_row(uid, r.get("orig", ""), r)
        return w

    def tab_options(self):
        w = QWidget()
        g = QGridLayout(w)
        gp = QGroupBox(_("Период и количество"))
        lp = QGridLayout(gp)
        self.use_from = QCheckBox(_("С даты:"))
        self.use_to = QCheckBox(_("По дату (включительно):"))
        self.d_from = QDateEdit(QDate.currentDate().addYears(-1), calendarPopup=True)
        self.d_to = QDateEdit(QDate.currentDate(), calendarPopup=True)
        for d in (self.d_from, self.d_to):
            d.setDisplayFormat("dd.MM.yyyy")
        self.limit = QSpinBox(maximum=10_000_000, specialValueText=_("все"))
        lp.addWidget(self.use_from, 0, 0); lp.addWidget(self.d_from, 0, 1)
        lp.addWidget(self.use_to, 1, 0); lp.addWidget(self.d_to, 1, 1)
        lp.addWidget(QLabel(_("Максимум сообщений с канала:")), 2, 0); lp.addWidget(self.limit, 2, 1)
        lp.addWidget(QLabel(_("Выгрузка с периодом/лимитом сохраняется в отдельную папку.")), 3, 0, 1, 2)
        g.addWidget(gp, 0, 0)
        gm = QGroupBox(_("Медиа"))
        lm = QVBoxLayout(gm)
        self.o_att = QCheckBox(_("Вложения (картинки, видео, файлы)"))
        self.o_av = QCheckBox(_("Аватарки пользователей"))
        self.o_em = QCheckBox(_("Кастомные эмодзи из сообщений и реакций"))
        self.o_st = QCheckBox(_("Стикеры из сообщений"))
        for c in (self.o_att, self.o_av, self.o_em, self.o_st):
            lm.addWidget(c)
        lm.addWidget(QLabel(_("Ссылки Discord на файлы со временем истекают —\nлучше скачивать сразу.")))
        g.addWidget(gm, 0, 1)
        gt = QGroupBox(_("Ветки и форумы"))
        lt = QVBoxLayout(gt)
        self.o_th = QCheckBox(_("Выгружать ветки выбранных каналов (активные и архивные)"))
        self.o_pth = QCheckBox(_("Включая закрытые архивные (нужно право «Управлять ветками»)"))
        lt.addWidget(self.o_th); lt.addWidget(self.o_pth)
        lt.addWidget(QLabel(_("Форумы выгружаются всегда вместе с ветками.")))
        g.addWidget(gt, 1, 0)
        gf = QGroupBox(_("Форматы"))
        lf = QVBoxLayout(gf)
        self.fmt = {}
        for k, t in (("json", _("JSON — для своего сайта (всегда сохраняется)")), ("html", _("HTML — готовый просмотр с поиском")),
                     ("txt", _("TXT — простой текст")), ("csv", _("CSV — для Excel"))):
            c = QCheckBox(t)
            self.fmt[k] = c
            lf.addWidget(c)
        self.fmt["json"].setChecked(True)
        self.fmt["json"].setEnabled(False)
        g.addWidget(gf, 1, 1)
        go = QGroupBox(_("Папка для архива"))
        lo = QHBoxLayout(go)
        self.out = QLineEdit(self.s["out_dir"])
        b = QPushButton(_("Обзор…"))
        b.clicked.connect(lambda: self.out.setText(QFileDialog.getExistingDirectory(self, _("Папка"), self.out.text()) or self.out.text()))
        lo.addWidget(self.out); lo.addWidget(b)
        g.addWidget(go, 2, 0, 1, 2)
        g.setRowStretch(3, 1)
        s = self.s
        for c, k in ((self.o_att, "attachments"), (self.o_av, "avatars"), (self.o_em, "emoji"), (self.o_st, "stickers"),
                     (self.o_th, "threads"), (self.o_pth, "private_threads")):
            c.setChecked(bool(s.get(k)))
        for k in s.get("formats", []):
            if k in self.fmt:
                self.fmt[k].setChecked(True)
        return w

    def tab_run(self):
        w = QWidget()
        v = QVBoxLayout(w)
        h = QHBoxLayout()
        self.btn_start = QPushButton(_("▶ Начать выгрузку"), objectName="primary")
        self.btn_start.clicked.connect(self.start)
        self.btn_stop = QPushButton(_("■ Остановить"), objectName="danger")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop)
        b1 = QPushButton(_("Открыть папку"))
        b1.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(self.out.text())))
        b2 = QPushButton(_("Открыть архив в браузере"))
        b2.clicked.connect(self.open_html)
        for b in (self.btn_start, self.btn_stop):
            h.addWidget(b)
        h.addStretch()
        h.addWidget(b1); h.addWidget(b2)
        v.addLayout(h)
        self.bar = QProgressBar()
        self.bar.setRange(0, 1)
        self.bar.setTextVisible(False)
        self.prog = QLabel("")
        v.addWidget(self.bar)
        v.addWidget(self.prog)
        self.logw = QPlainTextEdit(readOnly=True)
        self.logw.setFont(QFont("Consolas", 9))
        v.addWidget(self.logw, 1)
        v.addWidget(QLabel(_("Выгрузку можно остановить в любой момент — при следующем запуске она продолжится с того же места.")))
        return w


    def help(self):
        d = QDialog(self)
        d.setWindowTitle(_("Справка"))
        d.resize(620, 460)
        l = QVBoxLayout(d)
        t = QTextBrowser(openExternalLinks=True)
        t.setHtml((HELP if i18n.LANG == "ru" else i18n.HELP_EN) + _('<p>%s %s · <a href="%s">%s</a> · лицензия MIT</p>') % (APP_NAME, VERSION, REPO_URL, REPO_URL))
        l.addWidget(t)
        d.exec()

    def client(self, cancel=None):
        return Client(self.token.text(), cancel=cancel)

    def run_bg(self, fn, ok, busy_text):
        if self.worker and self.worker.isRunning():
            return False
        self.worker = Worker(fn)
        self.worker.ok.connect(ok)
        self.worker.fail.connect(self.on_fail)
        self.worker.log.connect(self.append_log)
        self.worker.prog.connect(self.on_prog)
        self.worker.finished.connect(self.idle)
        self.status.setText(busy_text)
        self.set_busy(True)
        self.worker.start()
        return True

    def set_busy(self, on):
        self.btn_connect.setEnabled(not on)
        self.btn_start.setEnabled(not on)
        self.btn_stop.setEnabled(on)
        self.bar.setRange(0, 0 if on else 1)

    def idle(self):
        self.set_busy(False)

    def on_fail(self, msg):
        if msg == "__cancelled__":
            self.append_log(_("\nОстановлено. При следующем запуске выгрузка продолжится с того же места."))
            self.status.setText(_("Остановлено"))
            return
        self.status.setText(msg)
        self.append_log(msg)
        QMessageBox.warning(self, APP_NAME, msg)

    def connect(self):
        if not self.token.text().strip():
            QMessageBox.information(self, APP_NAME, _("Вставь токен бота."))
            return

        def job(wk):
            c = Client(self.token.text(), cancel=wk.cancel)
            me = c.get("/users/@me")
            out = []
            for g in c.get("/users/@me/guilds"):
                out.append((g, c.get("/guilds/%s/channels" % g["id"])))
            return me, out
        self.run_bg(job, self.connected, _("Подключаюсь…"))

    def connected(self, res):
        me, guilds = res
        self._me = me
        self.guilds = guilds
        if self.remember.isChecked():
            settings.set_token(self.token.text().strip())
        self.status.setText(_("Бот: %s · серверов: %d") % (me.get("username"), len(guilds)))
        self.tree.blockSignals(True)
        self.tree.clear()
        for g, chans in guilds:
            gi = QTreeWidgetItem(self.tree, [g["name"], g["id"]])
            gi.setFlags(gi.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate)
            gi.setCheckState(0, Qt.Unchecked)
            gi.setData(0, Qt.UserRole, ("guild", g))
            a = QTreeWidgetItem(gi, [_("★ Эмодзи и стикеры сервера"), ""])
            a.setFlags(a.flags() | Qt.ItemIsUserCheckable)
            a.setCheckState(0, Qt.Unchecked)
            a.setData(0, Qt.UserRole, ("assets", g))
            cats = {c["id"]: c for c in chans if c.get("type") == 4}
            catitems = {}
            ok_types = TEXT_TYPES + FORUM_TYPES + VOICE_TYPES
            for c in sorted(chans, key=lambda c: (cats.get(c.get("parent_id"), {}).get("position", -1),
                                                    c.get("type") in VOICE_TYPES, c.get("position", 0))):
                if c.get("type") not in ok_types:
                    continue
                pid = c.get("parent_id")
                parent = gi
                if pid in cats:
                    if pid not in catitems:
                        ci = QTreeWidgetItem(gi, [cats[pid]["name"].upper(), ""])
                        ci.setFlags(ci.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate)
                        ci.setCheckState(0, Qt.Unchecked)
                        ci.setExpanded(True)
                        catitems[pid] = ci
                    parent = catitems[pid]
                it = QTreeWidgetItem(parent, ["%s %s" % (ICON.get(c["type"], "#"), c["name"]), c["id"]])
                it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
                it.setCheckState(0, Qt.Unchecked)
                it.setData(0, Qt.UserRole, ("chan", c))
            gi.setExpanded(True)
        self.tree.blockSignals(False)
        if not guilds:
            QMessageBox.information(self, APP_NAME, _("Бот не состоит ни на одном сервере. Добавь его по ссылке из OAuth2 → URL Generator."))

    def check_all(self, st):
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setCheckState(0, st)

    def selection(self):
        sel = []
        for i in range(self.tree.topLevelItemCount()):
            gi = self.tree.topLevelItem(i)
            g = gi.data(0, Qt.UserRole)[1]
            item = {"guild": g, "channels": [], "server_assets": False}
            stack = [gi.child(k) for k in range(gi.childCount())]
            while stack:
                it = stack.pop(0)
                d = it.data(0, Qt.UserRole)
                if d is None:
                    stack[0:0] = [it.child(k) for k in range(it.childCount())]
                elif it.checkState(0) == Qt.Checked:
                    if d[0] == "assets":
                        item["server_assets"] = True
                    elif d[0] == "chan":
                        item["channels"].append(d[1])
            if item["channels"] or item["server_assets"]:
                sel.append(item)
        return sel


    def ask_id(self):
        uid, ok = QInputDialog.getText(self, _("ID пользователя"), _("ID (число из 17–20 цифр):"))
        uid = (uid or "").strip()
        if ok and uid:
            if not uid.isdigit():
                QMessageBox.warning(self, APP_NAME, _("ID — это число. Включи режим разработчика в Discord и скопируй ID."))
                return None
            return uid
        return None

    def load_members(self, then):
        guilds = [g for g, _ in self.guilds]
        if not guilds:
            QMessageBox.information(self, APP_NAME, _("Сначала подключись."))
            return
        sel = [s["guild"]["id"] for s in self.selection()] or [g["id"] for g in guilds]

        def job(wk):
            c = Client(self.token.text(), cancel=wk.cancel)
            ex = Exporter(c, {"out_dir": "."})
            res = {}
            for gid in sel:
                for m in ex.members(gid):
                    u = m.get("user") or {}
                    res[u["id"]] = m.get("nick") or u.get("global_name") or u.get("username")
            return res

        def done(res):
            self.status.setText(_("Участников: %d") % len(res))
            self.members.update(res)
            d = MembersDialog(self, res)
            if d.exec():
                then(d.chosen())

        if not self.run_bg(job, done, _("Загружаю участников…")):
            return
        self.worker.fail.disconnect()
        self.worker.fail.connect(lambda m: self.on_fail(
            _("Не удалось получить участников. Включи боту Server Members Intent (Developer Portal → Bot) "
            "или добавляй по ID.\n\n") + m) if m != "__cancelled__" else None)

    def only_add_id(self):
        uid = self.ask_id()
        if uid:
            self.only_list.addItem(uid)
            self.r_only.setChecked(True)

    def only_pick(self):
        def add(lst):
            for uid, name in lst:
                it = QListWidgetItem("%s  (%s)" % (name, uid))
                it.setData(Qt.UserRole, uid)
                self.only_list.addItem(it)
            if lst:
                self.r_only.setChecked(True)
        self.load_members(add)

    def anon_row(self, uid, name="", rule=None):
        rule = rule or {}
        for r in range(self.anon.rowCount()):
            if self.anon.item(r, 0).text() == uid:
                return
        r = self.anon.rowCount()
        self.anon.insertRow(r)
        it = QTableWidgetItem(uid)
        it.setFlags(it.flags() & ~Qt.ItemIsEditable)
        self.anon.setItem(r, 0, it)
        it = QTableWidgetItem(name)
        it.setFlags(it.flags() & ~Qt.ItemIsEditable)
        self.anon.setItem(r, 1, it)
        cb = QComboBox()
        for k, t in MODES:
            cb.addItem(_(t), k)
        cb.setCurrentIndex(max(0, [k for k, _ in MODES].index(rule.get("mode", "rename"))))
        self.anon.setCellWidget(r, 2, cb)
        self.anon.setItem(r, 3, QTableWidgetItem(rule.get("name", "")))
        box = QWidget()
        bl = QHBoxLayout(box)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setAlignment(Qt.AlignCenter)
        ch = QCheckBox()
        ch.setChecked(bool(rule.get("keep_avatar")))
        bl.addWidget(ch)
        self.anon.setCellWidget(r, 4, box)

    def anon_add_id(self):
        uid = self.ask_id()
        if uid:
            self.anon_row(uid, self.members.get(uid, ""))

    def anon_pick(self):
        self.load_members(lambda lst: [self.anon_row(uid, name) for uid, name in lst])

    def anon_del(self):
        for r in sorted({i.row() for i in self.anon.selectedIndexes()} | {self.anon.currentRow()}, reverse=True):
            if r >= 0:
                self.anon.removeRow(r)

    def anon_rules(self):
        rules = {}
        for r in range(self.anon.rowCount()):
            uid = self.anon.item(r, 0).text()
            rules[uid] = {"mode": self.anon.cellWidget(r, 2).currentData(),
                          "name": (self.anon.item(r, 3).text() if self.anon.item(r, 3) else "").strip(),
                          "keep_avatar": self.anon.cellWidget(r, 4).findChild(QCheckBox).isChecked(),
                          "orig": self.anon.item(r, 1).text()}
        return rules


    def collect(self):
        s = self.s
        s.update({"out_dir": self.out.text().strip(), "attachments": self.o_att.isChecked(), "avatars": self.o_av.isChecked(),
                  "emoji": self.o_em.isChecked(), "stickers": self.o_st.isChecked(), "threads": self.o_th.isChecked(),
                  "private_threads": self.o_pth.isChecked(), "remember_token": self.remember.isChecked(), "lang": i18n.LANG,
                  "formats": [k for k, c in self.fmt.items() if c.isChecked()], "anon_rules": self.anon_rules()})
        try:
            settings.save(s)
        except OSError:
            pass
        if not self.remember.isChecked():
            settings.set_token("")
        opt = {k: s[k] for k in ("out_dir", "attachments", "avatars", "emoji", "stickers", "threads", "private_threads")}
        opt["formats"] = set(s["formats"]) | {"json"}
        opt["anon_rules"] = s["anon_rules"]
        opt["messages"] = True
        opt["lang"] = i18n.LANG
        if self.r_only.isChecked() and self.only_list.count():
            opt["only_users"] = {self.only_list.item(i).data(Qt.UserRole) or self.only_list.item(i).text()
                                 for i in range(self.only_list.count())}
        tag = []
        if self.use_from.isChecked():
            d = self.d_from.date().toPython()
            opt["from_ts"] = int(datetime.combine(d, dtime.min).astimezone().timestamp())
            opt["from_s"] = d.strftime("%d.%m.%Y")
            tag.append(opt["from_s"])
        if self.use_to.isChecked():
            d = self.d_to.date().toPython()
            opt["to_ts"] = int(datetime.combine(d, dtime.max).astimezone().timestamp())
            opt["to_s"] = d.strftime("%d.%m.%Y")
            tag.append(opt["to_s"])
        if self.limit.value():
            opt["limit"] = self.limit.value()
            tag.append(str(opt["limit"]))
        opt["tag"] = ("_" + "_".join(tag)) if tag else ""
        if opt.get("only_users"):
            opt["tag"] += "_users%d" % len(opt["only_users"])
        return opt

    def start(self):
        sel = self.selection()
        if not sel:
            QMessageBox.information(self, APP_NAME, _("Подключись и отметь каналы на вкладке «Каналы»."))
            return
        for r, rule in self.anon_rules().items():
            if rule["mode"] == "rename" and not rule["name"]:
                QMessageBox.warning(self, APP_NAME, _("Для пользователя %s не указан новый ник.") % r)
                self.tabs.setCurrentIndex(1)
                return
        opt = self.collect()
        self.tabs.setCurrentIndex(3)
        self.logw.clear()

        def job(wk):
            c = Client(self.token.text(), cancel=wk.cancel, log=wk.log.emit)
            ex = Exporter(c, opt, log=wk.log.emit, progress=lambda **kw: wk.prog.emit(kw))
            ex.run(sel)
            return opt["out_dir"]
        self.run_bg(job, self.finished_ok, _("Выгрузка…"))

    def finished_ok(self, out):
        self.status.setText(_("Готово"))
        self.prog.setText(_("Готово"))
        QMessageBox.information(self, APP_NAME, _("Выгрузка завершена.\nПапка: %s") % out)

    def stop(self):
        if self.worker:
            self.worker.cancel.set()
            self.status.setText(_("Останавливаю…"))

    def on_prog(self, d):
        self.prog.setText(_("#%s — %s сообщений, дошли до %s · медиа: %s") % (
            d.get("channel"), format(d.get("count", 0), ",").replace(",", " "), d.get("day"), d.get("media", 0)))

    def append_log(self, s):
        self.logw.appendPlainText(s)

    def open_html(self):
        p = os.path.join(self.out.text(), "index.html")
        if os.path.exists(p):
            QDesktopServices.openUrl(QUrl.fromLocalFile(p))
        else:
            QMessageBox.information(self, APP_NAME, _("Архив ещё не создан (или формат HTML не выбран)."))

    def change_lang(self, *_a):
        code = self.lang.currentData()
        if code == i18n.LANG:
            return
        if self.worker and self.worker.isRunning():
            self.lang.blockSignals(True)
            self.lang.setCurrentIndex(self.lang.findData(i18n.LANG))
            self.lang.blockSignals(False)
            return
        self.collect()
        i18n.set_lang(code)
        self.s["lang"] = code
        settings.save(self.s)
        w = Main()
        w.token.setText(self.token.text())
        if self.guilds:
            w.connected((self._me, self.guilds))
        w.setGeometry(self.geometry())
        w.show()
        QApplication.instance()._main = w
        self.worker = None
        self.close()

    def closeEvent(self, e):
        if self.worker and self.worker.isRunning():
            if QMessageBox.question(self, APP_NAME, _("Идёт выгрузка. Остановить и выйти?")) != QMessageBox.Yes:
                e.ignore()
                return
            self.worker.cancel.set()
            self.worker.wait(5000)
        try:
            self.collect()
        except Exception:
            pass
        e.accept()


def resource(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, name)


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Chronicord.App")
        except Exception:
            pass
    app = QApplication(sys.argv)
    dark(app)
    ic = resource(os.path.join("assets", "icon.ico"))
    if os.path.exists(ic):
        app.setWindowIcon(QIcon(ic))
    i18n.set_lang(settings.load().get("lang") or ("ru" if QLocale.system().name().startswith(("ru", "uk", "be", "kk")) else "en"))
    w = Main()
    w.show()
    sys.exit(app.exec())
