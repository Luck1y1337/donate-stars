<div align="center">

# 💛 Support Luck1y — Telegram Stars Donation Bot

**A polished, production-ready Telegram bot for accepting donations via Telegram Stars (⭐️).**
Beautiful HTML-formatted UI, a full multilingual admin panel, and one-command deployment.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![Telegram Stars](https://img.shields.io/badge/Payments-Telegram%20Stars%20⭐️-FFD700)](https://core.telegram.org/bots/payments-stars)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#-license)

Bot username: **[@luck1y_support_bot](https://t.me/luck1y_support_bot)** · Developer: **[@utofi](https://t.me/utofi)**

</div>

---

## ✨ Features

- 💳 **Donations in Telegram Stars** — preset amounts (15 / 50 / 100 / 250 / 500 ⭐️) or any custom value.
- 💬 **Optional message** attached to each donation, shown in public stats.
- 🎯 **Fundraising goal** with a live text progress bar; auto-detects when a goal is reached and prompts for a new one.
- 📊 **Public statistics** — goal progress, top-5 donors (🥇🥈🥉) and the latest donations.
- 👤 **Donor profile** — personal donation history and self-service refunds within 24 hours.
- ↩️ **Refunds** — donors can refund within 24 h; the admin can refund any donation at any time.
- 🌐 **Three languages** — Russian, Uzbek and English, switchable at any moment.
- ⚙️ **Full admin panel** (see below) — stats, goal management, donation browser, broadcast, CSV export and search.
- 🎨 **Beautiful UI** — HTML formatting (bold/italic), tasteful emoji, inline navigation with “Back” on every step.
- 🚀 **Deploy anywhere** — Docker, VPS + systemd, Railway/Render, or locally on Windows.

---

## ⚙️ Admin panel

The **⚙️ Admin** button appears in the bottom menu **only** for the account listed in `ADMIN_ID`
(you can also open it with `/admin`). The whole panel is localized into all three languages.

| Section | What it does |
| --- | --- |
| 📊 **Statistics** | Users, donors, donation & refund counts, total collected, current goal progress. |
| 🎯 **Goal** | View / set / reset the fundraising goal (buttons or `/setgoal <n>`). |
| 💸 **Donations** | Paginated list of every donation; tap one to see details and refund it (no time limit). |
| 🔍 **Search** | Find donations by `user_id` or `username`. |
| 📢 **Broadcast** | Send a text message to all bot users, with a confirmation step and a delivery report. |
| 📤 **Export CSV** | Download all donations as a single CSV file (opens cleanly in Excel). |

---

## 🧰 Tech stack

- **Python 3.11+**
- **[aiogram 3.x](https://docs.aiogram.dev/)** — async Telegram Bot framework
- **[aiosqlite](https://github.com/omnilib/aiosqlite)** — async SQLite (plain SQL, no ORM)
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** — environment configuration

> Telegram Stars payments work **out of the box** — no payment provider, no `provider_token`, no bank setup.

---

## 🚀 Quick start (local)

```bash
# 1. Enter the project folder
cd Stars-Donate

# 2. Create a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env from the template and fill it in
copy .env.example .env   # Windows
cp .env.example .env      # Linux / macOS

# 5. Run
python bot.py
```

The bot uses **long polling** — no open ports or domain required.
The SQLite database (`bot.db`) is created automatically on first launch.

**Even simpler:** double-click **`run.bat`** (Windows) or run **`./deploy/run.sh`** (Linux/macOS) —
they create the venv, install dependencies and start the bot for you.

After it starts, send the bot `/start`, pick a language, then set your first goal with `/setgoal 1000`.

---

## 🔐 Configuration

Copy `.env.example` to `.env` and fill in the values:

| Variable | Required | Description |
| --- | --- | --- |
| `BOT_TOKEN` | ✅ | Bot token from [@BotFather](https://t.me/BotFather). |
| `ADMIN_ID` | ✅ | Your numeric Telegram id — grants admin rights. |
| `THANK_YOU_STICKER_ID` | ⬜ | `file_id` of the “thank you” sticker (optional). |
| `DB_PATH` | ⬜ | SQLite file path (default `bot.db`; use `/data/bot.db` in Docker). |

<details>
<summary><b>How to get the bot token</b></summary>

1. Open [@BotFather](https://t.me/BotFather) → `/newbot`.
2. Name: `Support Luck1y`. Username: `luck1y_support_bot`.
3. Copy the token (`123456:AA...`) into `BOT_TOKEN`.

No payment provider is needed — Stars are supported natively.
</details>

<details>
<summary><b>How to get your ADMIN_ID</b></summary>

Open [@userinfobot](https://t.me/userinfobot), press Start, and copy the numeric `Id` into `ADMIN_ID`.
</details>

<details>
<summary><b>How to get a sticker file_id</b></summary>

Forward any sticker to [@idstickerbot](https://t.me/idstickerbot), copy the `file_id` into `THANK_YOU_STICKER_ID`.
Leave it empty to simply skip the sticker.
</details>

---

## 🐳 Deployment

### Option A — Docker (recommended)

```bash
cp .env.example .env   # fill in your values
docker compose up -d --build
```

- The database is stored on the `bot_data` volume, so it **survives redeploys**.
- Logs: `docker compose logs -f`
- Stop: `docker compose down`

### Option B — VPS with systemd (auto-start on boot)

```bash
cp .env.example .env   # fill in your values
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

The script creates a virtualenv, installs dependencies and registers a
`luck1y-donate-bot` systemd service that restarts on failure and starts on boot.

```bash
sudo systemctl status luck1y-donate-bot     # check status
sudo journalctl -u luck1y-donate-bot -f     # follow logs
```

### Option C — Railway / Render (cloud, a few clicks)

1. Push this repo to GitHub.
2. **Railway:** New Project → *Deploy from GitHub repo*. Config is read from `railway.json`.
   **Render:** New → *Blueprint*, pick the repo — `render.yaml` defines a worker service.
3. Add the environment variables `BOT_TOKEN`, `ADMIN_ID`, `THANK_YOU_STICKER_ID`
   (do **not** commit your `.env`).
4. Make sure it runs as a **worker** (polling, no web port).

> 💡 For persistent data in the cloud, attach a volume/disk and point `DB_PATH` to it
> (`render.yaml` already mounts a 1 GB disk at `/var/data`).

---

## 🗂️ Project structure

```
Stars-Donate/
├── bot.py                 # entry point, polling, HTML parse mode
├── config.py              # reads .env and constants
├── database.py            # all SQL queries (aiosqlite)
├── locales.py             # ru / uz / en texts (HTML + emoji)
├── keyboards.py           # reply & inline keyboards
├── states.py              # FSM states (donation + admin flows)
├── handlers/
│   ├── start.py           # /start, language, help
│   ├── donate.py          # donation flow & Stars payments
│   ├── stats.py           # public statistics & goal bar
│   ├── profile.py         # my donations
│   ├── refund.py          # donor-side refunds
│   └── admin.py           # full admin panel
├── deploy/
│   ├── deploy.sh          # VPS installer (systemd)
│   ├── run.sh             # simple Linux/macOS runner
│   └── luck1y-donate-bot.service
├── Dockerfile
├── docker-compose.yml
├── railway.json           # Railway config
├── render.yaml            # Render blueprint
├── Procfile               # generic worker process
├── run.bat / run.ps1      # Windows launchers
├── requirements.txt
└── .env.example
```

---

## 💬 Commands

| Command | Who | Description |
| --- | --- | --- |
| `/start` | everyone | choose language and open the main menu |
| `/donate` | everyone | make a donation |
| `/stats` | everyone | statistics and goal progress |
| `/refund` | everyone | refund your last donation (within 24 h) |
| `/help` | everyone | help |
| `/admin` | admin | open the admin panel |
| `/setgoal <n>` | admin | set a new fundraising goal |
| `/refund <id>` | admin | refund any donation by id, no time limit |

---

## 🧠 How the goal works

Progress is measured as `(total_all_time − cycle_start_total)` against `goal_current`.
When progress hits 100 %:

1. `cycle_start_total` is set to the current all-time total (a new cycle begins).
2. The admin is notified that the goal was reached and prompted to set a new one via `/setgoal`.
3. Until a new goal is set, the progress bar shows 100 % and “waiting for an update”.

---

## 🔒 Security notes

- `.env`, `bot.db` and `venv/` are git-ignored — never commit your token.
- User-provided content (names, donation messages, search queries) is HTML-escaped before rendering.
- Admin actions are gated by a router-level `ADMIN_ID` filter; non-admins can’t reach the panel.

---

## 📄 License

MIT — do whatever you like, attribution appreciated. Built with 💛 for [@utofi](https://t.me/utofi).
