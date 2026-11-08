<p align="center"><img src="assets/icon.png" width="96"></p>

<p align="center"><b>English</b> · <a href="README.ru.md">Русский</a></p>

# Chronicord

A free Windows app that saves Discord channel history **using your own bot** — into an archive you can open in a browser, publish on a website or just keep.

No sign-up, no ads, no telemetry. Open source, MIT license.

## Features

- A window to pick servers, categories and channels with checkboxes
- Text channels, announcement channels, voice channel chats, **threads** (active and archived) and **forums**
- **Attachments**, avatars, custom **emoji** (in text and reactions), **stickers**, **polls** with results, embeds, replies, forwarded and pinned messages
- Export of the **server's whole emoji and sticker set** with a `manifest.json`
- Date range, message limit, "only messages from selected users"
- **Replace or hide names** before exporting: rename a user, hide them, or exclude their messages entirely. Applies to authors, `@mentions` and replies; the user ID is replaced too
- Formats: **JSON** (for your own website), **HTML** (ready-made viewer with search, filters, dark/light theme), **TXT**, **CSV**
- Interface and HTML archive in **English and Russian**
- **Resume**: stop at any time, the next run continues where it left off and downloads only what's new

## Quick start

1. Download `Chronicord.exe` from [Releases](../../releases).
2. Create a bot: [discord.com/developers/applications](https://discord.com/developers/applications) → **New Application** → **Bot** tab → **Reset Token**.
3. On the same tab enable **Message Content Intent** (otherwise message text will be empty). To pick users from a list, also enable **Server Members Intent**.
4. **OAuth2 → URL Generator**: scope `bot`, permissions `View Channels` and `Read Message History` (for private archived threads also `Manage Threads`). Open the link and add the bot to your server.
5. Run Chronicord, paste the token, click "Connect", tick channels → "Start export".

Open the archive with "Open archive in browser" (`index.html` in the export folder).

> Windows may show "Windows protected your PC" because the exe isn't signed with a paid certificate. Click "More info → Run anyway". If in doubt, verify the checksum or build the app yourself (see below).

## Troubleshooting

- **0 messages in a channel or thread, no error.** The bot lacks **Read Message History** there. Discord doesn't return an error in this case — just an empty list. Threads inherit permissions from their **parent channel/forum**; check the channel's and its category's permission overrides.
- **Messages have empty text.** Enable **Message Content Intent** for the bot.
- **"Pick from members" fails.** Enable **Server Members Intent**, or add users by ID.

## Security and privacy

- The app works **only with a bot token**. User account tokens are not supported: using them breaks Discord's rules.
- Network: only `discord.com` (API) and `cdn.discordapp.com` / `media.discordapp.net` (files). Nothing is sent anywhere else — see [`chronicord/core/api.py`](chronicord/core/api.py).
- The token is never written to logs or files. If "Remember" is on, it's stored in **Windows Credential Manager**.
- Release builds are made by **GitHub Actions** straight from this code ([workflow](.github/workflows/build.yml)); each release includes `SHA256SUMS.txt`. Verify with `certutil -hashfile Chronicord.exe SHA256`.
- Export your own servers' chats. Before publishing an archive with other people's messages, ask for their consent — that's what name replacing/hiding is for.

## Building from source

Requires Python 3.10+.

```bat
git clone https://github.com/Manik1348/chronicord
cd chronicord
build.bat
```

The result is `dist\Chronicord.exe`. To run without building: `pip install -r requirements.txt` and `python main.py`.

## Archive layout

```
Chronicord/
  index.html                 list of all channels
  assets/                    avatars, emoji, stickers (shared by all channels)
  server-assets/<server>/    the server's full emoji and sticker set + manifest.json
  <channel>_<id>/
    index.html, data/        HTML viewer
    part-0001.jsonl          messages (one JSON per line, 20 MB parts)
    meta.json, state.json    export info and resume point
    media/                   attachments
    messages.txt / .csv
```

The JSONL line format is described in [FORMAT.md](FORMAT.md) (in Russian).

## License

MIT — use, modify and share freely.
