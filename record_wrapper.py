#!/usr/bin/env python3
"""
Wrapper to bypass tiktok-live-recorder main.py issues
"""
import sys
import os
import multiprocessing

# Add recorder to path
recorder_path = os.path.join(os.path.dirname(__file__), 'tiktok-live-recorder', 'src')
sys.path.insert(0, recorder_path)

def record_user(user, output, interval):
    """Record a user's live stream"""
    from core.tiktok_recorder import TikTokRecorder
    from utils.enums import Mode
    from utils.utils import read_cookies

    # Read cookies
    try:
        cookies = read_cookies()
    except:
        cookies = {}

    # Create recorder
    recorder = TikTokRecorder(
        url=None,
        user=user,
        room_id=None,
        mode=Mode.AUTOMATIC,
        automatic_interval=interval,
        cookies=cookies,
        proxy=None,
        output=output,
        duration=None,
        use_telegram=False
    )

    # Run recorder
    recorder.run()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: record_wrapper.py <username> <output_dir> <interval>")
        sys.exit(1)

    username = sys.argv[1]
    output_dir = sys.argv[2]
    interval = int(sys.argv[3])

    multiprocessing.freeze_support()
    record_user(username, output_dir, interval)
