# Deploy to Railway.app - Free 24/7 Hosting

The easiest way to run your bot 24/7 without keeping your computer on!

## Why Railway?

✅ **FREE** - 500 hours/month (enough for 24/7)
✅ **No credit card required** for hobby plan
✅ **Automatic restarts** if bot crashes
✅ **Easy logs viewing**
✅ **Takes 5 minutes to setup**

## Step-by-Step Guide

### 1. Create Railway Account

Go to [railway.app](https://railway.app) and sign up with GitHub

### 2. Install Railway CLI

**macOS:**
```bash
brew install railway
```

**Linux/Windows:**
```bash
npm install -g @railway/cli
```

Or use without installing: Just push to GitHub and deploy via web interface (see Method 2 below)

---

## Method 1: Direct Deploy (Fastest)

### 3. Login to Railway

```bash
railway login
```

This opens a browser to authenticate.

### 4. Navigate to your project

```bash
cd ~/Desktop/tiktok
```

### 5. Initialize and Deploy

```bash
railway init
railway up
```

### 6. Done!

Your bot is now running in the cloud!

Check logs:
```bash
railway logs
```

---

## Method 2: Deploy via GitHub (Recommended)

### 3. Create GitHub Repository

```bash
cd ~/Desktop/tiktok

# Initialize git
git init

# Create .gitignore
echo "*.log
__pycache__/
recordings/
tiktok-live-recorder/
monitoring_list.json
.DS_Store" > .gitignore

# Commit files
git add .
git commit -m "Initial commit"
```

### 4. Push to GitHub

Create a new repository on [GitHub.com](https://github.com/new), then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/tiktok-monitor.git
git branch -M main
git push -u origin main
```

### 5. Deploy on Railway

1. Go to [railway.app/new](https://railway.app/new)
2. Click **"Deploy from GitHub repo"**
3. Select your repository
4. Click **Deploy**

Railway will automatically:
- Detect it's a Python project
- Install dependencies
- Run `monitor_bot.py`

### 6. Check Status

1. Go to your Railway dashboard
2. Click on your project
3. Click **"Deployments"** to see logs

---

## Configuration

Your config.json is already set up, but Railway needs to know it exists.

**Option A: Push config.json to GitHub** (Not recommended for security)

**Option B: Use Environment Variables** (Recommended)

In Railway dashboard:
1. Click your project
2. Go to **Variables** tab
3. Click **Raw Editor**
4. Paste:

```
TELEGRAM_BOT_TOKEN=8108905704:AAEh_P89w9bFZsR8NjvhVcKGn69sRiXYpLU
TELEGRAM_CHAT_ID=@apsnyrec
```

Then modify `monitor_bot.py` to read from env vars (optional, config.json works too)

---

## Managing Your Bot

### View Logs
```bash
railway logs
```

Or in Railway dashboard → Deployments → View Logs

### Restart Bot
```bash
railway restart
```

### Stop Bot
```bash
railway down
```

### Check Status
In Railway dashboard, you'll see:
- ✅ Active (green) = Running
- ⚠️ Deploying (yellow) = Starting up
- ❌ Failed (red) = Error (check logs)

---

## Updating Your Bot

When you make changes:

```bash
cd ~/Desktop/tiktok

# Make your changes, then:
git add .
git commit -m "Update bot"
git push
```

Railway automatically detects the push and redeploys!

---

## Cost

**Free Tier:**
- 500 hours/month execution time
- $5 credit/month
- Perfect for one bot running 24/7

**If you exceed:** Upgrade to hobby plan ($5/month) for unlimited hours

---

## Troubleshooting

### "Build failed"

Check Railway logs. Usually means:
- Missing dependency → Add to requirements.txt
- Python version issue → Railway uses Python 3.11 by default

### Bot not responding to commands

1. Check logs: `railway logs`
2. Make sure bot is running (should show "Telegram bot started")
3. Verify bot token is correct in config.json

### Can't find tiktok-live-recorder

The Dockerfile and setup.sh handle this automatically. If issues:
1. Check Railway logs
2. Make sure setup.sh is executable: `chmod +x setup.sh`

### Videos not uploading

1. Check bot permissions in Telegram channel
2. Verify channel ID: `@apsnyrec`
3. Check Railway logs for errors

---

## Alternative: One-Click Deploy

Coming soon! For now, use Method 1 or 2 above.

---

## Support

- Railway Docs: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)

---

**That's it!** Your bot is now running 24/7 in the cloud, completely free! 🎉
