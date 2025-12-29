#!/usr/bin/env python3
"""
TikTok Live Monitor with Telegram Bot Control
Monitor TikTok users for live streams with interactive Telegram bot commands
"""

import json
import subprocess
import time
import logging
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
import requests
from typing import Dict, List, Set
from threading import Thread, Lock

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tiktok_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TikTokMonitor:
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.config_path = config_path
        self.active_recordings: Set[str] = set()
        self.recorder_path = None
        self.monitoring_enabled = True
        self.lock = Lock()

        # Load or create monitoring list
        self.monitoring_list_file = "monitoring_list.json"
        self.load_monitoring_list()

    def load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info("Configuration loaded successfully")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            sys.exit(1)

    def load_monitoring_list(self):
        """Load monitoring list from file or create from config"""
        try:
            if os.path.exists(self.monitoring_list_file):
                with open(self.monitoring_list_file, 'r') as f:
                    data = json.load(f)
                    self.monitoring_users = set(data.get('users', []))
                logger.info(f"Loaded {len(self.monitoring_users)} users from monitoring list")
            else:
                # Initialize from config
                self.monitoring_users = set(self.config.get('tiktok_users', []))
                self.save_monitoring_list()
                logger.info(f"Created new monitoring list with {len(self.monitoring_users)} users")
        except Exception as e:
            logger.error(f"Error loading monitoring list: {e}")
            self.monitoring_users = set()

    def save_monitoring_list(self):
        """Save monitoring list to file"""
        try:
            with self.lock:
                data = {
                    'users': list(self.monitoring_users),
                    'last_updated': datetime.now().isoformat()
                }
                with open(self.monitoring_list_file, 'w') as f:
                    json.dump(data, f, indent=2)
            logger.info("Monitoring list saved")
        except Exception as e:
            logger.error(f"Error saving monitoring list: {e}")

    def add_user(self, username: str) -> bool:
        """Add a user to monitoring list"""
        username = username.strip().lstrip('@')
        if not username:
            return False

        with self.lock:
            if username not in self.monitoring_users:
                self.monitoring_users.add(username)
                self.save_monitoring_list()
                logger.info(f"Added {username} to monitoring list")
                return True
            return False

    def remove_user(self, username: str) -> bool:
        """Remove a user from monitoring list"""
        username = username.strip().lstrip('@')
        with self.lock:
            if username in self.monitoring_users:
                self.monitoring_users.discard(username)
                self.save_monitoring_list()
                logger.info(f"Removed {username} from monitoring list")
                return True
            return False

    def get_monitoring_users(self) -> List[str]:
        """Get list of users being monitored"""
        with self.lock:
            return sorted(list(self.monitoring_users))

    def find_recorder(self) -> str:
        """Find the tiktok-live-recorder installation"""
        possible_paths = [
            "./tiktok-live-recorder/src/main.py",
            "../tiktok-live-recorder/src/main.py",
            "./src/main.py"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found tiktok-live-recorder at: {path}")
                return path

        logger.error("tiktok-live-recorder not found.")
        return None

    def check_live_status(self, username: str) -> bool:
        """Check if a user is currently live"""
        try:
            url = f"https://www.tiktok.com/@{username}/live"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            is_live = '"isLive":true' in response.text or 'LIVE' in response.text

            return is_live

        except Exception as e:
            logger.error(f"Error checking live status for {username}: {e}")
            return False

    def send_telegram_message(self, message: str):
        """Send a message to Telegram channel"""
        if not self.config['telegram']['enabled']:
            return

        try:
            bot_token = self.config['telegram']['bot_token']
            chat_id = self.config['telegram']['chat_id']

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info("Telegram notification sent")
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")

        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")

    def send_telegram_video(self, video_path: str, caption: str):
        """Upload video to Telegram channel"""
        if not self.config['telegram']['enabled']:
            return

        try:
            bot_token = self.config['telegram']['bot_token']
            chat_id = self.config['telegram']['chat_id']

            url = f"https://api.telegram.org/bot{bot_token}/sendVideo"

            with open(video_path, 'rb') as video:
                files = {'video': video}
                data = {
                    'chat_id': chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML'
                }

                logger.info(f"Uploading video to Telegram: {video_path}")
                response = requests.post(url, data=data, files=files, timeout=300)

                if response.status_code == 200:
                    logger.info("Video uploaded to Telegram successfully")
                    return True
                else:
                    logger.error(f"Failed to upload video: {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Error uploading video to Telegram: {e}")
            return False

    def start_recording(self, username: str):
        """Start recording a live stream"""
        if username in self.active_recordings:
            logger.info(f"Already recording {username}")
            return

        if not self.recorder_path:
            self.recorder_path = self.find_recorder()
            if not self.recorder_path:
                logger.error("Cannot start recording: recorder not found")
                return

        output_dir = self.config['recording']['output_directory']
        os.makedirs(output_dir, exist_ok=True)

        cmd = [
            sys.executable,
            self.recorder_path,
            "-user", username,
            "-output", output_dir
        ]

        if self.config['recording'].get('duration', 0) > 0:
            cmd.extend(["-duration", str(self.config['recording']['duration'])])

        if self.config['recording'].get('automatic_interval'):
            cmd.extend(["-automatic", str(self.config['recording']['automatic_interval'])])

        if self.config['proxy']['enabled'] and self.config['proxy']['http_proxy']:
            cmd.extend(["-proxy", self.config['proxy']['http_proxy']])

        try:
            logger.info(f"Starting recording for {username}")
            self.active_recordings.add(username)

            self.send_telegram_message(
                f"🔴 <b>{username}</b> is now LIVE!\n"
                f"Recording started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Monitor in separate thread
            thread = Thread(target=self.monitor_recording_process, args=(username, process, output_dir))
            thread.daemon = True
            thread.start()

        except Exception as e:
            logger.error(f"Error starting recording for {username}: {e}")
            self.active_recordings.discard(username)

    def monitor_recording_process(self, username: str, process: subprocess.Popen, output_dir: str):
        """Monitor the recording process and handle completion"""
        try:
            stdout, stderr = process.communicate()

            self.active_recordings.discard(username)

            if process.returncode == 0:
                logger.info(f"Recording completed for {username}")

                video_file = self.find_latest_video(output_dir, username)

                if video_file:
                    caption = (
                        f"📹 <b>{username}</b> - Live Stream Recording\n"
                        f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    self.send_telegram_video(video_file, caption)
                else:
                    logger.warning(f"No video file found for {username}")

            else:
                logger.error(f"Recording failed for {username}: {stderr}")
                self.send_telegram_message(f"❌ Recording failed for <b>{username}</b>")

        except Exception as e:
            logger.error(f"Error monitoring recording process for {username}: {e}")
            self.active_recordings.discard(username)

    def find_latest_video(self, output_dir: str, username: str) -> str:
        """Find the latest video file for a user"""
        try:
            video_extensions = ['.mp4', '.mkv', '.flv', '.ts']
            video_files = []

            for ext in video_extensions:
                pattern = f"{username}*{ext}"
                files = list(Path(output_dir).glob(pattern))
                video_files.extend(files)

            if video_files:
                latest_file = max(video_files, key=lambda p: p.stat().st_mtime)
                return str(latest_file)

            return None

        except Exception as e:
            logger.error(f"Error finding video file: {e}")
            return None

    def monitor_users(self):
        """Main monitoring loop"""
        logger.info("Starting TikTok Live Monitor")
        check_interval = self.config['recording']['check_interval']

        while True:
            try:
                if not self.monitoring_enabled:
                    time.sleep(5)
                    continue

                users = self.get_monitoring_users()

                if not users:
                    logger.debug("No users to monitor")
                    time.sleep(check_interval)
                    continue

                for username in users:
                    if username not in self.active_recordings:
                        is_live = self.check_live_status(username)

                        if is_live:
                            logger.info(f"{username} is LIVE!")
                            thread = Thread(target=self.start_recording, args=(username,))
                            thread.daemon = True
                            thread.start()
                        else:
                            logger.debug(f"{username} is not live")

                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Shutting down monitor...")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(check_interval)


# Global monitor instance
monitor = None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🎬 <b>TikTok Live Monitor Bot</b>\n\n"
        "Available commands:\n"
        "/add @username - Add TikTok user to monitor\n"
        "/remove @username - Remove user from monitoring\n"
        "/list - Show all monitored users\n"
        "/status - Show monitoring status\n"
        "/pause - Pause monitoring\n"
        "/resume - Resume monitoring\n"
        "/help - Show this message",
        parse_mode='HTML'
    )


async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /add command"""
    global monitor

    if not context.args:
        await update.message.reply_text("Usage: /add @username or /add username")
        return

    username = context.args[0].strip().lstrip('@')

    if monitor.add_user(username):
        await update.message.reply_text(
            f"✅ Added <b>@{username}</b> to monitoring list",
            parse_mode='HTML'
        )
        logger.info(f"User {update.effective_user.username} added {username}")
    else:
        await update.message.reply_text(
            f"ℹ️ <b>@{username}</b> is already being monitored",
            parse_mode='HTML'
        )


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /remove command"""
    global monitor

    if not context.args:
        await update.message.reply_text("Usage: /remove @username or /remove username")
        return

    username = context.args[0].strip().lstrip('@')

    if monitor.remove_user(username):
        await update.message.reply_text(
            f"✅ Removed <b>@{username}</b> from monitoring list",
            parse_mode='HTML'
        )
        logger.info(f"User {update.effective_user.username} removed {username}")
    else:
        await update.message.reply_text(
            f"ℹ️ <b>@{username}</b> is not in the monitoring list",
            parse_mode='HTML'
        )


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list command"""
    global monitor

    users = monitor.get_monitoring_users()

    if not users:
        await update.message.reply_text("📋 No users are currently being monitored")
        return

    user_list = "\n".join([f"• @{user}" for user in users])
    await update.message.reply_text(
        f"📋 <b>Monitored Users ({len(users)}):</b>\n\n{user_list}",
        parse_mode='HTML'
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    global monitor

    users = monitor.get_monitoring_users()
    active = list(monitor.active_recordings)

    status = "▶️ Running" if monitor.monitoring_enabled else "⏸ Paused"

    message = (
        f"📊 <b>Monitoring Status</b>\n\n"
        f"Status: {status}\n"
        f"Total users: {len(users)}\n"
        f"Active recordings: {len(active)}\n"
    )

    if active:
        active_list = "\n".join([f"🔴 @{user}" for user in active])
        message += f"\n<b>Currently recording:</b>\n{active_list}"

    await update.message.reply_text(message, parse_mode='HTML')


async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pause command"""
    global monitor

    monitor.monitoring_enabled = False
    await update.message.reply_text("⏸ Monitoring paused")
    logger.info(f"Monitoring paused by {update.effective_user.username}")


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /resume command"""
    global monitor

    monitor.monitoring_enabled = True
    await update.message.reply_text("▶️ Monitoring resumed")
    logger.info(f"Monitoring resumed by {update.effective_user.username}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await start_command(update, context)


def run_bot(bot_token: str):
    """Run the Telegram bot"""
    application = Application.builder().token(bot_token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("remove", remove_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("pause", pause_command))
    application.add_handler(CommandHandler("resume", resume_command))
    application.add_handler(CommandHandler("help", help_command))

    logger.info("Telegram bot started")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    global monitor

    print("""
╔═══════════════════════════════════════════════════════════╗
║   TikTok Live Monitor with Telegram Bot Control          ║
║   Control monitoring via Telegram commands               ║
╚═══════════════════════════════════════════════════════════╝
    """)

    monitor = TikTokMonitor()
    bot_token = monitor.config['telegram']['bot_token']

    # Start monitoring in separate thread
    monitor_thread = Thread(target=monitor.monitor_users)
    monitor_thread.daemon = True
    monitor_thread.start()

    # Run Telegram bot in main thread
    try:
        run_bot(bot_token)
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == "__main__":
    main()
