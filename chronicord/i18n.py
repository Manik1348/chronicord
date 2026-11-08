LANG = "ru"
LANGS = [("ru", "Русский"), ("en", "English")]


def set_lang(code):
    global LANG
    LANG = code if code in ("ru", "en") else "ru"


def _(s):
    if LANG == "ru":
        return s
    return EN.get(s, s)


EN = {
    "Заменить ник": "Replace name",
    "Скрыть ник": "Hide name",
    "Исключить сообщения": "Exclude messages",
    "Выбор пользователей": "Select users",
    "Показать": "Show",
    "Запомнить": "Remember",
    "Хранить токен в Диспетчере учётных данных Windows": "Store the token in Windows Credential Manager",
    "Подключиться": "Connect",
    "Как создать бота?": "How to create a bot?",
    "Не подключено": "Not connected",
    "1. Каналы": "1. Channels",
    "2. Пользователи": "2. Users",
    "3. Настройки": "3. Settings",
    "4. Выгрузка": "4. Export",
    "Чьи сообщения выгружать": "Whose messages to export",
    "Всех пользователей": "All users",
    "Только выбранных:": "Only selected:",
    "Замена и скрытие ников (применяется к автору, упоминаниям @ник и ответам)":
        "Replace or hide names (applies to authors, @mentions and replies)",
    "Период и количество": "Period and amount",
    "С даты:": "From:",
    "По дату (включительно):": "To (inclusive):",
    "Медиа": "Media",
    "Вложения (картинки, видео, файлы)": "Attachments (images, videos, files)",
    "Аватарки пользователей": "User avatars",
    "Кастомные эмодзи из сообщений и реакций": "Custom emoji from messages and reactions",
    "Стикеры из сообщений": "Stickers from messages",
    "Ветки и форумы": "Threads and forums",
    "Выгружать ветки выбранных каналов (активные и архивные)": "Export threads of selected channels (active and archived)",
    "Включая закрытые архивные (нужно право «Управлять ветками»)": "Including private archived ones (requires “Manage Threads”)",
    "Форматы": "Formats",
    "Папка для архива": "Archive folder",
    "Обзор…": "Browse…",
    "▶ Начать выгрузку": "▶ Start export",
    "■ Остановить": "■ Stop",
    "Открыть папку": "Open folder",
    "Открыть архив в браузере": "Open archive in browser",
    "Справка": "Help",
    "Подключаюсь…": "Connecting…",
    "ID пользователя": "User ID",
    "ID (число из 17–20 цифр):": "ID (a 17–20 digit number):",
    "Выгрузка…": "Exporting…",
    "Готово": "Done",
    "Поиск по нику или ID…": "Search by name or ID…",
    "Ctrl/Shift — выбрать несколько": "Ctrl/Shift — select several",
    "%s %s — архив чатов Discord": "%s %s — Discord chat archiver",
    "Токен бота (Developer Portal → Bot → Reset Token)": "Bot token (Developer Portal → Bot → Reset Token)",
    "Токен:": "Token:",
    "Язык:": "Language:",
    "Сервер / канал": "Server / channel",
    "Выбрать все": "Select all",
    "Снять все": "Clear all",
    "Пункт «★ Эмодзи и стикеры» выгружает весь набор сервера.": "The “★ Emoji and stickers” item exports the server's whole set.",
    "Добавить по ID": "Add by ID",
    "Выбрать из участников": "Pick from members",
    "Удалить": "Remove",
    "Имя": "Name",
    "Действие": "Action",
    "Новый ник": "New name",
    "Оставить аватар": "Keep avatar",
    "Удалить строку": "Remove row",
    "ID скопируешь в Discord: Настройки → Расширенные → Режим разработчика, затем ПКМ по пользователю → «Копировать ID».\n"
    "У скрытых и переименованных пользователей ID в архиве тоже заменяется (anon-1, anon-2…).":
        "To copy an ID in Discord: Settings → Advanced → Developer Mode, then right-click a user → “Copy User ID”.\n"
        "Hidden and renamed users also get their ID replaced in the archive (anon-1, anon-2…).",
    "все": "all",
    "Максимум сообщений с канала:": "Max messages per channel:",
    "Выгрузка с периодом/лимитом сохраняется в отдельную папку.": "An export with a period/limit is saved to a separate folder.",
    "Ссылки Discord на файлы со временем истекают —\nлучше скачивать сразу.": "Discord file links expire over time —\nbetter download them right away.",
    "Форумы выгружаются всегда вместе с ветками.": "Forums are always exported with their threads.",
    "JSON — для своего сайта (всегда сохраняется)": "JSON — for your own website (always saved)",
    "HTML — готовый просмотр с поиском": "HTML — ready-made viewer with search",
    "TXT — простой текст": "TXT — plain text",
    "CSV — для Excel": "CSV — for Excel",
    "Выгрузку можно остановить в любой момент — при следующем запуске она продолжится с того же места.":
        "You can stop the export at any time — the next run continues from the same place.",
    "\nОстановлено. При следующем запуске выгрузка продолжится с того же места.":
        "\nStopped. The next run will continue from the same place.",
    "Остановлено": "Stopped",
    "Вставь токен бота.": "Paste the bot token.",
    "Бот: %s · серверов: %d": "Bot: %s · servers: %d",
    "Бот не состоит ни на одном сервере. Добавь его по ссылке из OAuth2 → URL Generator.":
        "The bot isn't on any server. Add it using the link from OAuth2 → URL Generator.",
    "Сначала подключись.": "Connect first.",
    "Загружаю участников…": "Loading members…",
    "Подключись и отметь каналы на вкладке «Каналы».": "Connect and tick channels on the “Channels” tab.",
    "Выгрузка завершена.\nПапка: %s": "Export finished.\nFolder: %s",
    "Останавливаю…": "Stopping…",
    "#%s — %s сообщений, дошли до %s · медиа: %s": "#%s — %s messages, reached %s · media: %s",
    "Архив ещё не создан (или формат HTML не выбран).": "The archive hasn't been created yet (or HTML format isn't selected).",
    "<p>%s %s · <a href=\"%s\">%s</a> · лицензия MIT</p>": "<p>%s %s · <a href=\"%s\">%s</a> · MIT license</p>",
    "★ Эмодзи и стикеры сервера": "★ Server emoji and stickers",
    "ID — это число. Включи режим разработчика в Discord и скопируй ID.": "An ID is a number. Enable Developer Mode in Discord and copy the ID.",
    "Участников: %d": "Members: %d",
    "Идёт выгрузка. Остановить и выйти?": "An export is running. Stop and quit?",
    "Токен не подошёл. Проверь, что это токен бота из Developer Portal → Bot.":
        "The token was rejected. Make sure it's a bot token from Developer Portal → Bot.",
    "Ошибка: %s": "Error: %s",
    "Для пользователя %s не указан новый ник.": "No new name set for user %s.",
    "Папка": "Folder",
    "Не удалось получить участников. Включи боту Server Members Intent (Developer Portal → Bot) или добавляй по ID.\n\n":
        "Couldn't load members. Enable Server Members Intent for the bot (Developer Portal → Bot) or add users by ID.\n\n",
    "Нет доступа (%s). Проверь права бота.": "Access denied (%s). Check the bot's permissions.",
    "Ошибка Discord: %s": "Discord error: %s",
    "Язык изменится после перезапуска окна. Перезапустить сейчас?": "The language changes after the window restarts. Restart now?",
    "\nВсё. Время: %d мин. Файлы — в папке %s": "\nAll done. Time: %d min. Files are in %s",
    "  ↳ ветка «%s»": "  ↳ thread “%s”",
    "\n#%s": "\n#%s",
    "%s — %s": "%s — %s",
    "  докачиваю медиа для ранее выгруженных сообщений…": "  downloading media for previously exported messages…",
    "  Готово: %d сообщений, вложений %d (%s по данным Discord).": "  Done: %d messages, %d attachments (%s according to Discord).",
    "\nЭмодзи и стикеры сервера «%s»…": "\nServer emoji and stickers of “%s”…",
    "  эмодзи: %d, стикеров: %d → %s": "  emoji: %d, stickers: %d → %s",
    "  Веток найдено: %d (активных %d, архивных %d)": "  Threads found: %d (active %d, archived %d)",
    "  Скачано вложений: %d (%s), недоступно: %d.": "  Attachments downloaded: %d (%s), unavailable: %d.",
    "продолжаю": "resuming",
    "начинаю": "starting",
    "  ВНИМАНИЕ: у сообщений пустой текст. Включи боту Message Content Intent (Developer Portal → Bot), удали папку %s и запусти заново.":
        "  WARNING: messages have empty text. Enable Message Content Intent for the bot (Developer Portal → Bot), delete the folder %s and run again.",
    "  Нет доступа. Дай боту права «Просмотр канала» и «Читать историю сообщений».":
        "  No access. Give the bot “View Channel” and “Read Message History” permissions.",
    "  %s сообщений, дошли до %s": "  %s messages, reached %s",
    "  вложения: %d скачано (%s), дошли до %s": "  attachments: %d downloaded (%s), reached %s",
    "  Не удалось получить активные ветки (%s).": "  Couldn't get active threads (%s).",
    "\n#%s — форум, веток: %d": "\n#%s — forum, threads: %d",
    "  Закрытые ветки #%s недоступны (нужно право «Управлять ветками»).": "  Private threads of #%s are unavailable (requires “Manage Threads”).",
    "  Не удалось получить архивные ветки #%s (%s). Проверь право «Читать историю сообщений».":
        "  Couldn't get archived threads of #%s (%s). Check the “Read Message History” permission.",
    "  + ещё веток по сообщениям: %d": "  + more threads found via messages: %d",
    "%.1f МБ": "%.1f MB",
    "  Discord вернул 0 сообщений%s. Если сообщения там есть — у бота нет права «Читать историю сообщений». "
    "Для веток это право берётся из родительского канала/форума: проверь его настройки прав (и категории).":
        "  Discord returned 0 messages%s. If there are messages, the bot lacks “Read Message History”. "
        "Threads take this permission from the parent channel/forum: check its permission settings (and the category's).",
    " (по данным Discord в ветке: %d)": " (Discord reports %d in the thread)",
    "  Обычная загрузка вернула 0 сообщений, загружаю в обратном порядке…": "  Normal loading returned 0 messages, loading in reverse order…",
    "нет связи с Discord": "can't reach Discord",
    "Связь прервалась, повтор…": "Connection lost, retrying…",
    "Скрытый пользователь": "Hidden user",
    "роль": "role",
    "канал": "channel",
    "добавил участника": "added a member",
    "удалил участника": "removed a member",
    "звонок": "call",
    "изменил название канала": "changed the channel name",
    "закрепил сообщение": "pinned a message",
    "присоединился к серверу": "joined the server",
    "забустил сервер": "boosted the server",
    "создал ветку": "started a thread",
    "начальное сообщение ветки": "thread starter message",
    "результаты опроса": "poll results",
    "[переслано] ": "[forwarded] ",
    "[файл: %s]": "[file: %s]",
    "[встраивание: %s]": "[embed: %s]",
    "[стикер: %s]": "[sticker: %s]",
    "[реакции: %s]": "[reactions: %s]",
    "[ветка: %s]": "[thread: %s]",
    "[опрос: %s] ": "[poll: %s] ",
    "дата": "date",
    "автор_id": "author_id",
    "автор": "author",
    "текст": "text",
    "вложения": "attachments",
    "реакции": "reactions",
    "ответ_на": "reply_to",
    " (ред.)": " (edited)",
}

