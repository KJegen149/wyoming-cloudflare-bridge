# Direct Answers to Your Questions

## Q: Do you need any additional accesses to Cloudflare or Home Assistant?

### Cloudflare:
**YES** - You need:
1. Free Cloudflare account (no credit card required)
2. Wrangler CLI installed on your computer
3. Run `wrangler login` once to authorize

**That's it!** No API keys, no tokens, no payment methods.

### Home Assistant:
**NO** - The long-lived token you provided is **not required** for basic Wyoming integration.

- Wyoming Protocol connects directly without authentication
- Your token could be useful later for advanced features (custom conversation flows, API access)
- For this project: **Save it, but you don't need it now**

## Q: Do I need to run any local resources aside from Home Assistant on my Raspberry Pi 5 and the Satellites?

**YES** - But it's minimal! Just ONE thing:

### On Your Pi 5 (alongside Home Assistant):
```
Wyoming Bridge Server
├── Resource usage: ~100MB RAM, ~20MB disk, ~2-5% CPU
├── Deployment: Native Python service (no Docker!)
└── Management: SystemD service (starts automatically)
```

### On Your Satellites:
```
Nothing new! Just the Wyoming Satellite software you already have
(mic + speaker + basic audio processing)
```

### Optional (Recommended for Speed):
```
Wake Word Detection Server on Pi 5
├── Resource usage: ~50MB RAM
├── Purpose: Faster wake word detection (local vs cloud)
└── Options: OpenWakeWord, Porcupine, etc.
```

**Total new resources**:
- Main: 100MB RAM, 20MB disk on Pi 5
- Optional: +50MB RAM for wake word

Your Pi 5 has 4-8GB RAM, so this is **trivial** overhead!

## Q: Can we do this without any local Docker instances?

**YES! Absolutely!** And that's actually the **RECOMMENDED** approach for Pi 5.

### What You DON'T Need:
- ❌ Docker
- ❌ Docker Compose
- ❌ Container runtime
- ❌ Docker images
- ❌ Docker overhead (~100MB extra RAM)

### What You DO Use:
- ✅ Native Python (already on your Pi)
- ✅ Virtual environment (isolated dependencies)
- ✅ SystemD service (native Linux service manager)
- ✅ Direct execution (faster, less overhead)

### Benefits of No Docker:
1. **Less RAM**: 100MB vs 200MB
2. **Faster**: No container overhead
3. **Simpler**: Native systemd commands
4. **Easier debugging**: Direct logs via journalctl
5. **Auto-start**: SystemD handles boot startup

## Summary

### You Need:
| Component | Required? | Notes |
|-----------|-----------|-------|
| **Cloudflare free account** | ✅ Yes | No credit card |
| **Wrangler CLI** | ✅ Yes | On your computer, not Pi |
| **Wyoming Bridge on Pi 5** | ✅ Yes | Native Python, no Docker |
| **Home Assistant token** | ❌ No | Save for later |
| **Docker** | ❌ No | Not needed! |
| **Separate server** | ❌ No | Use your Pi 5 |

### Your Pi 5 Will Run:
```
Before:
- Home Assistant

After:
- Home Assistant
- Wyoming Bridge (native Python service) ← Only addition!
```

### Your Satellites Will Run:
```
Same as before:
- Wyoming Satellite software
(Just configured to connect to Pi 5's new bridge)
```

## Deployment Path

1. **From your computer**: Deploy Cloudflare Workers (5 min)
2. **On your Pi 5**: Install Python service (5 min)
3. **In Home Assistant**: Add Wyoming integration (2 min)
4. **On satellites**: Point to Pi 5 (2 min)

**Total time**: ~15 minutes
**Docker needed**: ❌ No
**Additional hardware**: ❌ No
**Monthly cost**: $0

## Next Steps

Follow: [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md)

This guide shows you exactly how to:
1. Deploy workers from your computer
2. Install bridge on Pi 5 without Docker
3. Configure everything

The guide is step-by-step with copy-paste commands.

## Questions?

If you hit any issues during setup, check:
- `sudo journalctl -u wyoming-cloudflare -f` (bridge logs)
- `./test-worker.sh` (test Cloudflare workers)
- RASPBERRY_PI_SETUP.md troubleshooting section
