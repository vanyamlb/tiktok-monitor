# Quick Start Guide

## 1. Run Setup Script

```bash
cd ~/Desktop/tiktok
./setup.sh
```

This will automatically install all dependencies.

## 2. Create Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send: `/newbot`
3. Choose a name and username for your bot
4. Copy the **bot token** (looks like: `123456789:ABC...`)

## 3. Create/Setup Telegram Channel

1. Create a new channel in Telegram
2. Add your bot as an administrator to the channel
3. Get your channel ID:
   - For public channels: use `@your_channel_name`
   - For private channels: forward a message to [@userinfobot](https://t.me/userinfobot)

## 4. Configure

Edit `config.json`:

```json
{
  "telegram": {
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    "chat_id": "@your_channel_name",
    "enabled": true
  },
  "tiktok_users": [
    "charlidamelio",
    "khaby.lame"
  ],
  "recording": {
    "output_directory": "./recordings",
    "check_interval": 60,
    "automatic_interval": 5,
    "duration": 0
  }
}
```

Replace:
- `bot_token`: Your actual bot token from BotFather
- `chat_id`: Your channel ID or @username
- `tiktok_users`: TikTok usernames you want to monitor (without @)

## 5. Run

```bash
python3 monitor.py
```

That's it! The monitor will:
- Check every 60 seconds if users are live
- Start recording automatically
- Send notification to your channel
- Upload video when stream ends

## Running in Background

To keep it running after closing terminal:

```bash
screen -S tiktok
python3 monitor.py
# Press: Ctrl+A then D to detach
```

To check status later:
```bash
screen -r tiktok
```

## Check Logs

```bash
tail -f tiktok_monitor.log
```

## Need Help?

See `README.md` for detailed documentation and troubleshooting.
