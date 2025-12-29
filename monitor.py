#!/usr/bin/env python3
"""
TikTok Live Monitor and Recorder
Monitors TikTok users for live streams, records them, and uploads to Telegram
"""

import json
import subprocess
import time
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
import requests
from typing import Dict, List, Set

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
        self.active_recordings: Set[str] = set()
        self.recorded_streams: Dict[str, Set[str]] = {}
        self.recorder_path = None

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

        logger.error("tiktok-live-recorder not found. Please clone it first.")
        logger.error("Run: git clone https://github.com/Michele0303/tiktok-live-recorder")
        sys.exit(1)

    def check_live_status(self, username: str) -> bool:
        """
        Check if a user is currently live
        Uses TikTok's API to check live status
        """
        try:
            url = f"https://www.tiktok.com/@{username}/live"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)

            # Simple check - if the page contains specific live indicators
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

        output_dir = self.config['recording']['output_directory']
        os.makedirs(output_dir, exist_ok=True)

        cmd = [
            sys.executable,
            self.recorder_path,
            "-user", username,
            "-output", output_dir
        ]

        # Add optional parameters
        if self.config['recording'].get('duration', 0) > 0:
            cmd.extend(["-duration", str(self.config['recording']['duration'])])

        if self.config['recording'].get('automatic_interval'):
            cmd.extend(["-automatic", str(self.config['recording']['automatic_interval'])])

        if self.config['proxy']['enabled'] and self.config['proxy']['http_proxy']:
            cmd.extend(["-proxy", self.config['proxy']['http_proxy']])

        try:
            logger.info(f"Starting recording for {username}")
            self.active_recordings.add(username)

            # Send Telegram notification
            self.send_telegram_message(
                f"🔴 <b>{username}</b> is now LIVE!\n"
                f"Recording started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # Start recording process in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Monitor the recording process
            self.monitor_recording_process(username, process, output_dir)

        except Exception as e:
            logger.error(f"Error starting recording for {username}: {e}")
            self.active_recordings.discard(username)

    def monitor_recording_process(self, username: str, process: subprocess.Popen, output_dir: str):
        """Monitor the recording process and handle completion"""
        try:
            # Wait for process to complete
            stdout, stderr = process.communicate()

            self.active_recordings.discard(username)

            if process.returncode == 0:
                logger.info(f"Recording completed for {username}")

                # Find the latest video file
                video_file = self.find_latest_video(output_dir, username)

                if video_file:
                    # Upload to Telegram
                    caption = (
                        f"📹 <b>{username}</b> - Live Stream Recording\n"
                        f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )

                    self.send_telegram_video(video_file, caption)
                else:
                    logger.warning(f"No video file found for {username}")

            else:
                logger.error(f"Recording failed for {username}: {stderr}")
                self.send_telegram_message(
                    f"❌ Recording failed for <b>{username}</b>"
                )

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
                # Get the most recent file
                latest_file = max(video_files, key=lambda p: p.stat().st_mtime)
                return str(latest_file)

            return None

        except Exception as e:
            logger.error(f"Error finding video file: {e}")
            return None

    def monitor_users(self):
        """Main monitoring loop"""
        logger.info("Starting TikTok Live Monitor")
        logger.info(f"Monitoring users: {', '.join(self.config['tiktok_users'])}")

        check_interval = self.config['recording']['check_interval']

        while True:
            try:
                for username in self.config['tiktok_users']:
                    if username not in self.active_recordings:
                        is_live = self.check_live_status(username)

                        if is_live:
                            logger.info(f"{username} is LIVE!")
                            # Start recording in a separate thread to avoid blocking
                            import threading
                            thread = threading.Thread(
                                target=self.start_recording,
                                args=(username,)
                            )
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


def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║         TikTok Live Monitor & Recorder                    ║
║         Automatically record and upload to Telegram       ║
╚═══════════════════════════════════════════════════════════╝
    """)

    monitor = TikTokMonitor()
    monitor.monitor_users()


if __name__ == "__main__":
    main()
