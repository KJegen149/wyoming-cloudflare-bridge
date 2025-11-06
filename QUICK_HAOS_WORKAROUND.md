# Quick Home Assistant OS Workaround

**For users who want to test RIGHT NOW without waiting for GitHub setup.**

## Limitations

- Manual setup (no add-on)
- Runs in terminal (stops when terminal closes)
- No auto-start
- For testing only

## Better Solution

See [HOME_ASSISTANT_OS_SETUP.md](HOME_ASSISTANT_OS_SETUP.md) for the proper add-on approach.

## Quick Steps

### 1. Deploy Cloudflare Workers

From your computer:

```bash
cd wyoming-cloudflare-bridge
npm install -g wrangler
wrangler login
./deploy.sh
```

**Save the URLs!** You'll need them.

### 2. Install Terminal Add-on in HA

1. Settings → Add-ons → Add-on Store
2. Search "Terminal & SSH"
3. Install "Terminal & SSH"
4. Configuration tab:
   ```yaml
   password: "your-password-here"
   ```
5. Save, then Start
6. Click "Open Web UI"

### 3. Install Python Dependencies

In the terminal:

```bash
apk add --no-cache python3 py3-pip
pip3 install wyoming aiohttp
```

### 4. Create Server Files

```bash
mkdir -p /config/wyoming-bridge
cd /config/wyoming-bridge
```

Create `__init__.py`:
```bash
cat > __init__.py << 'EOF'
"""Wyoming Cloudflare Bridge server."""
__version__ = "1.0.0"
EOF
```

Create `__main__.py` (copy from your repo, or use wget if on GitHub):
```bash
# If on GitHub:
wget https://raw.githubusercontent.com/YOUR_USERNAME/wyoming-cloudflare-bridge/main/server/__main__.py

# Or create manually:
nano __main__.py
# Paste the content from server/__main__.py
# Ctrl+X, Y, Enter to save
```

Create `handler.py`:
```bash
# If on GitHub:
wget https://raw.githubusercontent.com/YOUR_USERNAME/wyoming-cloudflare-bridge/main/server/handler.py

# Or create manually:
nano handler.py
# Paste the content from server/handler.py
# Ctrl+X, Y, Enter to save
```

### 5. Run the Bridge

```bash
cd /config/wyoming-bridge

python3 -m . \
  --uri tcp://0.0.0.0:10300 \
  --stt-url "https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev" \
  --tts-url "https://wyoming-tts.YOUR-SUBDOMAIN.workers.dev"
```

**Replace the URLs with your actual Cloudflare Worker URLs!**

You should see:
```
Starting Wyoming Cloudflare Bridge
STT URL: https://wyoming-stt...
TTS URL: https://wyoming-tts...
Listening on: tcp://0.0.0.0:10300
```

### 6. Add Wyoming Integration (New Terminal Tab)

The terminal is now occupied. Open Home Assistant in another tab:

1. Settings → Devices & Services → Add Integration
2. Search "Wyoming Protocol"
3. Enter:
   - Host: `localhost` or `127.0.0.1`
   - Port: `10300`
4. Submit

### 7. Create Voice Assistant

1. Settings → Voice Assistants → Add Assistant
2. Configure:
   - Name: "Cloudflare Assistant"
   - STT: cloudflare-whisper
   - TTS: cloudflare-aura
3. Create

### 8. Test

Configure your satellite to connect to your Home Assistant IP on port 10300, then test a voice command!

## Problems with This Approach

❌ **No auto-start**: You have to manually start it every time
❌ **Terminal must stay open**: Closing terminal stops the service
❌ **No persistence**: Restarts lose the service
❌ **Manual management**: No HA integration for logs/status

## Next Steps

This works for testing, but you should:

1. **Test that everything works**
2. **Then set up the proper add-on** (see PUBLISH_ADDON.md)
3. **Install the add-on** for permanent, managed deployment

The add-on gives you:
- ✅ Auto-start with Home Assistant
- ✅ Runs in background
- ✅ Proper logging in HA UI
- ✅ Easy configuration
- ✅ Survives restarts

## Alternative: Enable SSH Properly

Instead of this workaround, you can:

1. Install "Terminal & SSH" add-on
2. Enable SSH on port 22222
3. Connect via SSH from your computer
4. Follow the normal installation steps

See [HOME_ASSISTANT_OS_SETUP.md](HOME_ASSISTANT_OS_SETUP.md) Option 1.

## Keeping It Running

If you want to keep the bridge running in the background (hack):

```bash
# Install screen
apk add screen

# Start in detached screen
cd /config/wyoming-bridge
screen -dmS wyoming python3 -m . \
  --uri tcp://0.0.0.0:10300 \
  --stt-url "YOUR_STT_URL" \
  --tts-url "YOUR_TTS_URL"

# Check it's running
screen -ls

# Attach to see logs
screen -r wyoming

# Detach: Ctrl+A, then D
```

But seriously, use the proper add-on instead!
