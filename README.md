# Wyoming Cloudflare Bridge

Connect your Home Assistant Wyoming Satellites to Cloudflare Workers AI for free, cloud-based Speech-to-Text (Whisper) and Text-to-Speech (Deepgram Aura) processing.

## Features

- **Free Tier**: Uses Cloudflare Workers AI free tier (10,000 neurons/day = ~200-500 voice commands/day)
- **Low Latency**: Cloudflare's global edge network for fast AI processing
- **No API Keys**: Uses Cloudflare Workers AI binding (included in free plan)
- **Easy Install**: One-click Home Assistant add-on

## Quick Start

### 1. Deploy Cloudflare Workers (5 minutes)

From your computer:

```bash
# Install Wrangler CLI
npm install -g wrangler

# Login to Cloudflare (opens browser)
wrangler login

# Clone this repository
git clone https://github.com/KJegen149/wyoming-cloudflare-bridge
cd wyoming-cloudflare-bridge

# Deploy workers automatically
./deploy.sh
```

**Save the URLs shown!** You'll need them for configuration.

### 2. Install Home Assistant Add-on (10 minutes)

#### Add Repository

1. Open Home Assistant
2. Go to **Settings** → **Add-ons** → **Add-on Store**
3. Click **⋮** (top right) → **Repositories**
4. Add: `https://github.com/KJegen149/wyoming-cloudflare-bridge`
5. Close dialog

#### Install Add-on

1. Scroll to find "**Wyoming Cloudflare Bridge**"
2. Click it → Click **Install**
3. Wait 5-10 minutes for build to complete

#### Configure Add-on

1. Go to **Configuration** tab
2. Enter your Cloudflare Worker URLs:

```yaml
stt_url: "https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev"
tts_url: "https://wyoming-tts.YOUR-SUBDOMAIN.workers.dev"
log_level: INFO
```

3. **Save** → **Info** tab → Toggle **"Start on boot"** → **Start**

### 3. Configure Home Assistant (2 minutes)

#### Add Wyoming Integration

1. **Settings** → **Devices & Services** → **+ Add Integration**
2. Search "**Wyoming Protocol**"
3. Enter:
   - Host: `f02c1104-wyoming-cloudflare-bridge`
   - Port: `10300`

#### Create Voice Assistant

1. **Settings** → **Voice Assistants** → **+ Add Assistant**
2. Configure:
   - Name: "Cloudflare Assistant"
   - Speech-to-Text: **cloudflare-whisper**
   - Text-to-Speech: **cloudflare-aura**
   - Conversation: **Home Assistant Conversation**
3. **Create**

### 4. Configure Satellites

Point your Wyoming Satellites to Home Assistant:

```bash
python3 -m wyoming_satellite \
  --name "Living Room" \
  --uri "tcp://YOUR_HOME_ASSISTANT_IP:10300" \
  --mic-command "arecord -r 16000 -c 1 -f S16_LE -t raw" \
  --snd-command "aplay -r 22050 -c 1 -f S16_LE -t raw"
```

### 5. Test!

Say: "Hey Mycroft, what time is it?"

You should hear a response! 🎉

## Architecture

```
Wyoming Satellite → Home Assistant → Wyoming Bridge → Cloudflare Workers AI
     (mic)              (HA OS)        (Add-on)          (STT + TTS)
```

## Free Tier Limits

- **10,000 neurons per day** (resets at 00:00 UTC)
- Approximately **200-500 voice commands per day**
- No credit card required
- **$0.011 per 1,000 neurons** if you exceed (optional)

## Performance

Expected latency:
- Wake word: 200-400ms (if using local wake word detection)
- STT: 500-1000ms
- Intent processing: 100-300ms
- TTS: 500-1000ms
- **Total: 2-4 seconds** (comparable to Google Home)

## Troubleshooting

### Add-on won't build

**Error: "server/ not found"**

The `server/` directory must be inside `addon/`. Run the cleanup script:

```bash
./cleanup-and-restructure.sh
git add -A
git commit -m "Fix structure"
git push
```

Then reload add-on store and try again.

### Add-on won't start

Check the **Log** tab for errors:

- **"STT URL is not configured"**: Add your Cloudflare Worker URLs in Configuration tab
- **"Connection refused"**: Make sure both URLs are correct and workers are deployed

### Satellites can't connect

- Use your Home Assistant's **IP address** (not localhost) from satellites
- Verify add-on is running: Info tab should show "Started"
- Check port 10300 is accessible

### Check worker status

From your computer:

```bash
cd wyoming-cloudflare-bridge/workers
wrangler tail wyoming-stt    # View STT logs
wrangler tail wyoming-tts    # View TTS logs
```

### Verify workers are deployed

```bash
curl -X POST https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev \
  -H "Content-Type: audio/wav" \
  --data-binary @test.wav
```

Should return JSON with transcription.

## Customization

### Use Faster STT (English only)

Edit `workers/stt-worker.js` line 37:

```javascript
const response = await env.AI.run('@cf/openai/whisper-tiny-en', {
  audio: Array.from(new Uint8Array(audioData)),
});
```

Redeploy:

```bash
cd workers
wrangler deploy --config wrangler-stt.toml
```

### Use Spanish TTS

Edit `workers/tts-worker.js` line 42:

```javascript
const response = await env.AI.run('@cf/deepgram/aura-2-es', {
  text: text,
});
```

Redeploy:

```bash
cd workers
wrangler deploy --config wrangler-tts.toml
```

Update the TTS URL in add-on configuration.

## Monitoring

### View Add-on Logs

Add-on page → **Log** tab

### Monitor Cloudflare Usage

1. [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. **Workers & Pages** → **Overview**
3. Click **Workers AI** to see daily neuron usage

## Support

- **Issues**: [GitHub Issues](https://github.com/KJegen149/wyoming-cloudflare-bridge/issues)
- **Documentation**: This README
- **Logs**: Add-on → Log tab

## Project Structure

```
wyoming-cloudflare-bridge/
├── addon/              # Home Assistant Add-on
│   ├── server/        # Wyoming Protocol bridge (Python)
│   └── ...
└── workers/           # Cloudflare Workers (STT + TTS)
```

## Contributing

Pull requests welcome! Please test thoroughly before submitting.

## License

MIT License - See [LICENSE](LICENSE)

## Acknowledgments

- [Wyoming Protocol](https://github.com/OHF-Voice/wyoming) - Open Home Foundation
- [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/)
- [Home Assistant](https://www.home-assistant.io/)
- OpenAI Whisper
- Deepgram Aura

## Cost Monitoring

Track your usage to stay within free tier:

1. Cloudflare Dashboard → Workers AI
2. Check daily neuron usage
3. Typical usage: 20-50 neurons per voice command
4. Set up alerts if approaching 10,000/day

If you consistently exceed the free tier, consider:
- Upgrading to paid plan ($0.011 per 1,000 neurons)
- Running wake word detection locally to reduce cloud calls
- Using faster models (whisper-tiny-en uses fewer neurons)
