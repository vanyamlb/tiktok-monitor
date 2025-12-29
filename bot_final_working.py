#!/usr/bin/env python3
"""
TikTok Live Monitor - FINAL WORKING VERSION
Uses the exact live detection method from tiktok-live-recorder
"""

import logging
import json
import time
import requests
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
from threading import Thread, Lock
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG_FILE = "config.json"
MONITORING_FILE = "monitoring_list.json"
RECORDER_PATH = "./record_wrapper.py"
OUTPUT_DIR = "./recordings"

# Global variables
config = {}
monitoring_users = []
monitoring_enabled = True
active_recordings = {}
recordings_lock = Lock()


def load_config():
    """Load config from file"""
    global config
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        logger.info("✅ Config loaded")
    except Exception as e:
        logger.error(f"❌ Config error: {e}")
        config = {
            "telegram": {
                "bot_token": "8573121438:AAGzUXeI_zX2cCVHVoIzsC18QRUAsW2N6IU",
                "chat_id": "@apsnyrec",
                "enabled": True
            },
            "recording": {
                "check_interval": 30
            }
        }


def load_monitoring_list():
    """Load monitoring list from file"""
    global monitoring_users
    try:
        if Path(MONITORING_FILE).exists():
            with open(MONITORING_FILE, 'r') as f:
                data = json.load(f)
                monitoring_users = data.get('users', [])
            logger.info(f"✅ Loaded {len(monitoring_users)} users")
        else:
            monitoring_users = []
            save_monitoring_list()
    except Exception as e:
        logger.error(f"❌ Load list error: {e}")
        monitoring_users = []


def save_monitoring_list():
    """Save monitoring list to file"""
    try:
        data = {
            'users': monitoring_users,
            'last_updated': datetime.now().isoformat()
        }
        with open(MONITORING_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"❌ Save error: {e}")


def send_telegram_message(message: str):
    """Send message to Telegram channel"""
    try:
        bot_token = config['telegram']['bot_token']
        chat_id = config['telegram']['chat_id']

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }

        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"❌ Message error: {e}")
        return False


def send_telegram_video(video_path: str, caption: str):
    """Upload video to Telegram channel"""
    try:
        bot_token = config['telegram']['bot_token']
        chat_id = config['telegram']['chat_id']

        url = f"https://api.telegram.org/bot{bot_token}/sendVideo"

        with open(video_path, 'rb') as video:
            files = {'video': video}
            data = {
                'chat_id': chat_id,
                'caption': caption,
                'parse_mode': 'HTML'
            }

            logger.info(f"📤 Uploading: {Path(video_path).name}")
            response = requests.post(url, data=data, files=files, timeout=300)

            if response.status_code == 200:
                logger.info("✅ Video uploaded!")
                return True
            else:
                logger.error(f"❌ Upload failed")
                return False
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        return False


