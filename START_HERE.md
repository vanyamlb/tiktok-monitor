# 🚀 TikTok Live Monitor - Start Here!

Your bot is ready! You can control everything through Telegram commands.

## Your Configuration ✅

- Bot Token: `8108905704:AAEh_P89w9bFZsR8NjvhVcKGn69sRiXYpLU`
- Channel: `@apsnyrec`

---

## Choose Your Setup Method

### Option A: Cloud Hosting (FREE, 24/7) ⭐ RECOMMENDED

**No need to keep your computer running!**

1. **Quick Setup (5 minutes):**
   ```bash
   cd ~/Desktop/tiktok
   pip3 install -r requirements.txt
   ./setup.sh
   ```

2. **Deploy to Railway (Free):**
   - See: `DEPLOY_RAILWAY.md`
   - Takes 5 minutes
   - Runs 24/7 for free
   - No computer needed

**[→ Read DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md)** for step-by-step guide

---

### Option B: Run on Your Computer

**Keep your terminal running:**

1. **Setup:**
   ```bash
   cd ~/Desktop/tiktok
   pip3 install -r requirements.txt
   ./setup.sh
   ```

2. **Add bot to your channel:**
   - Go to [@apsnyrec](https://t.me/apsnyrec)
   - Add your bot as administrator
   - Give it "Post Messages" permission

3. **Start the bot:**
   ```bash
   python3 monitor_bot.py
   ```

4. **Control via Telegram:**
   - Find your bot in Telegram
   - Send: `/start`
   - Add users: `/add username`

---

## Bot Commands

Once running, control your bot via Telegram:

| Command | What it does |
|---------|--------------|
| `/start` | Show welcome & commands |
| `/add username` | Start monitoring a TikTok user |
| `/remove username` | Stop monitoring a user |
| `/list` | Show all monitored users |
| `/status` | Check bot status & active recordings |
| `/pause` | Pause monitoring |
| `/resume` | Resume monitoring |

**Example:**
```
/add charlidamelio
/add khaby.lame
/list
```

---

## How It Works

1. **You add users** via Telegram commands
2. **Bot checks every 60 seconds** if they're live
3. **When someone goes live:**
   - 🔴 Sends notification to your channel
   - 📹 Starts recording
4. **When stream ends:**
   - 📤 Uploads video to your channel
   - ✅ Sends completion message

---

## Files Overview

| File | Purpose |
|------|---------|
| `monitor_bot.py` | Main bot with Telegram commands |
| `config.json` | Your configuration (already set up) |
| `DEPLOY_RAILWAY.md` | Deploy to cloud for free 24/7 hosting |
| `BOT_COMMANDS.md` | Full list of bot commands |
| `DEPLOYMENT.md` | All deployment options |
| `setup.sh` | Automated installation script |

---

## Quick Start Checklist

- [ ] Run `pip3 install -r requirements.txt`
- [ ] Run `./setup.sh` (installs TikTok recorder)
- [ ] Add your bot to @apsnyrec as administrator
- [ ] Choose: Cloud hosting OR run locally
- [ ] Start bot: `python3 monitor_bot.py` OR deploy to Railway
- [ ] Find your bot in Telegram and send `/start`
- [ ] Add TikTok users: `/add username`
- [ ] Done! 🎉

---

## Recommended: Cloud Deployment

Don't want to keep your computer running?

**Deploy to Railway.app (FREE):**

```bash
# Install Railway CLI
brew install railway

# Deploy
cd ~/Desktop/tiktok
railway login
railway init
railway up
```

Done! Bot runs 24/7 in the cloud for free.

**[Full guide: DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md)**

---

## Need Help?

- **Cloud deployment**: See `DEPLOY_RAILWAY.md`
- **Bot commands**: See `BOT_COMMANDS.md`
- **All deployment options**: See `DEPLOYMENT.md`
- **Test Telegram setup**: Run `python3 test_telegram.py`

---

## Next Steps

1. **If you want 24/7 hosting**: Read `DEPLOY_RAILWAY.md`
2. **If you want to test locally first**: Run `python3 monitor_bot.py`
3. **Learn all commands**: Read `BOT_COMMANDS.md`

---

**Ready to start?**

```bash
# Quick start (local):
pip3 install -r requirements.txt
./setup.sh
python3 monitor_bot.py

# Then in Telegram:
# /start
# /add username
```

🎉 **That's it!** Your TikTok live monitor is ready!
