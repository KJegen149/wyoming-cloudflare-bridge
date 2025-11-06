# Project Structure

```
wyoming-cloudflare-bridge/
├── workers/                          # Cloudflare Workers (AI Processing)
│   ├── stt-worker.js                 # Speech-to-Text worker (Whisper)
│   ├── tts-worker.js                 # Text-to-Speech worker (Aura)
│   ├── wrangler-stt.toml             # STT worker configuration
│   ├── wrangler-tts.toml             # TTS worker configuration
│   └── package.json                  # NPM scripts for deployment
│
├── server/                           # Wyoming Bridge Server (Python)
│   ├── __init__.py                   # Package initialization
│   ├── __main__.py                   # Main entry point and CLI
│   ├── handler.py                    # Wyoming protocol event handler
│   └── requirements.txt              # Python dependencies
│
├── systemd/                          # SystemD service files
│   ├── wyoming-cloudflare-bridge.service  # Service definition
│   └── INSTALL.md                    # SystemD installation guide
│
├── Dockerfile                        # Docker image definition
├── docker-compose.yml                # Docker Compose configuration
├── deploy.sh                         # Automated deployment script
├── test-worker.sh                    # Test script for workers
│
├── README.md                         # Main documentation
├── QUICKSTART.md                     # 5-minute setup guide
├── OPTIMIZATION.md                   # Performance tuning guide
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
└── LICENSE                           # MIT License

```

## File Descriptions

### Cloudflare Workers (`workers/`)

**stt-worker.js**
- Receives audio data (WAV format)
- Calls Cloudflare Workers AI Whisper model
- Returns transcribed text as JSON

**tts-worker.js**
- Receives text as JSON
- Calls Cloudflare Workers AI Deepgram Aura model
- Returns synthesized audio (WAV format)

**wrangler-*.toml**
- Configuration for deploying workers
- Specifies AI binding and compatibility

**package.json**
- NPM scripts for easy deployment
- `npm run deploy-all` to deploy both workers

### Bridge Server (`server/`)

**__main__.py**
- CLI argument parsing
- Server initialization
- Wyoming protocol info setup (ASR/TTS models)

**handler.py**
- Implements `AsyncEventHandler` from Wyoming protocol
- Handles audio recording and buffering
- Sends audio to STT worker, receives transcription
- Sends text to TTS worker, receives audio
- Streams audio back to satellites

**requirements.txt**
- `wyoming>=1.5.0` - Wyoming protocol library
- `aiohttp>=3.9.0` - Async HTTP client

### Deployment Files

**Dockerfile**
- Python 3.11 slim image
- Installs dependencies and server code
- Exposes port 10300

**docker-compose.yml**
- Service definition for bridge server
- Environment variable configuration
- Port mapping and restart policy

**deploy.sh**
- Automated deployment script
- Deploys both Cloudflare Workers
- Extracts worker URLs
- Creates `.env` file automatically

**test-worker.sh**
- Tests STT worker with sample audio
- Tests TTS worker with sample text
- Measures latency
- Verifies deployment

### Documentation

**README.md** (Main Documentation)
- Project overview and features
- Detailed setup instructions
- Troubleshooting guide
- Configuration examples

**QUICKSTART.md** (5-Minute Guide)
- Minimal steps to get running
- Copy-paste commands
- Quick troubleshooting

**OPTIMIZATION.md** (Performance Guide)
- Latency optimization techniques
- Network configuration
- Hardware recommendations
- Monitoring and profiling

**systemd/INSTALL.md** (Native Installation)
- SystemD service setup
- Non-Docker deployment
- Management commands

### Configuration Files

**.env.example**
- Template for environment variables
- Documents required variables
- Default values

**.gitignore**
- Python artifacts
- Environment files
- IDE and OS files

**LICENSE**
- MIT License
- Open source and free to use

## Architecture Flow

```
┌─────────────────────┐
│ Wyoming Satellite   │
│ (Mic + Speaker)     │
└──────────┬──────────┘
           │ Wyoming Protocol (TCP)
           │ Audio Stream
           ▼
┌─────────────────────┐
│ Bridge Server       │
│ (Python/Docker)     │
│ Port 10300          │
└──────────┬──────────┘
           │ HTTPS/REST
           │ Audio/Text
           ▼
┌─────────────────────┐
│ Cloudflare Workers  │
│ - STT (Whisper)     │
│ - TTS (Aura)        │
└──────────┬──────────┘
           │
           │ Transcription
           ▼
┌─────────────────────┐
│ Home Assistant      │
│ (Intent Processing) │
└─────────────────────┘
```

## Data Flow

### Speech-to-Text Flow

1. Satellite captures audio → sends to bridge (Wyoming Protocol)
2. Bridge accumulates audio into WAV buffer
3. Bridge sends WAV to STT worker (HTTPS)
4. STT worker calls Whisper model
5. STT worker returns transcription
6. Bridge sends transcript to Home Assistant (Wyoming Protocol)

### Text-to-Speech Flow

1. Home Assistant sends response text → bridge (Wyoming Protocol)
2. Bridge sends text to TTS worker (HTTPS)
3. TTS worker calls Aura model
4. TTS worker returns audio
5. Bridge parses audio and streams chunks
6. Bridge sends audio to satellite (Wyoming Protocol)
7. Satellite plays audio

## Port Usage

- **10300**: Wyoming bridge server (TCP)
- **10400**: Wake word detection (optional, local)
- **HTTPS**: Cloudflare Workers (443)

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `STT_URL` | Cloudflare STT worker URL | `https://wyoming-stt.example.workers.dev` |
| `TTS_URL` | Cloudflare TTS worker URL | `https://wyoming-tts.example.workers.dev` |
| `LOG_LEVEL` | Logging verbosity | `INFO` or `DEBUG` |

## Development

### Testing Changes

```bash
# Test workers locally (requires wrangler dev)
cd workers
wrangler dev --config wrangler-stt.toml

# Test bridge server
cd server
python -m server --stt-url "http://localhost:8787" --tts-url "http://localhost:8788"
```

### Adding Features

**New TTS Voice:**
1. Edit `workers/tts-worker.js`
2. Change model name (e.g., `@cf/myshell/melotts`)
3. Redeploy: `wrangler deploy --config wrangler-tts.toml`

**Different STT Model:**
1. Edit `workers/stt-worker.js`
2. Change model name (e.g., `@cf/openai/whisper-tiny-en`)
3. Redeploy: `wrangler deploy --config wrangler-stt.toml`

**Caching:**
1. Edit `server/handler.py`
2. Add caching logic in `_handle_synthesize()`
3. Rebuild: `docker-compose up --build -d`

## Maintenance

### Updating

```bash
# Pull latest changes (if using git)
git pull

# Update Python dependencies
cd server
pip install --upgrade -r requirements.txt

# Redeploy workers
./deploy.sh

# Restart bridge server
docker-compose restart
```

### Monitoring

```bash
# Bridge server logs
docker-compose logs -f

# Cloudflare Worker logs
cd workers
wrangler tail wyoming-stt
wrangler tail wyoming-tts

# System resources
docker stats wyoming-cloudflare-bridge
```

### Backup

Important files to backup:
- `.env` (contains worker URLs)
- `docker-compose.yml` (if customized)
- `server/` (if you made custom changes)

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Test workers: `./test-worker.sh`
3. Review documentation: `README.md`, `QUICKSTART.md`, `OPTIMIZATION.md`
4. Open GitHub issue with logs and error details
