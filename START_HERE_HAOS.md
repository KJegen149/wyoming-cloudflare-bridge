# Start Here - Home Assistant OS Users

**You asked: Can I run commands via Terminal & SSH add-on?**

**Answer: YES!** But I've created something BETTER for you. 👇

## Three Options for Home Assistant OS

### ⭐ Option 1: Home Assistant Add-on (BEST)

**What it is**: A proper Home Assistant add-on that installs with one click.

**Benefits**:
- ✅ One-click install from add-on store
- ✅ Configure via UI
- ✅ Auto-starts with Home Assistant
- ✅ Logs in HA interface
- ✅ No SSH needed
- ✅ Easy to update

**Setup time**: 10 minutes (including GitHub setup)

**Guide**: [HOME_ASSISTANT_OS_SETUP.md](HOME_ASSISTANT_OS_SETUP.md) → Option 3

**How to use**:
1. Push this code to GitHub (see [PUBLISH_ADDON.md](PUBLISH_ADDON.md))
2. Add repository URL to HA add-on store
3. Install "Wyoming Cloudflare Bridge" add-on
4. Configure with your Cloudflare URLs
5. Done!

### ✓ Option 2: Terminal & SSH Add-on (Quick Test)

**What it is**: Run commands in the web-based terminal.

**Benefits**:
- ✅ No SSH setup needed
- ✅ Works in browser
- ✅ Quick for testing

**Limitations**:
- ❌ Stops when terminal closes
- ❌ No auto-start
- ❌ Manual management

**Setup time**: 5 minutes

**Guide**: [QUICK_HAOS_WORKAROUND.md](QUICK_HAOS_WORKAROUND.md)

**Best for**: Testing if everything works before doing proper setup.

### ✓ Option 3: Enable SSH Properly

**What it is**: Enable real SSH access to Home Assistant OS.

**Benefits**:
- ✅ Full SSH access from computer
- ✅ Can use automation scripts
- ✅ More flexibility

**Limitations**:
- ⚠️  Still need to manage service manually
- ⚠️  Add-on approach is better

**Setup time**: 3 minutes

**Guide**: [HOME_ASSISTANT_OS_SETUP.md](HOME_ASSISTANT_OS_SETUP.md) → Option 1

**How to use**:
1. Install "Terminal & SSH" add-on in HA
2. Configure password or SSH key
3. Enable SSH
4. Connect from computer: `ssh root@YOUR_HA_IP -p 22222`
5. Install bridge as systemd service

## My Recommendation

```
Path A (Best experience):
  Deploy Workers → Push to GitHub → Install Add-on → Configure → Done!

Path B (Quick test):
  Deploy Workers → Use Terminal Add-on → Test it works → Then do Path A
```

## What I've Created For You

### For Home Assistant OS:
```
addon/
├── config.yaml          # Add-on metadata
├── Dockerfile          # Container definition
├── run.sh             # Startup script
├── README.md          # Add-on store description
└── DOCS.md            # Full documentation
```

### Guides:
- `HOME_ASSISTANT_OS_SETUP.md` - Complete HA OS guide
- `QUICK_HAOS_WORKAROUND.md` - Quick terminal test
- `PUBLISH_ADDON.md` - How to publish add-on

## Quick Start (My Recommendation)

### Step 1: Deploy Cloudflare Workers (5 min)

From your computer:
```bash
cd wyoming-cloudflare-bridge
npm install -g wrangler
wrangler login
./deploy.sh
```

Save the URLs!

### Step 2: Push to GitHub (3 min)

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/wyoming-cloudflare-bridge.git
git push -u origin main
```

### Step 3: Add to Home Assistant (2 min)

1. Settings → Add-ons → Add-on Store → ⋮ → Repositories
2. Add: `https://github.com/YOUR_USERNAME/wyoming-cloudflare-bridge`
3. Find "Wyoming Cloudflare Bridge" in store
4. Install!

### Step 4: Configure (1 min)

```yaml
stt_url: "https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev"
tts_url: "https://wyoming-tts.YOUR-SUBDOMAIN.workers.dev"
log_level: INFO
```

Start the add-on!

### Step 5: Use (1 min)

1. Add Wyoming integration (host: `f02c1104-wyoming-cloudflare-bridge`, port: `10300`)
2. Create voice assistant with cloudflare-whisper/aura
3. Point satellites to your HA IP

**Total**: ~12 minutes for complete setup!

## If You Want to Test First

Use the Terminal & SSH add-on to test:

1. Install Terminal & SSH add-on
2. Open Web UI
3. Follow [QUICK_HAOS_WORKAROUND.md](QUICK_HAOS_WORKAROUND.md)
4. Test voice commands
5. Then do proper add-on setup

## Files You Need

### For Cloudflare (deploy from computer):
- `workers/stt-worker.js`
- `workers/tts-worker.js`
- `workers/wrangler-*.toml`

### For Home Assistant Add-on:
- `addon/*` (all files)
- `server/*` (Python code)

### Guides:
- `HOME_ASSISTANT_OS_SETUP.md` ← Start here!
- `PUBLISH_ADDON.md` ← GitHub setup
- `QUICK_HAOS_WORKAROUND.md` ← Quick test

## What You Don't Need

For Home Assistant OS users:
- ❌ Docker Compose (add-on handles it)
- ❌ SystemD files (not applicable to HA OS)
- ❌ Manual service management
- ❌ Direct SSH (can use Terminal add-on)

## Summary

**Your Question**: Can I use Terminal & SSH add-on?
**Answer**: YES, but I made you something better!

**Best Path**:
1. Deploy Cloudflare Workers (from computer)
2. Push to GitHub (from computer)
3. Install as HA Add-on (in HA UI)
4. Configure and use!

**Quick Test Path**:
1. Deploy Cloudflare Workers
2. Use Terminal & SSH add-on to test
3. Then do proper add-on setup

**Read These**:
- [HOME_ASSISTANT_OS_SETUP.md](HOME_ASSISTANT_OS_SETUP.md) - Complete guide
- [QUICK_HAOS_WORKAROUND.md](QUICK_HAOS_WORKAROUND.md) - Quick test

Ready? Start with deploying the Cloudflare Workers!

```bash
cd wyoming-cloudflare-bridge
./deploy.sh
```

Then follow HOME_ASSISTANT_OS_SETUP.md Option 3 (Add-on) or QUICK_HAOS_WORKAROUND.md (quick test).

Questions? All guides have troubleshooting sections!
