# Telegram Assistant Bot

A feature-rich, modular personal Telegram bot designed to automate tasks, provide information, and help you manage groups or personal chats.

---

## ✨ Features

- **Modular Plugin System:** Easily add or remove plugins for new features.
- **Rich Help System:** `/help` shows an interactive, paginated menu with inline buttons for plugin help—new users and admins can onboard with zero coding.
- **Logging:** All actions and errors logged for transparent diagnostics.
- **Permission Middleware:** Owner-only, admin-only, and public command controls.
- **Database Integration:** Uses MongoDB for scalable, async user and plugin data management.

> _You can enable/disable any plugin with a simple config change. No code edits needed!_

---

## 🚀 Quick Start – Deploy Locally

> **No coding experience required! Just follow these steps.**

### 1. Prerequisites

- Python **3.9+** (recommended: 3.11+)
- [Git](https://git-scm.com/) (for cloning the repo)
- [MongoDB](https://www.mongodb.com/try/download/community) running locally or via MongoDB Atlas

### 2. Get Your Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Type `/newbot` and follow the steps
3. Copy your **bot token** (something like `123456:ABC-DEF1234...`)

### 3. Clone the Repository

```
git clone https://github.com/monsurcodes/telegram_assistant_bot.git

cd telegram_assistant_bot
```

### 4. Create and Edit `.env` File

Make a copy of the example `.env` file:
```
cp .env.example .env
```


Open `.env` in any text editor (Notepad, VSCode, nano, etc) and fill in:

- `BOT_TOKEN` = your Telegram bot token from BotFather
- `OWNER_ID` = your (the admin's) Telegram **user ID** (not username)
- `MONGODB_URI` = MongoDB connection string (default for local: `mongodb://localhost:27017/`)
- `MONGODB_DBNAME` = desired db name, e.g. `telegram_bot`
- For weather, Spotify, etc, add any relevant API keys you want (see plugin docs below)

**Save the file** – this will securely store your secrets.

### 5. Create a Python Virtual Environment and Install Requirements

```
python -m venv .venv
```
On Linux/Mac:
```
source .venv/bin/activate
```
On Windows:
```
.venv\Scripts\activate
```
then
```
pip install --upgrade pip
pip install -r requirements.txt
```


### 6. Run MongoDB

- If local: `mongod` in a terminal window, keep it running.
- If Atlas: Ensure your cluster is accessible and `MONGODB_URI` is set correctly.

### 7. Start the Bot

```
python -m bot.main
```


**Done!** Your bot is now running. Try talking to it on Telegram. Use `/help` to see all features.

---

## 🔌 How to Add Your Own Plugins

> **Basic undersating about pyhton is required.**

1. **Pick a Plugin:**  
   - Browse the `/bot/plugins/` folder.  
     Each file (like `reminder.py`) is a plugin.
2. **Enable or Disable Plugins:**
   - Open `.env` from your root folder.
   - Find the `DISABLED_PLUGINS` field.
   - To disable (skip) a plugin: add its class name to `DISABLED_PLUGINS`.
   - To enable, remove it from the field.
3. **Enable or Disable Help from your Plugins:**
   - Open `.env` from your root folder.
   - Find the `HELP_DISABLED_PLUGINS` field.
   - To disable help from a plugin: add its class name to `HELP_DISABLED_PLUGINS`.
   - To enable, remove it from the field.
4. **Add New Plugins (from Templates):**
   - Copy any existing file in `/bot/plugins/` (such as `weather.py` or `reminder.py`).
   - Rename it (e.g. `myplugin.py`).
   - Update the class name (e.g. `MyPlugin`) and `name` attribute.
   - Register your commands following any sample plugin.
   - No need to register manually plugin_loader will load it unless disabled.
5. **Show your plugin's Help with /help:**  
   - Make sure each plugin function has the `@register_help_text` decorator (see code base for usage).
6. **Restart the bot:**  
   - Stop (`Ctrl+C`) and start again to load new or changed plugins.

If you want to **code new advanced plugins** (optional):
- Start from the BasePlugin template.
- See any `/bot/plugins/*.py` for structure.
- Each command handler is an async method.
- Use Telethon's `events.NewMessage` and the utility decorators.

---

## 🛡️ Security, Permissions, and Admin/Owner Controls

- **Bot owner (YOUR user ID)** can access owner-only commands from anywhere.
- **Group admins** can access advanced moderation commands (like `/kick @user`)—protected by middleware.
- **General users** can use standard public commands like `/help` and `/remind`.

---

## 🧩 Advanced Features

- **Paginated help menu:** Just type `/help` and use the inline buttons to browse all plugins and their features.
- **Rich permission system:** Quickly restrict features to admins or owner only by adding decorators. No manual ID checks.
- **Logging:** See everything the bot does (in `logs/bot.log`). Each action is recorded for review or troubleshooting.

---

## 🆘 Support & Troubleshooting

- Review error messages and logs in `logs/bot.log` for detailed diagnostics.
- If a plugin does not seem to load or work, check:
  - Is it listed in the `DISABLED_PLUGINS` list?
  - Did you install all requirements?
  - Are API keys (weather, Spotify, etc) present in `.env`?

---

## 📚 Contributing

Pull requests are welcome!  
Please fork, make your changes, and open a PR.  
To request new plugins or submit ideas, open an [issue page](https://github.com/monsurcodes/telegram_assistant_bot/issues).

---

## 📜 License

[MIT](https://github.com/monsurcodes/telegram_assistant_bot/blob/main/LICENSE)

---

## 🤝 Community & Credits

This bot is open-source because collaboration and learning are better when shared.  
Thanks to [monsurcodes](https://github.com/monsurcodes) for development and to external libraries:  
- [Telethon](https://github.com/LonamiWebs/Telethon)  
- [Motor (async MongoDB)](https://motor.readthedocs.io/)  
- [Spotipy](https://spotipy.readthedocs.io/en/2.0.1/)  
- [WeatherAPI.com](https://www.weatherapi.com/)

---

**Start by running /help. Explore, customize, and automate your Telegram experience!**
