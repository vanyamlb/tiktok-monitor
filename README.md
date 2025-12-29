# TikTok Live Monitor & Recorder

Automatically monitor TikTok users for live streams, record them, and upload to your Telegram channel.

## Features

- 🔍 Monitor multiple TikTok accounts simultaneously
- 📹 Automatically record live streams
- 📤 Upload recordings to Telegram channel
- 🔔 Real-time notifications when streams start/end
- ⚙️ Configurable monitoring intervals
- 🔄 Continuous monitoring with error recovery

## Prerequisites

- Python 3.11 or higher
- FFmpeg (for video processing)
- Git
- A Telegram Bot Token and Channel

## Installation

### 1. Clone this repository (if not already done)

```bash
cd ~/Desktop/tiktok
```

### 2. Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### 3. Clone the tiktok-live-recorder

```bash
git clone https://github.com/Michele0303/tiktok-live-recorder
cd tiktok-live-recorder/src
pip3 install -r requirements.txt
cd ../..
```

### 4. Install Python dependencies for the monitor

```bash
pip3 install requests
```

## Telegram Setup

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the **Bot Token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get your Channel ID

**Method 1: Using a public channel**
1. Create a public channel or use an existing one
2. Add your bot as an administrator to the channel
3. The channel ID is `@your_channel_name`

**Method 2: Using a private channel**
1. Create a channel (can be private)
2. Add your bot as an administrator
3. Forward any message from the channel to [@userinfobot](https://t.me/userinfobot)
4. It will show you the channel ID (looks like: `-1001234567890`)

### 3. Update Configuration

Edit `config.json`:

```json
{
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "chat_id": "YOUR_CHANNEL_ID_HERE",
    "enabled": true
  },
  "tiktok_users": [
    "username1",
    "username2"
  ],
  "recording": {
    "output_directory": "./recordings",
    "check_interval": 60,
    "automatic_interval": 5,
    "duration": 0
  },
  "proxy": {
    "enabled": false,
    "http_proxy": ""
  }
}
```

**Configuration Options:**

- `bot_token`: Your Telegram bot token from BotFather
- `chat_id`: Your Telegram channel ID (or @channel_name)
- `enabled`: Set to `true` to enable Telegram uploads
- `tiktok_users`: Array of TikTok usernames to monitor (without @)
- `output_directory`: Where to save recordings
- `check_interval`: How often to check for live streams (in seconds)
- `automatic_interval`: Interval for the recorder to check if stream is still live
- `duration`: Maximum recording duration (0 = unlimited)
- `proxy`: Optional HTTP proxy configuration

## Usage

### Start the Monitor

```bash
python3 monitor.py
```

The monitor will:
1. Check if any of the configured users are live every 60 seconds (or your configured interval)
2. Automatically start recording when a user goes live
3. Send a notification to your Telegram channel
4. Upload the recording to Telegram when the stream ends

### Run in Background (recommended)

**Using screen (macOS/Linux):**
```bash
screen -S tiktok-monitor
python3 monitor.py
# Press Ctrl+A then D to detach
# To reattach: screen -r tiktok-monitor
```

**Using nohup:**
```bash
nohup python3 monitor.py > monitor.log 2>&1 &
```

**Using systemd (Linux):**
Create `/etc/systemd/system/tiktok-monitor.service`:
```ini
[Unit]
Description=TikTok Live Monitor
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/Users/vanyamlb/Desktop/tiktok
ExecStart=/usr/bin/python3 /Users/vanyamlb/Desktop/tiktok/monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tiktok-monitor
sudo systemctl start tiktok-monitor
```

## Logs

Logs are saved to `tiktok_monitor.log` in the same directory.

View logs in real-time:
```bash
tail -f tiktok_monitor.log
```

## Troubleshooting

### "tiktok-live-recorder not found"
Make sure you cloned the repository in the correct location:
```bash
git clone https://github.com/Michele0303/tiktok-live-recorder
```

### "FFmpeg not found"
Install FFmpeg using your package manager (see Installation section)

### "Failed to upload video"
- Check your bot token is correct
- Ensure the bot is an administrator in your channel
- Verify the chat_id is correct
- Check file size (Telegram has a 2GB limit for bots, 4GB for premium)

### "Error checking live status"
- The user might have blocked their profile
- TikTok might be rate-limiting requests
- Try increasing the `check_interval` in config.json

### Recording fails immediately
- Check if you need cookies (some regions require authentication)
- See tiktok-live-recorder documentation for cookie setup

## Advanced Configuration

### Using Cookies for Authentication

Some regions require authentication. Create `cookies.json` in the `tiktok-live-recorder/src` directory:

```json
{
  "cookies": [
    {
      "name": "cookie_name",
      "value": "cookie_value",
      "domain": ".tiktok.com"
    }
  ]
}
```

### Using a Proxy

If you need to bypass regional restrictions:

```json
{
  "proxy": {
    "enabled": true,
    "http_proxy": "http://proxy.example.com:8080"
  }
}
```

## File Structure

```
tiktok/
├── monitor.py              # Main monitoring script
├── config.json            # Configuration file
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── tiktok_monitor.log     # Log file (created automatically)
├── recordings/            # Recorded videos (created automatically)
└── tiktok-live-recorder/  # The recorder tool (cloned separately)
```

## Credits

This tool is built on top of [tiktok-live-recorder](https://github.com/Michele0303/tiktok-live-recorder) by Michele0303.

## License

MIT License - feel free to modify and distribute
