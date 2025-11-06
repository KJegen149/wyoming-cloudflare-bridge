# Performance Optimization Guide

Tips and techniques to achieve near real-time voice assistant performance.

## Target Latencies

For a "Google Home"-like experience, aim for:
- **Wake word detection**: < 500ms (local processing)
- **STT (Speech-to-Text)**: 500-1500ms
- **Intent processing**: 100-500ms (Home Assistant)
- **TTS (Text-to-Speech)**: 500-1500ms
- **Total end-to-end**: 2-4 seconds

## 1. Local Wake Word Detection

**Critical for responsiveness!**

Run wake word detection locally to avoid sending continuous audio to the cloud.

### Option A: Wyoming OpenWakeWord (Recommended)

```bash
# On a local server (can be the same as bridge server)
docker run -d \
  --name wyoming-openwakeword \
  -p 10400:10400 \
  -v /path/to/models:/models \
  rhasspy/wyoming-openwakeword

# Configure satellite to use it
python -m wyoming_satellite \
  --name "Living Room" \
  --uri "tcp://BRIDGE_IP:10300" \
  --wake-word-name "hey_jarvis" \
  --wake-word-uri "tcp://localhost:10400" \
  --mic-command "arecord -r 16000 -c 1 -f S16_LE -t raw" \
  --snd-command "aplay -r 22050 -c 1 -f S16_LE -t raw"
```

### Option B: Porcupine (Commercial, very fast)

```bash
pip install pvporcupine
# Follow Porcupine Wyoming integration guide
```

## 2. Audio Configuration

### Optimal Settings

```bash
# For satellites
--mic-command "arecord -r 16000 -c 1 -f S16_LE -t raw -D plughw:CARD=Device,DEV=0"
--snd-command "aplay -r 22050 -c 1 -f S16_LE -t raw -D plughw:CARD=Device,DEV=0"
```

**Why these settings?**
- **16kHz sample rate**: Whisper's native rate (no resampling needed)
- **Mono (1 channel)**: Reduces data transfer by 50%
- **S16_LE format**: Direct PCM format, no encoding overhead

### VAD (Voice Activity Detection)

Enable VAD on the satellite to only send audio when speech is detected:

```bash
python -m wyoming_satellite \
  --name "Living Room" \
  --uri "tcp://BRIDGE_IP:10300" \
  --vad \
  --wake-word-name "hey_jarvis" \
  --wake-word-uri "tcp://localhost:10400" \
  # ... other settings
```

## 3. Network Optimization

### Use Wired Ethernet

WiFi adds latency and jitter. Use Ethernet for:
- Wyoming Satellites
- Bridge Server
- Home Assistant

### Measure Network Latency

```bash
# From satellite to bridge server
ping BRIDGE_IP

# From bridge server to Cloudflare
ping 1.1.1.1

# Test worker response time
time curl -X POST https://wyoming-stt.YOUR_SUBDOMAIN.workers.dev \
  --data-binary @test-audio.wav \
  -H "Content-Type: audio/wav"
```

Target: < 50ms to bridge, < 100ms to Cloudflare

### QoS (Quality of Service)

Configure router QoS to prioritize:
- Port 10300 (Wyoming protocol)
- HTTPS traffic to `*.workers.dev`

## 4. Cloudflare Workers Optimization

### Use Whisper Tiny for English-Only

Edit `workers/stt-worker.js`:

```javascript
// Faster for English-only environments
const response = await env.AI.run('@cf/openai/whisper-tiny-en', {
  audio: Array.from(new Uint8Array(audioData)),
});
```

**Benefits**:
- 2-3x faster than whisper-large-v3-turbo
- Lower neuron cost
- Slightly lower accuracy (usually acceptable)

### Regional Deployment

Cloudflare Workers automatically route to the nearest edge location, but you can verify:

```bash
# Check which datacenter is serving you
curl -I https://wyoming-stt.YOUR_SUBDOMAIN.workers.dev
# Look for: cf-ray header (shows datacenter code)
```

## 5. Bridge Server Optimization

### Run on Fast Hardware

Recommended specs:
- **CPU**: 2+ cores
- **RAM**: 512MB minimum, 1GB recommended
- **Network**: Gigabit Ethernet

### Reduce Docker Overhead

For maximum performance, run natively with systemd (see `systemd/INSTALL.md`)

### Enable Connection Pooling

The bridge server uses aiohttp which pools connections by default. Monitor with:

```bash
docker-compose logs -f | grep -i "connection"
```

## 6. Home Assistant Optimization

### Use Conversation Agent Efficiently

```yaml
# configuration.yaml
conversation:
  intents:
    # Pre-define common intents for faster matching
    TurnOnLight:
      - "turn on [the] {name}"
      - "switch on [the] {name}"
```

### Database Optimization

Large Home Assistant databases slow down intent processing:

```bash
# In Home Assistant container
hass --script recorder purge --keep-days 7
```

### Run on SSD

