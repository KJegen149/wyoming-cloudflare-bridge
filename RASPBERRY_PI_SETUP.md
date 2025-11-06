# Raspberry Pi 5 Setup Guide

Deploy Wyoming Cloudflare Bridge on your Pi 5 **without Docker**.

## Architecture

```
Raspberry Pi 5 (192.168.x.x)
├── Home Assistant (port 8123)
├── Wyoming Bridge (port 10300) ← New!
└── Wake Word Detection (port 10400) ← Optional
       ↓
Wyoming Satellites (port 10300) ← Connect here
       ↓
Cloudflare Workers AI (cloud)
```

## Prerequisites

- Raspberry Pi 5 with Home Assistant already running
- Internet connection
- SSH access to your Pi

## Step 1: Deploy Cloudflare Workers (5 minutes)

### On Your Computer (not Pi)

```bash
# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login
# This will open a browser to authorize

# Navigate to the project
cd wyoming-cloudflare-bridge

# Deploy workers
./deploy.sh
```

This will output your worker URLs. **Save these!**

Example:
```
STT: https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev
TTS: https://wyoming-tts.YOUR-SUBDOMAIN.workers.dev
```

## Step 2: Install Bridge on Pi 5 (3 minutes)

### SSH into your Pi 5

```bash
ssh pi@YOUR_PI_IP
# Or however you access your Pi
```

### Install Dependencies

```bash
# Update system
sudo apt update
sudo apt install python3-pip python3-venv

# Create directory
sudo mkdir -p /opt/wyoming-cloudflare-bridge
cd /opt/wyoming-cloudflare-bridge

# Copy or download the server code
# Option A: If you have git
git clone https://github.com/YOUR_REPO/wyoming-cloudflare-bridge.git .

# Option B: Copy from your computer
# On your computer: scp -r server pi@YOUR_PI_IP:/tmp/
# On Pi: sudo mv /tmp/server /opt/wyoming-cloudflare-bridge/
```

### Install Python Dependencies

```bash
cd /opt/wyoming-cloudflare-bridge

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r server/requirements.txt
```

### Test It

```bash
# Replace with YOUR Cloudflare Worker URLs
python3 -m server \
  --uri tcp://0.0.0.0:10300 \
  --stt-url "https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev" \
  --tts-url "https://wyoming-tts.YOUR-SUBDOMAIN.workers.dev"
```

You should see:
```
Starting Wyoming Cloudflare Bridge
STT URL: https://wyoming-stt...
TTS URL: https://wyoming-tts...
Listening on: tcp://0.0.0.0:10300
```

Press `Ctrl+C` to stop. If it works, continue to create a service.

## Step 3: Create SystemD Service (2 minutes)

### Create Service File

```bash
sudo nano /etc/systemd/system/wyoming-cloudflare.service
```

Paste this content (replace YOUR_URLs):

```ini
[Unit]
Description=Wyoming Cloudflare Bridge
After=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/opt/wyoming-cloudflare-bridge
ExecStart=/opt/wyoming-cloudflare-bridge/venv/bin/python -m server \
  --uri tcp://0.0.0.0:10300 \
  --stt-url https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev \
  --tts-url https://wyoming-tts.YOUR-SUBDOMAIN.workers.dev \
  --log-level INFO
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save with `Ctrl+X`, `Y`, `Enter`

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable wyoming-cloudflare

# Start service now
sudo systemctl start wyoming-cloudflare

# Check status
sudo systemctl status wyoming-cloudflare
```

You should see "active (running)" in green.

### View Logs

```bash
# Follow logs in real-time
sudo journalctl -u wyoming-cloudflare -f

# View last 50 lines
sudo journalctl -u wyoming-cloudflare -n 50
```

## Step 4: Configure Home Assistant (2 minutes)

### Add Wyoming Integration

