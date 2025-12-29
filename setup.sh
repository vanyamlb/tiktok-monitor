#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     TikTok Live Monitor & Recorder - Setup Script        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi
echo "✅ Python is installed"
echo ""

# Check FFmpeg
echo "[2/5] Checking FFmpeg..."
ffmpeg -version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ FFmpeg is not installed."
    echo "Please install it:"
    echo "  macOS: brew install ffmpeg"
    echo "  Linux: sudo apt install ffmpeg"
    exit 1
fi
echo "✅ FFmpeg is installed"
echo ""

# Clone tiktok-live-recorder
echo "[3/5] Cloning tiktok-live-recorder..."
if [ -d "tiktok-live-recorder" ]; then
    echo "⚠️  tiktok-live-recorder already exists, skipping..."
else
    git clone https://github.com/Michele0303/tiktok-live-recorder
    if [ $? -ne 0 ]; then
        echo "❌ Failed to clone tiktok-live-recorder"
        exit 1
    fi
    echo "✅ tiktok-live-recorder cloned"
fi
echo ""

# Install recorder dependencies
echo "[4/5] Installing tiktok-live-recorder dependencies..."
cd tiktok-live-recorder/src
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install tiktok-live-recorder dependencies"
    exit 1
fi
cd ../..
echo "✅ Recorder dependencies installed"
echo ""

# Install monitor dependencies
echo "[5/5] Installing monitor dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install monitor dependencies"
    exit 1
fi
echo "✅ Monitor dependencies installed"
echo ""

# Create recordings directory
mkdir -p recordings

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                  Setup Complete! ✅                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit config.json with your Telegram bot token and channel ID"
echo "2. Add TikTok usernames to monitor in config.json"
echo "3. Run: python3 monitor.py"
echo ""
echo "For detailed setup instructions, see README.md"
