# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Cloudflare account (free)
- Docker and Docker Compose installed
- Home Assistant running
- Wyoming Satellite device(s)

## 1. Clone and Deploy (2 minutes)

```bash
# Navigate to your project directory
cd wyoming-cloudflare-bridge

# Install Wrangler and login
npm install -g wrangler
wrangler login

# Deploy workers automatically
./deploy.sh
```

This will:
- Deploy STT and TTS workers to Cloudflare
- Create `.env` file with worker URLs
- Display next steps

## 2. Start Bridge Server (30 seconds)

```bash
docker-compose up -d
```

Check it's running:
```bash
docker-compose logs -f
```

You should see:
```
Starting Wyoming Cloudflare Bridge
STT URL: https://wyoming-stt.YOUR_SUBDOMAIN.workers.dev
TTS URL: https://wyoming-tts.YOUR_SUBDOMAIN.workers.dev
Listening on: tcp://0.0.0.0:10300
```

## 3. Add to Home Assistant (1 minute)

1. Open Home Assistant
2. Go to **Settings** → **Devices & Services**
3. Click **+ Add Integration**
4. Search for "Wyoming Protocol"
5. Enter:
   - **Host**: Your server's IP (e.g., `192.168.1.100`)
   - **Port**: `10300`
6. Click **Submit**

## 4. Create Voice Assistant (1 minute)

1. Go to **Settings** → **Voice Assistants**
2. Click **+ Add Assistant**
3. Give it a name (e.g., "Cloudflare Assistant")
4. Configure:
   - **Speech-to-Text**: cloudflare-whisper
   - **Text-to-Speech**: cloudflare-aura
   - **Conversation**: Home Assistant Conversation
5. Click **Create**

## 5. Configure Satellite (30 seconds)

On your Wyoming Satellite device:

```bash
python -m wyoming_satellite \
  --name "Living Room" \
  --uri "tcp://YOUR_BRIDGE_SERVER_IP:10300" \
  --mic-command "arecord -r 16000 -c 1 -f S16_LE -t raw" \
  --snd-command "aplay -r 22050 -c 1 -f S16_LE -t raw"
```

Replace `YOUR_BRIDGE_SERVER_IP` with your bridge server's IP address.

## 6. Test It! (30 seconds)

Say to your satellite:
- "Hey Mycroft" (or your wake word)
- "Turn on the living room lights"

You should hear a response!

## Troubleshooting

### Bridge server not starting

```bash
# Check logs
docker-compose logs

# Verify .env file exists
cat .env
```

### Home Assistant can't connect

```bash
# Test connection from Home Assistant server
nc -zv YOUR_BRIDGE_SERVER_IP 10300

# If fails, check firewall
sudo ufw allow 10300
```

### Satellite can't connect

```bash
# Test from satellite device
nc -zv YOUR_BRIDGE_SERVER_IP 10300

# Check bridge server logs
docker-compose logs -f
```

### No transcription

```bash
# Enable debug logging
echo "LOG_LEVEL=DEBUG" >> .env
docker-compose restart

# Watch logs
docker-compose logs -f
```

## What's Next?

- Add more satellites
- Customize TTS voice (see README.md)
- Set up wake word detection locally
- Monitor usage in Cloudflare dashboard

## Resources

- Full documentation: `README.md`
- Wyoming Protocol: https://github.com/OHF-Voice/wyoming
- Home Assistant Voice: https://www.home-assistant.io/voice_control/