Home Assistant should run on SSD, not SD card or HDD.

## 7. Multi-Satellite Setup

### Dedicated Bridge Server

For multiple satellites, run bridge server on dedicated hardware:

```
Satellite 1 ─┐
Satellite 2 ─┼─→ Bridge Server → Cloudflare
Satellite 3 ─┘
```

### Load Distribution

The bridge server handles multiple satellites concurrently. Monitor CPU usage:

```bash
docker stats wyoming-cloudflare-bridge
```

If CPU > 80%, consider:
- Faster hardware
- Multiple bridge instances with load balancer

## 8. Monitoring and Profiling

### Enable Detailed Logging

```bash
# .env
LOG_LEVEL=DEBUG
```

Watch for timing information:

```bash
docker-compose logs -f | grep -E "(Transcribing|Transcription:|Synthesizing)"
```

Example output:
```
2025-11-05 12:34:56 - INFO - Transcribing 32768 bytes of audio
2025-11-05 12:34:57 - INFO - Transcription: turn on the lights  [1.2s]
2025-11-05 12:34:57 - INFO - Synthesizing: Turning on the lights
2025-11-05 12:34:58 - INFO - Received 45056 bytes of audio  [0.8s]
```

### Cloudflare Analytics

Check Workers Analytics in Cloudflare Dashboard:
- Requests per second
- P50/P95/P99 latency
- Error rate

### End-to-End Testing

Create a test script:

```bash
#!/bin/bash
# test-latency.sh

echo "Testing end-to-end latency..."

START=$(date +%s.%N)
# Simulate satellite command (use actual satellite or curl to Wyoming protocol)
echo "Turn on the living room lights"
# Wait for response...
END=$(date +%s.%N)

LATENCY=$(echo "$END - $START" | bc)
echo "Total latency: ${LATENCY}s"
```

## 9. Caching Strategies

### TTS Response Caching

For common responses, implement caching in the bridge server:

```python
# In handler.py
_tts_cache = {}

async def _handle_synthesize(self, text: str) -> None:
    # Check cache first
    if text in _tts_cache:
        audio_data = _tts_cache[text]
        # Send cached audio...
        return

    # Otherwise, call Cloudflare and cache result
    audio_data = await fetch_from_cloudflare(text)
    _tts_cache[text] = audio_data
```

### Pre-warm Common Phrases

```python
COMMON_RESPONSES = [
    "OK",
    "Turning on the lights",
    "I don't understand",
    # ... etc
]

# Pre-fetch on startup
for phrase in COMMON_RESPONSES:
    _tts_cache[phrase] = await fetch_tts(phrase)
```

## 10. Hardware Acceleration

### Use Hardware Audio Devices

Instead of software audio, use hardware with DSP:

- **ReSpeaker 2-Mic HAT**: Built-in echo cancellation
- **ReSpeaker 4-Mic Array**: Far-field voice capture
- **USB sound cards**: Offload audio processing from CPU

### Edge TPU (Optional)

For wake word detection, use Google Coral Edge TPU:

```bash
pip install tflite-runtime
# Configure openwakeword to use Edge TPU
```

## Expected Performance

With all optimizations:

| Phase | Expected Latency |
|-------|------------------|
| Wake word detection | 200-400ms |
| Audio capture | 500-1000ms |
| STT processing | 400-800ms |
| Intent processing | 100-300ms |
| TTS processing | 300-600ms |
| Audio playback | 500-1000ms |
| **Total** | **2-4 seconds** |

This matches or exceeds Google Home performance for most use cases!

## Troubleshooting Slow Performance

### Checklist

- [ ] Wake word detection running locally?
- [ ] Using 16kHz mono audio?
- [ ] Bridge server on wired network?
- [ ] Home Assistant database optimized?
- [ ] Cloudflare Workers responding quickly? (check logs)
- [ ] No WiFi interference?
- [ ] Satellite hardware sufficient? (Pi 3B+ minimum)

### Diagnosis Commands

```bash
# Test each component individually

# 1. STT latency
time curl -X POST https://wyoming-stt.YOUR_SUBDOMAIN.workers.dev \
  --data-binary @test-audio.wav

# 2. TTS latency
time curl -X POST https://wyoming-tts.YOUR_SUBDOMAIN.workers.dev \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world"}'

# 3. Bridge server health
docker-compose exec wyoming-cloudflare-bridge ps aux

# 4. Network path
traceroute BRIDGE_IP
traceroute 1.1.1.1
```

## Advanced: Streaming Audio

For even lower latency, implement streaming:

1. **Streaming STT**: Send audio chunks as they arrive
2. **Streaming TTS**: Play audio as it's generated

This requires:
- Cloudflare Workers with streaming support
- Modified bridge server to handle streaming
- Updated satellite firmware

See `STREAMING.md` (TODO) for implementation details.

## Questions?

Open an issue on GitHub with:
- Your latency measurements
- Hardware specs
- Network topology
- Logs from debug mode
