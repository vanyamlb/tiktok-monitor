# Railway Deployment Guide

## Quick Deploy to Railway

Your code is ready at: https://github.com/vanyamlb/tiktok-monitor

### Step 1: Create New Project on Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose: **vanyamlb/tiktok-monitor**

### Step 2: Configure Environment (IMPORTANT!)

Railway will start building automatically, but you need to check if cookies are included.

**Option A: If cookies.json is in the repo (current setup)**
- The cookies are already included in `tiktok-live-recorder/src/cookies.json`
- Railway will use them automatically
- ✅ No action needed!

**Option B: If cookies need to be added as environment variable**
- In Railway project, go to "Variables" tab
- Add variable: `COOKIES_JSON` 
- Paste the TikTok cookies JSON content
- Redeploy

### Step 3: Verify Deployment

1. Wait for build to complete (~3-5 minutes)
2. Check "Deployments" tab for status
3. Click on latest deployment to see logs
4. Look for: "✅ Bot started - send /start to @tiksnzbot"

### Step 4: Test the Bot

1. Open Telegram
2. Send `/start` to @tiksnzbot
3. Try `/status` to check if monitoring is running
4. Check your channel @apsnyrec for notifications

## Troubleshooting

### If build fails:
- Check "Deploy Logs" in Railway
- Common issues:
  - Missing FFmpeg: Fixed by nixpacks.toml (included)
  - Python version: Using 3.13 (configured in runtime.txt)
  - Dependencies: All in requirements.txt

### If bot starts but doesn't record:
- Check cookies are valid (TikTok cookies expire)
- Verify FFmpeg is installed (check logs for FFmpeg output)
- Test live detection manually from Railway shell

### If recordings don't upload to Telegram:
- Verify bot token in config.json
- Check channel @apsnyrec exists and bot is admin
- Check file size (Telegram has 50MB limit for bots)

## Manual Configuration

If you need to update config after deployment:

1. Go to Railway project
2. Click "Settings" → "Source Repo"
3. Update GitHub files
4. Railway auto-deploys on push

## Current Configuration

- **Bot**: @tiksnzbot
- **Channel**: @apsnyrec  
- **Monitoring**: vasya.tv8
- **Check Interval**: 30 seconds
- **Recording**: Automatic via wrapper script

## Files on Railway

```
/app
├── bot_final_working.py          # Main bot
├── record_wrapper.py              # Recording wrapper
├── config.json                    # Bot config
├── requirements.txt               # Python deps
├── Procfile                       # Railway start command
├── nixpacks.toml                  # System dependencies
└── tiktok-live-recorder/
    └── src/
        └── cookies.json           # TikTok cookies
```
