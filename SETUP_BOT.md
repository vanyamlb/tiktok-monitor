# Setup Guide - Interactive Bot Version

## Quick Setup

### 1. Install Dependencies

```bash
cd ~/Desktop/tiktok
pip3 install -r requirements.txt
```

This will install:
- `requests` - For API calls
- `python-telegram-bot` - For bot commands

### 2. Your Configuration

Your config is already set up:
- Bot Token: `8108905704:AAEh_P89w9bFZsR8NjvhVcKGn69sRiXYpLU`
- Channel: `@apsnyrec`

### 3. Add Bot to Channel

**Important:** Add your bot as administrator to @apsnyrec

1. Open your channel [@apsnyrec](https://t.me/apsnyrec)
2. Click the channel name at top
3. Click **Administrators**
4. Click **Add Administrator**
5. Search for your bot and select it
6. Enable these permissions:
   - ✅ Post Messages
   - ✅ Edit Messages (optional)
   - ✅ Delete Messages (optional)
7. Click **Done**

### 4. Setup TikTok Recorder

```bash
cd ~/Desktop/tiktok
./setup.sh
```

This will clone and install the TikTok recorder tool.

### 5. Start the Bot

```bash
python3 monitor_bot.py
```

You should see:
```
╔═══════════════════════════════════════════════════════════╗
║   TikTok Live Monitor with Telegram Bot Control          ║
║   Control monitoring via Telegram commands               ║
╚═══════════════════════════════════════════════════════════╝

INFO - Telegram bot started
```

### 6. Talk to Your Bot

1. Search for your bot in Telegram (use the bot username from BotFather)
2. Send: `/start`
3. You'll see the command list

### 7. Add TikTok Users to Monitor

In your bot chat, send:
```
/add charlidamelio
/add khaby.lame
/add bellapoarch
```

The bot will confirm each addition:
```
✅ Added @charlidamelio to monitoring list
```

### 8. Verify Everything Works

Check monitoring status:
```
/list
```

You should see your users listed.

## How It Works

1. The bot runs continuously in the background
2. It checks every 60 seconds if monitored users are live
3. When someone goes live:
   - Starts recording automatically
   - Sends notification to your channel
4. When stream ends:
   - Uploads video to your channel
   - Sends completion message

## Running in Background

To keep the bot running even after closing terminal:

**Using screen:**
```bash
screen -S tiktok-bot
python3 monitor_bot.py
# Press Ctrl+A then D to detach
```

To check status later:
```bash
screen -r tiktok-bot
```

**Using nohup:**
```bash
nohup python3 monitor_bot.py > bot.log 2>&1 &
```

## Managing Users

All management is done through Telegram commands - no need to edit files!

**Add user:**
```
/add username
```

**Remove user:**
```
/remove username
```

**See current list:**
```
/list
```

**Check status:**
```
/status
```

**Pause/Resume:**
```
/pause
/resume
```

## Logs

View logs:
```bash
tail -f tiktok_monitor.log
```

## Troubleshooting

### Bot doesn't respond to commands
- Make sure the bot is running (`python3 monitor_bot.py`)
- Check if you started a chat with the bot first (`/start`)

### Can't add bot to channel
- Make sure you're an admin of the channel
- Try using the bot's full username (get it from @BotFather)

### Videos aren't uploading
- Check bot has "Post Messages" permission in channel
- Verify channel ID is correct: `@apsnyrec`
- Check file size (Telegram limit: 2GB for bots)

### "tiktok-live-recorder not found"
- Run `./setup.sh` to install it
- Or manually: `git clone https://github.com/Michele0303/tiktok-live-recorder`

## Next Steps

See `BOT_COMMANDS.md` for full list of commands and examples.