def check_user_live(username: str) -> bool:
    """
    Check if user is live using the exact method from tiktok-live-recorder
    """
    try:
        # Step 1: Get signed URL from tikrec.com
        sign_url = f"https://tikrec.com/tiktok/room/api/sign?unique_id={username}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(sign_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return False

        signed_data = response.json()
        signed_path = signed_data.get("signed_path")
        if not signed_path:
            return False

        # Step 2: Get room info
        room_url = f"https://www.tiktok.com{signed_path}"
        response = requests.get(room_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return False

        room_data = response.json()
        room_id = room_data.get("data", {}).get("user", {}).get("roomId")
        if not room_id:
            return False

        # Step 3: Check if room is alive
        check_url = (
            f"https://webcast.tiktok.com/webcast/room/check_alive/"
            f"?aid=1988&region=CH&room_ids={room_id}&user_is_login=true"
        )

        response = requests.get(check_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return False

        check_data = response.json()
        if "data" in check_data and len(check_data["data"]) > 0:
            is_alive = check_data["data"][0].get("alive", False)
            return is_alive

        return False

    except Exception as e:
        logger.debug(f"Check error for {username}: {e}")
        return False


def find_latest_video(username: str) -> str:
    """Find latest video file"""
    try:
        video_extensions = ['.mp4', '.mkv', '.flv', '.ts']
        video_files = []

        for ext in video_extensions:
            # Try multiple patterns to catch different naming formats
            patterns = [
                f"{username}*{ext}",      # vasya.tv8*.mp4
                f"*{username}*{ext}",     # TK_vasya.tv8*.mp4
                f"TK_{username}*{ext}"    # TK_vasya.tv8*.mp4 (explicit)
            ]

            for pattern in patterns:
                files = list(Path(OUTPUT_DIR).glob(pattern))
                video_files.extend(files)

        # Remove duplicates
        video_files = list(set(video_files))

        if video_files:
            latest = max(video_files, key=lambda p: p.stat().st_mtime)
            return str(latest)

        return None
    except Exception as e:
        logger.error(f"❌ Find video error: {e}")
        return None


def start_recording(username: str):
    """Start recording a live stream"""
    if not Path(RECORDER_PATH).exists():
        logger.error(f"❌ Recorder not found")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cmd = [
        sys.executable,
        RECORDER_PATH,
        username,  # username (no -user flag)
        OUTPUT_DIR,  # output directory
        "10"  # check interval in minutes
    ]

    try:
        logger.info(f"🎬 Starting recording: {username}")

        send_telegram_message(
            f"🔴 <b>{username}</b> is LIVE!\n"
            f"📹 Recording started\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}\n"
            f"Link: https://www.tiktok.com/@{username}/live"
        )

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        with recordings_lock:
            active_recordings[username] = process

        # Monitor in background
        Thread(target=monitor_recording, args=(username, process), daemon=True).start()

    except Exception as e:
        logger.error(f"❌ Recording error: {e}")


def monitor_recording(username: str, process: subprocess.Popen):
    """Monitor recording and upload when done"""
    try:
        stdout, stderr = process.communicate()

        # Log recorder output
        if stdout:
            logger.info(f"📝 Recorder output for {username}:\n{stdout}")
        if stderr:
            logger.error(f"❌ Recorder errors for {username}:\n{stderr}")

        with recordings_lock:
            if username in active_recordings:
                del active_recordings[username]

        logger.info(f"✅ Recording completed: {username}")

        # Find and upload video
        video_file = find_latest_video(username)

        if video_file:
            caption = (
                f"📹 <b>{username}</b> - Live Recording\n"
                f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            if send_telegram_video(video_file, caption):
                logger.info(f"✅ Uploaded: {username}")
            else:
                send_telegram_message(f"⚠️ Recording saved but upload failed: {username}")
        else:
            logger.warning(f"⚠️ No video found: {username}")

    except Exception as e:
        logger.error(f"❌ Monitor error: {e}")
        with recordings_lock:
            if username in active_recordings:
                del active_recordings[username]


def monitoring_loop():
    """Main monitoring loop"""
    logger.info("🔍 Monitoring started")

    checked = {}  # Track who we've notified about

    while True:
        try:
            if not monitoring_enabled:
                time.sleep(10)
                continue

            if not monitoring_users:
                time.sleep(config['recording']['check_interval'])
                continue

            for username in monitoring_users[:]:
                with recordings_lock:
                    if username in active_recordings:
                        continue  # Already recording

                # Check if live
                logger.info(f"🔍 Checking {username}...")
                is_live = check_user_live(username)
                logger.info(f"📊 {username}: {'🔴 LIVE' if is_live else '⚫ offline'}")

                if is_live and username not in checked:
                    # Just went live!
                    logger.info(f"🔴 {username} is LIVE - starting recording!")
                    checked[username] = True
                    start_recording(username)

                elif not is_live and username in checked:
                    # Stream ended
                    logger.info(f"⚫ {username} stream ended")
                    del checked[username]

                time.sleep(2)

            # Wait before next check
            time.sleep(config['recording']['check_interval'])

        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")
            time.sleep(30)


# ===== TELEGRAM BOT COMMANDS =====

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start"""
    logger.info(f"✅ START from {update.effective_user.username}")
    await update.message.reply_text(
        "🎬 <b>TikTok Live Monitor & Recorder</b>\n\n"
        "Commands:\n"
        "/add username - Add user to monitor\n"
        "/remove username - Remove user\n"
        "/list - Show monitored users\n"
        "/status - Show status\n"
        "/stop username - Stop recording and send video",
        parse_mode='HTML'
    )


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add"""
    logger.info(f"✅ ADD from {update.effective_user.username}")

    if not context.args:
        await update.message.reply_text("Usage: /add username")
        return

    username = context.args[0].strip().lstrip('@')

    if username in monitoring_users:
        await update.message.reply_text(f"ℹ️ Already monitoring @{username}")
        return

    monitoring_users.append(username)
    save_monitoring_list()

    await update.message.reply_text(f"✅ Added @{username}")
    logger.info(f"Added: {username}")


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /remove"""
    logger.info(f"✅ REMOVE from {update.effective_user.username}")

    if not context.args:
        await update.message.reply_text("Usage: /remove username")
        return

    username = context.args[0].strip().lstrip('@')

    if username not in monitoring_users:
        await update.message.reply_text(f"ℹ️ Not monitoring @{username}")
        return

    monitoring_users.remove(username)
    save_monitoring_list()

    await update.message.reply_text(f"✅ Removed @{username}")
    logger.info(f"Removed: {username}")


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list"""
    logger.info(f"✅ LIST from {update.effective_user.username}")

    if not monitoring_users:
        await update.message.reply_text("📋 No users monitored")
        return

    users_text = "\n".join([f"• @{u}" for u in sorted(monitoring_users)])
    await update.message.reply_text(
        f"📋 <b>Monitored ({len(monitoring_users)}):</b>\n\n{users_text}",
        parse_mode='HTML'
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status"""
    logger.info(f"✅ STATUS from {update.effective_user.username}")

    with recordings_lock:
        active = list(active_recordings.keys())

    message = (
        f"📊 <b>Status</b>\n\n"
        f"Users tracked: {len(monitoring_users)}\n"
        f"Active recordings: {len(active)}"
    )

    if active:
        active_text = "\n".join([f"🔴 @{u}" for u in active])
        message += f"\n\n<b>Recording:</b>\n{active_text}"

    await update.message.reply_text(message, parse_mode='HTML')


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop - Stop recording and send video"""
    logger.info(f"✅ STOP from {update.effective_user.username}")

    if not context.args:
        await update.message.reply_text("Usage: /stop username")
        return

    username = context.args[0].strip().lstrip('@')

    with recordings_lock:
        if username not in active_recordings:
            await update.message.reply_text(f"ℹ️ No active recording for @{username}")
            return

        # Get the process
        process = active_recordings[username]

        # Terminate the recording
        try:
            process.terminate()
            logger.info(f"🛑 Stopped recording for {username}")
            await update.message.reply_text(f"⏹️ Stopping recording for @{username}...\n📤 Uploading video...")

            # Wait a moment for file to finalize
            time.sleep(2)

            # Remove from active recordings
            del active_recordings[username]

            # Find and upload the latest video
            video_file = find_latest_video(username)

            if video_file:
                caption = (
                    f"📹 <b>{username}</b> - Manual Stop\n"
                    f"Stopped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )

                if send_telegram_video(video_file, caption):
                    await update.message.reply_text(f"✅ Video uploaded for @{username}")
                    logger.info(f"✅ Uploaded manually stopped recording: {username}")
                else:
                    await update.message.reply_text(f"⚠️ Recording saved but upload failed: {username}")
            else:
                await update.message.reply_text(f"⚠️ No video found for @{username}")
                logger.warning(f"⚠️ No video found for {username}")

        except Exception as e:
            logger.error(f"❌ Error stopping recording: {e}")
            await update.message.reply_text(f"❌ Error stopping recording: {str(e)}")


def main():
    """Main entry point"""

    print("""
╔═══════════════════════════════════════════════════════════╗
║     TikTok Live Monitor - FINAL WORKING VERSION!          ║
║     Real detection + Auto recording + Telegram upload     ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # Load config
    load_config()
    load_monitoring_list()

    # Check recorder
    if not Path(RECORDER_PATH).exists():
        logger.error("❌ Recorder not found! Run ./setup.sh")
        return

    # Start monitoring thread
    logger.info("🚀 Starting monitoring...")
    monitor_thread = Thread(target=monitoring_loop, daemon=True)
    monitor_thread.start()
    logger.info("✅ Monitoring started!")

    # Build bot
    bot_token = config['telegram']['bot_token']
    application = Application.builder().token(bot_token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("remove", remove_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("stop", stop_command))

    logger.info("✅ Bot started - send /start to @tiksnzbot")

    # Run
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
