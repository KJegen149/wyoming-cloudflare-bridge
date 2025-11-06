# Setup Summary

Quick reference for deploying Wyoming Cloudflare Bridge.

## Choose Your Deployment Method

### Option 1: Raspberry Pi 5 (Recommended if you have Home Assistant on Pi)
**Guide**: [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md)

**Pros**:
- No Docker needed
- Minimal resource usage
- Same device as Home Assistant
- Easy to manage with systemd

**Requirements**:
- Raspberry Pi with Home Assistant
- SSH access to Pi
- ~100MB RAM, ~20MB disk

### Option 2: Docker (Any Linux server)
**Guide**: [README.md](README.md) → Docker sections

**Pros**:
- Easy deployment
- Isolated environment
- Works on any system with Docker

**Requirements**:
- Docker and Docker Compose
- Separate server or VM
- ~200MB RAM (Docker overhead)

### Option 3: Standalone Server (systemd)
**Guide**: [systemd/INSTALL.md](systemd/INSTALL.md)

**Pros**:
- Native performance
- SystemD management
- Works on any Linux distro

**Requirements**:
- Linux server with systemd
- Python 3.8+
- ~100MB RAM, ~20MB disk

## What You Need

### Required
- ✅ Cloudflare Account (free)
- ✅ Home Assistant (any deployment method)
- ✅ Wyoming Satellite device(s)

### Optional
- 🔧 Local wake word detection server (for speed)
- 🔧 Docker (only if you choose that method)

## Deployment Steps (All Methods)

### 1. Deploy Cloudflare Workers (5 min)

```bash
# From your computer
npm install -g wrangler
wrangler login
cd wyoming-cloudflare-bridge
./deploy.sh
```

**Output**: Two URLs you'll need later
- STT: `https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev`
- TTS: `https://wyoming-tts.YOUR-SUBDOMAIN.workers.dev`

### 2. Deploy Bridge Server

**Pi 5 Method** (Recommended):
```bash
# Copy to Pi
./deploy-to-pi.sh

# Follow RASPBERRY_PI_SETUP.md
```

**Docker Method**:
```bash
# Create .env with your URLs
cp .env.example .env
nano .env  # Add your worker URLs

# Start
docker-compose up -d
```

**SystemD Method**:
```bash
# Follow systemd/INSTALL.md
```

### 3. Configure Home Assistant (2 min)

1. Settings → Devices & Services → Add Integration
2. Search "Wyoming Protocol"
3. Enter:
   - Host: `localhost` (if on same Pi) or server IP
   - Port: `10300`
4. Create Voice Assistant:
   - Settings → Voice Assistants → Add
   - STT: cloudflare-whisper
   - TTS: cloudflare-aura

### 4. Configure Satellites (2 min)

Point them to your bridge server:

```bash
python3 -m wyoming_satellite \
  --name "Living Room" \
  --uri "tcp://YOUR_BRIDGE_IP:10300" \
  --mic-command "arecord -r 16000 -c 1 -f S16_LE -t raw" \
  --snd-command "aplay -r 22050 -c 1 -f S16_LE -t raw"
```

### 5. Test!

Say: "Hey Mycroft, what time is it?"

## Access Requirements

### Cloudflare
- Free account at https://dash.cloudflare.com/sign-up
- No credit card required
- Workers AI included in free tier

### Home Assistant
- No special access needed
- Wyoming integration is built-in
- Long-lived token NOT required for basic setup

### Local Resources

**Minimum** (Pi 5 / Native):
- CPU: 2 cores
- RAM: 512MB (100MB for bridge)
- Disk: 50MB
- Network: Any

**Docker** (adds overhead):
- CPU: 2 cores
- RAM: 1GB (200MB for bridge)
- Disk: 500MB
- Network: Any

**None required** (on cloud):
- Cloudflare Workers run on edge network
- No local AI processing needed
- Satellites can be low-power devices

## Costs

### Cloudflare Workers AI
- **Free tier**: 10,000 neurons/day
- **Capacity**: ~100-500 voice commands/day
- **Paid**: $0.011 per 1,000 neurons (if you exceed free tier)

### Local Resources
- **Power**: ~1-2W for bridge server on Pi
- **Network**: ~100KB per voice command

### Total Cost
**$0/month** for typical home use!

## Performance Targets

With all optimizations:
- Wake word: <500ms (local)
- STT: 500-1000ms
- Intent: 100-300ms
- TTS: 500-1000ms
- **Total: 2-4 seconds**

Comparable to Google Home!

## Troubleshooting Quick Reference

### Workers deployed but not responding
```bash
cd workers
wrangler tail wyoming-stt
# Check for errors
```

### Bridge won't start
```bash
# Docker
docker-compose logs -f

# Pi 5 / SystemD
sudo journalctl -u wyoming-cloudflare -f
```

### Satellites can't connect
```bash
# Test connectivity
nc -zv YOUR_BRIDGE_IP 10300

# Check firewall
sudo ufw allow 10300
```

### Home Assistant can't find integration
- Make sure bridge is running
- Check host/port are correct
- Try `localhost` if on same machine

## Next Steps

After basic setup:
1. **Performance**: Read [OPTIMIZATION.md](OPTIMIZATION.md)
2. **Wake word**: Set up local wake word detection
3. **Monitor**: Check Cloudflare Dashboard for usage
4. **Customize**: Change voices/models in workers

## Documentation Map

| File | Purpose | When to Read |
|------|---------|--------------|
| **RASPBERRY_PI_SETUP.md** | Pi 5 deployment | If you have HA on Pi |
| **QUICKSTART.md** | Fastest setup | Want running in 5 min |
| **README.md** | Complete reference | Detailed info needed |
| **OPTIMIZATION.md** | Performance tuning | Want faster response |
| **PROJECT_STRUCTURE.md** | Code overview | Understanding architecture |
| **systemd/INSTALL.md** | Native Linux install | SystemD deployment |
| This file | Overview | Choosing deployment method |

## Support

1. Check logs first
2. Review relevant setup guide
3. See troubleshooting sections
4. Open GitHub issue with logs

## Quick Commands

```bash
# Deploy everything
./deploy.sh                    # Deploy workers
./deploy-to-pi.sh             # Deploy to Pi (optional)

# Test
./test-worker.sh              # Test Cloudflare workers

# Manage (Docker)
docker-compose up -d          # Start
docker-compose logs -f        # View logs
docker-compose restart        # Restart

# Manage (Pi/SystemD)
sudo systemctl status wyoming-cloudflare   # Check status
sudo systemctl restart wyoming-cloudflare  # Restart
sudo journalctl -u wyoming-cloudflare -f   # View logs

# Monitor
wrangler tail wyoming-stt     # Watch STT worker
wrangler tail wyoming-tts     # Watch TTS worker
```

That's it! Choose your deployment method and follow the corresponding guide.