HELP_EN = """<h3>How to connect a bot</h3><ol>
<li>Open <a href="https://discord.com/developers/applications">discord.com/developers/applications</a> → <b>New Application</b>.</li>
<li><b>Bot</b> tab → <b>Reset Token</b> → copy the token and paste it into the app.</li>
<li>On the same tab enable <b>Message Content Intent</b> (without it message text will be empty).
 To pick users from a list, also enable <b>Server Members Intent</b>.</li>
<li><b>OAuth2 → URL Generator</b> tab: scope <b>bot</b>, permissions <b>View Channels</b>, <b>Read Message History</b>
 (for private archived threads also <b>Manage Threads</b>). Open the link and add the bot to your server.</li></ol>
<h3>Security</h3><p>The token is sent only to discord.com. The app sends data nowhere else,
collects no statistics and never asks for your account token (that is against Discord's rules).
If “Remember” is on, the token is stored in Windows Credential Manager.</p>"""

VIEWER = {
    "ru": {"search": "Поиск…", "all_authors": "Все авторы", "from": "С даты", "to": "По дату", "theme": "Тема",
           "theme_t": "Светлая/тёмная тема", "all_channels": "← Все каналы", "loading": "Загрузка…",
           "threads": "Ветки:", "nothing": "Ничего не найдено", "messages": "Сообщений: ", "of": " из ",
           "no_msgs": "Сообщений нет.", "forum": "Это форум: выбери ветку выше.", "unavailable": "сообщение недоступно",
           "attachment": "[вложение]", "forwarded": "переслано", "sticker": "стикер", "votes": " голосов",
           "multi": " · несколько ответов", "edited": " (ред.)", "bot": "БОТ", "webhook": "ВЕБХУК", "in": " · в #",
           "mb": " МБ", "locale": "ru-RU", "archive": "Архив Discord", "made": "создано в Chronicord",
           "msgs_short": " сообщ.", "empty": "Пусто",
           "sys": {"1": "добавил участника", "2": "удалил участника", "4": "изменил название канала", "6": "закрепил сообщение",
                   "7": "присоединился к серверу", "8": "забустил сервер", "9": "забустил сервер", "10": "забустил сервер",
                   "11": "забустил сервер", "18": "создал ветку", "46": "опрос завершён"}},
    "en": {"search": "Search…", "all_authors": "All authors", "from": "From", "to": "To", "theme": "Theme",
           "theme_t": "Light/dark theme", "all_channels": "← All channels", "loading": "Loading…",
           "threads": "Threads:", "nothing": "Nothing found", "messages": "Messages: ", "of": " of ",
           "no_msgs": "No messages.", "forum": "This is a forum: pick a thread above.", "unavailable": "message unavailable",
           "attachment": "[attachment]", "forwarded": "forwarded", "sticker": "sticker", "votes": " votes",
           "multi": " · multiple answers", "edited": " (edited)", "bot": "BOT", "webhook": "WEBHOOK", "in": " · in #",
           "mb": " MB", "locale": "en-GB", "archive": "Discord archive", "made": "made with Chronicord",
           "msgs_short": " msgs", "empty": "Empty",
           "sys": {"1": "added a member", "2": "removed a member", "4": "changed the channel name", "6": "pinned a message",
                   "7": "joined the server", "8": "boosted the server", "9": "boosted the server", "10": "boosted the server",
                   "11": "boosted the server", "18": "started a thread", "46": "poll ended"}},
}
