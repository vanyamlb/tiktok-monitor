# Update Existing Railway Project

## Quick Update Steps:

### 1. Go to Your Railway Project
- Open https://railway.app
- Click on your existing TikTok monitor project

### 2. Check GitHub Connection
- Click "Settings" tab
- Look for "Source Repo" section
- Should show: vanyamlb/tiktok-monitor
- Branch: main

### 3A: If Connected - Trigger Redeploy
- Go to "Deployments" tab
- Latest commit should be: "Add Railway deployment guide" 
- If not, click "Redeploy" button (3 dots menu)

### 3B: If NOT Connected - Reconnect GitHub
- Settings → Source Repo → "Connect Repo"
- Select: vanyamlb/tiktok-monitor
- Branch: main
- Root Directory: leave empty
- Railway will start deploying automatically

### 4. Verify New Deployment
Check deployment logs for these key indicators:

```
✅ Installing FFmpeg (from nixpacks.toml)
✅ Installing Python 3.13 dependencies
✅ Starting: python3 bot_final_working.py
✅ Config loaded
✅ Loaded 1 users
✅ Bot started - send /start to @tiksnzbot
```

## What Changed in This Update:

✅ **Fixed recording** - Now uses record_wrapper.py to bypass Python 3.14 issues
✅ **Fixed cookies** - Converted to curl_cffi compatible format  
✅ **Added FFmpeg** - nixpacks.toml ensures it's installed
✅ **Working live detection** - Using tikrec.com API method
✅ **Complete tiktok-live-recorder** - All source files included

## Check Current Deployment:

### In Railway Logs, you should see:
```
🔍 Checking vasya.tv8...
📊 vasya.tv8: 🔴 LIVE (or ⚫ offline)
```

If vasya.tv8 is live, you'll also see:
```
🎬 Starting recording: vasya.tv8
```

## Troubleshooting:

### If Build Fails:
1. Check "Deploy Logs" for error messages
2. Most common: Python version mismatch
   - Solution: runtime.txt specifies Python 3.13 ✅
3. FFmpeg missing:
   - Solution: nixpacks.toml includes FFmpeg ✅

### If Bot Starts But Doesn't Record:
1. Check cookies are valid in logs
2. Verify FFmpeg is available: look for FFmpeg output in logs
3. Check recordings directory is being created

### If You See "Conflict: terminated by other getUpdates":
- Another bot instance is running
- Only ONE instance can run at a time
- Stop any local instances of the bot
- Railway will continue working fine

## Current Bot Configuration:

```json
{
  "telegram": {
    "bot_token": "8573121438:AAGzUXeI_zX2cCVHVoIzsC18QRUAsW2N6IU",
    "chat_id": "@apsnyrec"
  },
  "recording": {
    "check_interval": 30
  }
}
```

## File Structure on Railway:

```
/app
├── bot_final_working.py          ← Main bot (NEW)
├── record_wrapper.py              ← Recording wrapper (NEW)
├── config.json                    
├── nixpacks.toml                  ← FFmpeg config (NEW)
├── tiktok-live-recorder/
│   └── src/
│       ├── cookies.json           ← Reformatted (FIXED)
│       └── [all recorder files]   ← Full source (NEW)
└── requirements.txt               ← Updated deps
```

## Test After Deployment:

1. **Telegram bot**: Send `/start` to @tiksnzbot
2. **Check status**: Send `/status`
3. **View logs**: Railway → Deployments → View Logs
4. **Wait for live**: When vasya.tv8 goes live, check @apsnyrec

---

**Need to see what's deployed?**
- Railway → Settings → Show commit SHA
- Should match latest GitHub commit: 41d6607
