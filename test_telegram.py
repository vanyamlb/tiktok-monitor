#!/usr/bin/env python3
"""
Test script to verify Telegram bot configuration
"""

import json
import sys
import requests


def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found!")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Invalid JSON in config.json!")
        sys.exit(1)


def test_bot_token(bot_token):
    """Test if the bot token is valid"""
    print("\n[1/3] Testing bot token...")

    url = f"https://api.telegram.org/bot{bot_token}/getMe"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get('ok'):
            bot_info = data['result']
            print(f"✅ Bot token is valid!")
            print(f"   Bot name: {bot_info['first_name']}")
            print(f"   Bot username: @{bot_info['username']}")
            return True
        else:
            print(f"❌ Bot token is invalid!")
            print(f"   Error: {data.get('description', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Error connecting to Telegram API: {e}")
        return False


def test_send_message(bot_token, chat_id):
    """Test sending a message to the channel"""
    print("\n[2/3] Testing channel access...")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    data = {
        'chat_id': chat_id,
        'text': '🧪 <b>Test Message</b>\n\nYour TikTok Live Monitor is configured correctly!',
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, data=data, timeout=10)
        result = response.json()

        if result.get('ok'):
            print(f"✅ Successfully sent test message to channel!")
            print(f"   Message ID: {result['result']['message_id']}")
            return True
        else:
            print(f"❌ Failed to send message!")
            error_desc = result.get('description', 'Unknown error')
            print(f"   Error: {error_desc}")

            if 'chat not found' in error_desc.lower():
                print("\n   💡 Tips:")
                print("   - Make sure the chat_id is correct")
                print("   - For public channels, use: @channel_username")
                print("   - For private channels, use the numeric ID: -1001234567890")
            elif 'bot was blocked' in error_desc.lower():
                print("\n   💡 Tips:")
                print("   - Make sure the bot is added to the channel")
                print("   - Make sure the bot is an administrator")
            elif 'not enough rights' in error_desc.lower():
                print("\n   💡 Tips:")
                print("   - Make sure the bot is an administrator in the channel")
                print("   - Give the bot permission to post messages")

            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_channel_info(bot_token, chat_id):
    """Get information about the channel"""
    print("\n[3/3] Getting channel information...")

    url = f"https://api.telegram.org/bot{bot_token}/getChat"

    data = {
        'chat_id': chat_id
    }

    try:
        response = requests.post(url, data=data, timeout=10)
        result = response.json()

        if result.get('ok'):
            chat = result['result']
            print(f"✅ Channel info retrieved!")
            print(f"   Type: {chat['type']}")
            print(f"   Title: {chat.get('title', 'N/A')}")
            if 'username' in chat:
                print(f"   Username: @{chat['username']}")
            return True
        else:
            print(f"⚠️  Could not retrieve channel info")
            print(f"   (This is okay if the message was sent successfully)")
            return True

    except Exception as e:
        print(f"⚠️  Could not retrieve channel info: {e}")
        print(f"   (This is okay if the message was sent successfully)")
        return True


def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║           Telegram Configuration Test                     ║
╚═══════════════════════════════════════════════════════════╝
    """)

    config = load_config()

    bot_token = config['telegram']['bot_token']
    chat_id = config['telegram']['chat_id']

    if bot_token == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please update your bot_token in config.json!")
        sys.exit(1)

    if chat_id == "YOUR_CHANNEL_ID_HERE":
        print("❌ Please update your chat_id in config.json!")
        sys.exit(1)

    # Run tests
    token_valid = test_bot_token(bot_token)

    if not token_valid:
        print("\n❌ Bot token test failed. Please check your configuration.")
        sys.exit(1)

    message_sent = test_send_message(bot_token, chat_id)

    if message_sent:
        test_channel_info(bot_token, chat_id)
        print("\n" + "="*60)
        print("✅ All tests passed! Your Telegram configuration is correct.")
        print("="*60)
        print("\nYou can now run: python3 monitor.py")
    else:
        print("\n" + "="*60)
        print("❌ Tests failed. Please fix the issues above.")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
