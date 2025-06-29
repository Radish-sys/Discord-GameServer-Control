
# Discord Game Server Controller Bot

A lightweight Python bot that lets you control and monitor any game server executable through Discord commands.

Originally built for a community-run *WebFishing* server, this bot is adaptable to any server that can be launched as a subprocess and accepts stdin commands.

---

## Features

- Launches and monitors an external game server (`.exe`, binary, or script)
- Listens for Discord commands to:
  - `!send <command>` — send raw server commands
  - `!say <message>` — relay a message through the server
  - `!kick <player>` / `!ban <player>`
  - `!restart` the server
  - `!refresh` the bot
- Periodically restarts the server on a schedule (default: every 12 hours)
- Streams server logs to a Discord channel
- Implements rate-limited message queues to prevent spam
- Fully asynchronous using `asyncio` and `discord.py`

---

## Setup

### 1. Configure Environment

This bot uses the `DISCORD_TOKEN` environment variable for authentication:

```python
TOKEN = os.getenv("DISCORD_TOKEN")
```

Before running the bot, export your token:

```bash
export DISCORD_TOKEN=your_token_here  # On Linux/macOS
set DISCORD_TOKEN=your_token_here     # On Windows
```

### 2. Set Executable Path

In `webfreak3.py`, set the full path to your WebFishing server executable:

```python
SERVER_EXECUTABLE = r"C:\Path\To\WebFishing.exe"
```

### 3. Install Requirements

```bash
pip install discord.py
```

### 4. Run the Bot

```bash
python webfreak3.py
```

---

## Requirements

- Python 3.8+
- `discord.py`
- A game server that:
  - Can be launched via subprocess
  - Accepts commands via stdin
  - Outputs readable logs to stdout/stderr

---

## Notes

This project was originally designed for *WebFishing* but can be adapted to servers like Minecraft, Rust, or other custom engines with minor changes.

---

## License

MIT License – Use freely, modify as needed.
