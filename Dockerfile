FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clone tiktok-live-recorder
RUN git clone https://github.com/Michele0303/tiktok-live-recorder && \
    cd tiktok-live-recorder/src && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create recordings directory
RUN mkdir -p recordings

# Run the bot
CMD ["python3", "monitor_bot.py"]