1. Open Home Assistant web interface
2. Go to **Settings** → **Devices & Services**
3. Click **+ Add Integration**
4. Search for "Wyoming Protocol"
5. Enter:
   - **Host**: `localhost` or `127.0.0.1` (since it's on the same Pi!)
   - **Port**: `10300`
6. Click **Submit**

You should see "Wyoming Protocol" added successfully!

### Create Voice Assistant

1. Go to **Settings** → **Voice Assistants**
2. Click **+ Add Assistant**
3. Name it: "Cloudflare Assistant"
4. Configure:
   - **Speech-to-Text**: cloudflare-whisper
   - **Text-to-Speech**: cloudflare-aura
   - **Conversation**: Home Assistant Conversation
5. Click **Create**

## Step 5: Configure Satellites (2 minutes)

### On Each Satellite Device

Point them to your **Pi 5's IP address** (not localhost!):

```bash
python3 -m wyoming_satellite \
  --name "Living Room Satellite" \
  --uri "tcp://YOUR_PI5_IP:10300" \
  --mic-command "arecord -r 16000 -c 1 -f S16_LE -t raw" \
  --snd-command "aplay -r 22050 -c 1 -f S16_LE -t raw"
```

Replace `YOUR_PI5_IP` with your Pi 5's IP (e.g., `192.168.1.100`)

## Step 6: Test! (1 minute)

Say to your satellite:
1. "Hey Mycroft" (or your wake word)
2. "What time is it?"

You should hear a response!

## Resource Usage

Running on Pi 5 alongside Home Assistant:

- **CPU**: ~2-5% idle, ~10-20% during voice commands
- **RAM**: ~50-100MB
- **Disk**: ~20MB

Your Pi 5 has plenty of power for this!

## Optional: Wake Word Detection on Pi 5

For better performance, run wake word detection locally on the Pi 5:

### Install OpenWakeWord

```bash
# In a new terminal
cd ~
git clone https://github.com/rhasspy/wyoming-openwakeword.git
cd wyoming-openwakeword

# Install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run it
python3 -m wyoming_openwakeword \
  --uri tcp://0.0.0.0:10400 \
  --preload-model hey_jarvis
```

### Update Satellites

```bash
python3 -m wyoming_satellite \
  --name "Living Room Satellite" \
  --uri "tcp://YOUR_PI5_IP:10300" \
  --wake-word-name "hey_jarvis" \
  --wake-word-uri "tcp://YOUR_PI5_IP:10400" \  # ← Added this
  --mic-command "arecord -r 16000 -c 1 -f S16_LE -t raw" \
  --snd-command "aplay -r 22050 -c 1 -f S16_LE -t raw"
```

This keeps wake word processing off satellites and off the cloud = faster!

## Troubleshooting

### Bridge won't start

```bash
# Check logs
sudo journalctl -u wyoming-cloudflare -n 50

# Test manually
cd /opt/wyoming-cloudflare-bridge
source venv/bin/activate
python3 -m server --stt-url "YOUR_STT_URL" --tts-url "YOUR_TTS_URL"
```

### Satellites can't connect

```bash
# Test from satellite
nc -zv YOUR_PI5_IP 10300

# Check firewall on Pi
sudo ufw allow 10300
```

### Home Assistant can't find integration

Since the bridge is on the same Pi as Home Assistant:
- Use `localhost` or `127.0.0.1` as the host
- Make sure service is running: `sudo systemctl status wyoming-cloudflare`

### Check worker status

```bash
# From your computer
cd wyoming-cloudflare-bridge/workers
wrangler tail wyoming-stt
```

## Management Commands

```bash
# View logs
sudo journalctl -u wyoming-cloudflare -f

# Restart service
sudo systemctl restart wyoming-cloudflare

# Stop service
sudo systemctl stop wyoming-cloudflare

# Disable service
sudo systemctl disable wyoming-cloudflare

# Check status
sudo systemctl status wyoming-cloudflare
```

## Updating

```bash
# Stop service
sudo systemctl stop wyoming-cloudflare

# Update code (if using git)
cd /opt/wyoming-cloudflare-bridge
git pull

# Or manually copy updated files
# scp -r server pi@YOUR_PI5_IP:/tmp/
# sudo cp -r /tmp/server /opt/wyoming-cloudflare-bridge/

# Update dependencies
source venv/bin/activate
pip install --upgrade -r server/requirements.txt

# Start service
sudo systemctl start wyoming-cloudflare
```

## Summary

You now have:
- ✅ Cloudflare Workers (cloud AI processing)
- ✅ Wyoming Bridge on Pi 5 (no Docker!)
- ✅ Home Assistant integration configured
- ✅ Satellites connected

**Total local resources on Pi 5**: Just one lightweight Python service!

No Docker containers, no heavy images, minimal overhead.

## Performance

Expected latency with this setup:
- **Wake word** (if local): 200-400ms
- **STT via Cloudflare**: 500-1000ms
- **Home Assistant intent**: 100-300ms
- **TTS via Cloudflare**: 500-1000ms
- **Total**: 2-4 seconds

This is comparable to or faster than commercial smart speakers!

## What's Next?

- Add more satellites (just point them to your Pi 5 IP)
- Customize voices (see README.md)
- Monitor usage in Cloudflare Dashboard
- Set up wake word detection for even faster response

## Need Help?

Check logs first:
```bash
sudo journalctl -u wyoming-cloudflare -f
```

Then review the main README.md for detailed troubleshooting.
