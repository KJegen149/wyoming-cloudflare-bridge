# Wyoming Cloudflare Bridge

A Wyoming Protocol bridge that connects Home Assistant Wyoming Satellites to Cloudflare Workers AI for Speech-to-Text (Whisper) and Text-to-Speech (Deepgram Aura) processing.

## Features

- **Free Tier Friendly**: Uses Cloudflare Workers AI free tier (10,000 neurons/day)
- **Low Latency**: Cloudflare's global edge network for fast AI processing
- **Self-Hosted Control**: Run your own Wyoming bridge server
- **Wyoming Protocol**: Compatible with Home Assistant Wyoming Satellites
- **No API Keys Needed**: Uses Cloudflare Workers AI binding (included in free plan)

## Architecture

```
Wyoming Satellite (mic + speaker)
    ↓ Wyoming Protocol
Wyoming Bridge Server (Python)
    ↓ HTTP/REST
Cloudflare Workers AI (STT + TTS)
    ↓
Home Assistant (Intent Processing)
```

## Quick Start

> **🎯 Running Home Assistant on Raspberry Pi?** See [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md) for a simplified guide without Docker!

### Prerequisites

1. **Cloudflare Account** (free tier)
2. **Node.js and npm** (for deploying workers)
3. **Python 3.8+** (for bridge server) OR **Docker** (alternative)
4. **Home Assistant** with Wyoming integration
5. **Wyoming Satellite** devices

### Step 1: Deploy Cloudflare Workers

#### Install Wrangler CLI

```bash
npm install -g wrangler
wrangler login
```

#### Deploy STT Worker

```bash
cd workers
wrangler deploy --config wrangler-stt.toml
```

Note the deployed URL (e.g., `https://wyoming-stt.YOUR_SUBDOMAIN.workers.dev`)

#### Deploy TTS Worker

```bash
wrangler deploy --config wrangler-tts.toml
```

Note the deployed URL (e.g., `https://wyoming-tts.YOUR_SUBDOMAIN.workers.dev`)

### Step 2: Configure Environment

```bash
cd ..
cp .env.example .env
```

Edit `.env` and set your Cloudflare Worker URLs:

```env
STT_URL=https://wyoming-stt.YOUR_SUBDOMAIN.workers.dev
TTS_URL=https://wyoming-tts.YOUR_SUBDOMAIN.workers.dev
LOG_LEVEL=INFO
```

### Step 3: Run the Bridge Server

#### Option A: Docker (Recommended)

```bash
docker-compose up -d
```

#### Option B: Python Virtual Environment

```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m server --stt-url "$STT_URL" --tts-url "$TTS_URL" --uri tcp://0.0.0.0:10300
```

The bridge server will listen on `tcp://0.0.0.0:10300` by default.

### Step 4: Configure Home Assistant

#### Add Wyoming Integration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Wyoming Protocol**
4. Enter the IP address of your bridge server and port `10300`

#### Configure Voice Assistant

1. Go to **Settings** → **Voice Assistants**
2. Click **Add Assistant**
3. Configure:
   - **Speech-to-Text**: Select "cloudflare-whisper"
   - **Text-to-Speech**: Select "cloudflare-aura"
   - **Conversation**: Select your preferred conversation agent (e.g., Home Assistant Conversation)

### Step 5: Configure Wyoming Satellite

On your Wyoming Satellite device, configure it to connect to your bridge server:

```bash
python -m wyoming_satellite \
  --name "My Satellite" \
  --uri "tcp://BRIDGE_SERVER_IP:10300" \
  --mic-command "arecord -r 16000 -c 1 -f S16_LE -t raw" \
  --snd-command "aplay -r 22050 -c 1 -f S16_LE -t raw"
```

## Free Tier Limits

Cloudflare Workers AI free tier includes:

- **10,000 neurons per day** (resets at 00:00 UTC)
- No credit card required for free tier
- Suitable for moderate home use

### Estimating Usage

- **Whisper (STT)**: ~10-50 neurons per request (depends on audio length)
- **Aura (TTS)**: ~10-50 neurons per request (depends on text length)

With 10,000 neurons/day, you can handle approximately:
- **100-500 voice commands per day** (combined STT + TTS)

For a typical smart home, this is more than sufficient!

## Optimizing for Real-Time Performance

### 1. Wake Word Detection

**Run wake word detection locally** on the satellite or a local server to avoid unnecessary cloud calls:

```bash
# On satellite, use local wake word detection
python -m wyoming_satellite \
  --name "My Satellite" \
  --uri "tcp://BRIDGE_SERVER_IP:10300" \
  --wake-word-name "hey_mycroft" \
  --wake-word-uri "tcp://WAKE_WORD_SERVER:10400" \
  --mic-command "arecord -r 16000 -c 1 -f S16_LE -t raw" \
  --snd-command "aplay -r 22050 -c 1 -f S16_LE -t raw"
```

### 2. Use Cloudflare's Edge Network

Cloudflare Workers run on their global edge network, so requests are processed at the nearest data center. This minimizes latency.

### 3. Audio Settings

Use optimal audio settings to reduce processing time:

- **Sample Rate**: 16kHz (good balance of quality and speed)
- **Channels**: Mono (1 channel)
- **Format**: S16_LE (16-bit signed little-endian)

### 4. Monitor Latency

Enable debug logging to monitor performance:

```bash
LOG_LEVEL=DEBUG docker-compose up
```

Check logs for timing information:
```
INFO - Transcribing 32768 bytes of audio
INFO - Transcription: turn on the living room lights
```

## Troubleshooting

### "No audio data to transcribe"

- Check that your satellite is sending audio correctly
- Verify audio format settings match (16kHz, mono, S16_LE)

### "STT/TTS request timed out"

- Check internet connectivity
- Verify Cloudflare Worker URLs are correct
- Ensure Cloudflare Workers AI is enabled in your account

### "STT failed with status 500"

- Check Cloudflare Workers logs: `wrangler tail wyoming-stt`
- Verify AI binding is configured in wrangler.toml
- Ensure you're not exceeding daily neuron limits

### Home Assistant doesn't discover the integration

- Ensure the bridge server is running: `docker-compose ps`
- Check firewall rules allow port 10300
- Manually add the integration with the server's IP address

## Advanced Configuration

### Custom Port

```bash
docker-compose up -d
# Or with Python:
python -m server --uri tcp://0.0.0.0:8080 --stt-url "$STT_URL" --tts-url "$TTS_URL"
```

Update Home Assistant integration with the new port.

### Multiple Satellites

The bridge server supports multiple simultaneous satellite connections. Just point each satellite to the same bridge server.

### Different TTS Voice

Edit `workers/tts-worker.js` to use a different model:

```javascript
// Options: @cf/deepgram/aura-2-en, @cf/deepgram/aura-2-es, @cf/myshell/melotts
const response = await env.AI.run('@cf/deepgram/aura-2-en', {
  text: text,
});
```

Redeploy the worker:
```bash
cd workers
wrangler deploy --config wrangler-tts.toml
```

## Cost Monitoring

Monitor your Cloudflare Workers AI usage:

1. Go to Cloudflare Dashboard
2. Navigate to **Workers & Pages** → **Overview**
3. Check **Workers AI** usage

If you exceed the free tier, costs are:
- **$0.011 per 1,000 neurons** beyond the 10,000 daily limit

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [Wyoming Protocol](https://github.com/OHF-Voice/wyoming) by Rhasspy
- [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/)
- [Home Assistant](https://www.home-assistant.io/)
- OpenAI Whisper
- Deepgram Aura

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review logs: `docker-compose logs -f`
- Open an issue on GitHub
