# Wyoming Cloudflare Bridge Add-on

Connect your Wyoming Satellites to Cloudflare Workers AI for Speech-to-Text and Text-to-Speech processing.

## About

This add-on provides a Wyoming Protocol server that bridges your Home Assistant Wyoming Satellites to Cloudflare Workers AI, giving you:

- **Free AI processing** using Cloudflare's free tier (10,000 neurons/day)
- **Low latency** via Cloudflare's global edge network
- **No API keys** needed - uses Workers AI binding
- **Self-hosted control** over your voice pipeline

## Prerequisites

Before installing this add-on, you need to deploy two Cloudflare Workers:

### 1. Deploy Cloudflare Workers

On your computer (not on Home Assistant):

```bash
# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Clone or download the repository
git clone https://github.com/yourusername/wyoming-cloudflare-bridge
cd wyoming-cloudflare-bridge

# Deploy workers
./deploy.sh
```

This will output two URLs that you'll need for configuration:
- `https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev`
- `https://wyoming-tts.YOUR-SUBDOMAIN.workers.dev`

### 2. Save Your Worker URLs

You'll need these URLs for the add-on configuration.

## Installation

1. Navigate to **Settings** → **Add-ons** → **Add-on Store**
2. Click the menu (⋮) in the top right
3. Select **Repositories**
4. Add this repository: `https://github.com/yourusername/wyoming-cloudflare-bridge`
5. Close the repositories dialog
6. Refresh the page
7. Find "Wyoming Cloudflare Bridge" in the add-on store
8. Click on it and click **Install**

## Configuration

After installation, configure the add-on:

```yaml
stt_url: "https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev"
tts_url: "https://wyoming-tts.YOUR-SUBDOMAIN.workers.dev"
log_level: INFO
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `stt_url` | Your Cloudflare STT Worker URL | (required) |
| `tts_url` | Your Cloudflare TTS Worker URL | (required) |
| `log_level` | Logging verbosity | `INFO` |

### Log Levels

- `DEBUG` - Detailed debugging information
- `INFO` - General information (recommended)
- `WARNING` - Warning messages only
- `ERROR` - Error messages only
- `CRITICAL` - Critical messages only

## Usage

### 1. Start the Add-on

1. Save your configuration
2. Go to the **Info** tab
3. Toggle **"Start on boot"** to ON
4. Click **Start**
5. Check the **Log** tab to verify it started successfully

### 2. Add Wyoming Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Wyoming Protocol"
4. Enter:
   - **Host**: `f02c1104-wyoming-cloudflare-bridge` (the add-on's hostname)
   - **Port**: `10300`
5. Click **Submit**

### 3. Create Voice Assistant

1. Go to **Settings** → **Voice Assistants**
2. Click **+ Add Assistant**
3. Configure:
   - **Name**: "Cloudflare Assistant"
   - **Speech-to-Text**: cloudflare-whisper
   - **Text-to-Speech**: cloudflare-aura
   - **Conversation**: Home Assistant Conversation
4. Click **Create**

### 4. Configure Wyoming Satellites

Point your Wyoming Satellite devices to Home Assistant:

```bash
python3 -m wyoming_satellite \
  --name "Living Room" \
  --uri "tcp://YOUR_HOME_ASSISTANT_IP:10300" \
  --mic-command "arecord -r 16000 -c 1 -f S16_LE -t raw" \
  --snd-command "aplay -r 22050 -c 1 -f S16_LE -t raw"
```

Replace `YOUR_HOME_ASSISTANT_IP` with your Home Assistant's IP address.

## Troubleshooting

### Add-on won't start

Check the logs in the **Log** tab. Common issues:

1. **Missing URLs**: Make sure both `stt_url` and `tts_url` are configured
2. **Invalid URLs**: Verify your Cloudflare Worker URLs are correct
3. **Network issues**: Ensure Home Assistant can reach Cloudflare

### Home Assistant can't find the integration

1. Make sure the add-on is running (check **Info** tab)
2. Use the add-on hostname: `f02c1104-wyoming-cloudflare-bridge`
3. Port should be `10300`
4. Try restarting the add-on

### Satellites can't connect

1. Use your Home Assistant's IP address (not localhost)
2. Make sure port 10300 is accessible
3. Check firewall settings
4. Verify the add-on is running

### Check Worker Status

From your computer:

```bash
cd wyoming-cloudflare-bridge/workers
wrangler tail wyoming-stt    # View STT worker logs
wrangler tail wyoming-tts    # View TTS worker logs
```

### Test Workers

```bash
./test-worker.sh  # From the repository directory
```

## Free Tier Limits

Cloudflare Workers AI free tier includes:

- **10,000 neurons per day** (resets at 00:00 UTC)
- Approximately **100-500 voice commands per day**
- No credit card required

If you exceed the free tier, costs are:
- **$0.011 per 1,000 neurons** beyond the daily limit

Monitor your usage in the [Cloudflare Dashboard](https://dash.cloudflare.com/).

## Performance

Expected latency:
- **Wake word detection**: 200-400ms (if using local wake word detection)
- **STT (Speech-to-Text)**: 500-1000ms
- **Intent processing**: 100-300ms
- **TTS (Text-to-Speech)**: 500-1000ms
- **Total**: 2-4 seconds

Comparable to commercial smart speakers like Google Home!

## Support

For issues and questions:

- Check the add-on logs
- Review the [troubleshooting guide](https://github.com/yourusername/wyoming-cloudflare-bridge#troubleshooting)
- Open an issue on [GitHub](https://github.com/yourusername/wyoming-cloudflare-bridge/issues)

## Changelog

See [CHANGELOG.md](https://github.com/yourusername/wyoming-cloudflare-bridge/blob/main/CHANGELOG.md)

## License

MIT License - See [LICENSE](https://github.com/yourusername/wyoming-cloudflare-bridge/blob/main/LICENSE)
