# Wyoming Cloudflare Bridge Documentation

## Quick Start

1. **Deploy Cloudflare Workers** (from your computer):
   ```bash
   npm install -g wrangler
   wrangler login
   cd wyoming-cloudflare-bridge
   ./deploy.sh
   ```
   Save the URLs shown!

2. **Configure this add-on**:
   - Enter your STT and TTS worker URLs
   - Save configuration
   - Start the add-on

3. **Add Wyoming integration**:
   - Settings → Devices & Services → Add Integration → Wyoming Protocol
   - Host: `f02c1104-wyoming-cloudflare-bridge`
   - Port: `10300`

4. **Create voice assistant**:
   - Settings → Voice Assistants → Add Assistant
   - STT: cloudflare-whisper
   - TTS: cloudflare-aura

5. **Configure satellites**:
   Point them to your Home Assistant IP, port 10300

## Configuration

### Required Settings

- **stt_url**: Your Cloudflare Speech-to-Text worker URL
- **tts_url**: Your Cloudflare Text-to-Speech worker URL

Example:
```yaml
stt_url: "https://wyoming-stt.example.workers.dev"
tts_url: "https://wyoming-tts.example.workers.dev"
log_level: INFO
```

### Log Levels

- **DEBUG**: Detailed debugging (use for troubleshooting)
- **INFO**: Standard logging (recommended)
- **WARNING**: Only warnings and errors
- **ERROR**: Only errors
- **CRITICAL**: Only critical errors

## Advanced Configuration

### Custom Models

To use different Cloudflare AI models, edit your workers before deploying:

**For faster STT** (English only):
Edit `workers/stt-worker.js`:
```javascript
const response = await env.AI.run('@cf/openai/whisper-tiny-en', {
  audio: Array.from(new Uint8Array(audioData)),
});
```

**For Spanish TTS**:
Edit `workers/tts-worker.js`:
```javascript
const response = await env.AI.run('@cf/deepgram/aura-2-es', {
  text: text,
});
```

Then redeploy:
```bash
cd workers
wrangler deploy --config wrangler-stt.toml
wrangler deploy --config wrangler-tts.toml
```

Update the URLs in this add-on's configuration.

## Monitoring

### View Add-on Logs

Click the **Log** tab in this add-on to see:
- Startup messages
- Connection status
- Transcription requests
- TTS requests
- Errors and warnings

### Monitor Cloudflare Usage

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **Workers & Pages** → **Overview**
3. Click on **Workers AI**
4. View your daily neuron usage

### Performance Metrics

Enable DEBUG logging to see detailed timing:

```yaml
log_level: DEBUG
```

Look for lines like:
```
INFO - Transcribing 32768 bytes of audio
INFO - Transcription: turn on the lights
INFO - Synthesizing: Turning on the lights
```

## Troubleshooting

### "STT URL is not configured"

The add-on requires both worker URLs. Make sure you've:
1. Deployed the Cloudflare Workers
2. Entered both URLs in configuration
3. Saved the configuration
4. Restarted the add-on

### "Connection refused" errors

If satellites can't connect:
1. Verify the add-on is running
2. Check you're using Home Assistant's IP (not localhost) from satellites
3. Ensure port 10300 is accessible
4. Check firewall settings

### Slow response times

1. Check your internet connection speed
2. Monitor Cloudflare Dashboard for worker latency
3. Consider running wake word detection locally
4. See [OPTIMIZATION.md](https://github.com/yourusername/wyoming-cloudflare-bridge/blob/main/OPTIMIZATION.md)

### Worker errors

View worker logs from your computer:
```bash
cd wyoming-cloudflare-bridge/workers
wrangler tail wyoming-stt
wrangler tail wyoming-tts
```

Common issues:
- **Workers AI not enabled**: Check Cloudflare Dashboard
- **Exceeded free tier**: Monitor usage, upgrade if needed
- **Invalid audio format**: Satellites should send 16kHz mono WAV

## Network Requirements

### Ports

- **10300**: Wyoming Protocol server (exposed by add-on)

### Firewall

If using external satellites:
```bash
# On router or Home Assistant OS
# Allow incoming connections on port 10300
```

### DNS

The add-on needs to reach:
- `*.workers.dev` (Cloudflare Workers)
- Standard HTTPS (port 443)

## Performance Optimization

### Local Wake Word Detection

Install the OpenWakeWord add-on:
1. Add-on Store → OpenWakeWord
2. Install and configure
3. Point satellites to both:
   - Wake word: `YOUR_HA_IP:10400`
   - Wyoming: `YOUR_HA_IP:10300`

This prevents sending continuous audio to the cloud.

### Audio Settings

Configure satellites with optimal settings:
```bash
--mic-command "arecord -r 16000 -c 1 -f S16_LE -t raw"
--snd-command "aplay -r 22050 -c 1 -f S16_LE -t raw"
```

- **16kHz**: Matches Whisper's native rate
- **Mono**: Reduces bandwidth by 50%
- **S16_LE**: Standard PCM format

## Integration with Home Assistant

### Automations

You can use the voice assistant in automations:

```yaml
automation:
  - alias: "Voice command received"
    trigger:
      - platform: conversation
        command: "turn on all lights"
    action:
      - service: light.turn_on
        target:
          area_id: all
```

### Multiple Satellites

The add-on supports multiple simultaneous satellites:
- Each satellite connects independently
- Concurrent voice commands are handled
- No additional configuration needed

### Custom Intents

Define custom intents in Home Assistant:

```yaml
# configuration.yaml
conversation:
  intents:
    TurnOnLight:
      - "turn on [the] {name}"
      - "switch on [the] {name}"
```

## Backup and Restore

### Configuration Backup

Your add-on configuration is included in Home Assistant backups.

### Worker Backup

Keep a copy of:
- Worker URLs (in your password manager)
- `workers/` directory (in git or backup)

To redeploy workers:
```bash
cd workers
wrangler deploy --config wrangler-stt.toml
wrangler deploy --config wrangler-tts.toml
```

## Updating

### Update Add-on

1. Go to the add-on page
2. If an update is available, click **Update**
3. The add-on will restart automatically

### Update Workers

```bash
cd wyoming-cloudflare-bridge
git pull  # If using git
cd workers
wrangler deploy --config wrangler-stt.toml
wrangler deploy --config wrangler-tts.toml
```

No need to update add-on configuration if URLs haven't changed.

## Support

- **Documentation**: [GitHub](https://github.com/yourusername/wyoming-cloudflare-bridge)
- **Issues**: [GitHub Issues](https://github.com/yourusername/wyoming-cloudflare-bridge/issues)
- **Community**: [Home Assistant Community](https://community.home-assistant.io/)
