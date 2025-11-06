# Fixing Add-on Install Error

## The Problem

You're getting:
```
Can't install ghcr.io/yourusername/wyoming-cloudflare-bridge-aarch64:1.0.0: 403 Client Error
```

This happens because the `addon/config.yaml` had a placeholder image reference to a Docker registry that doesn't exist.

## The Fix

I've removed the `image:` line from `addon/config.yaml`. Now Home Assistant will **build the add-on locally** from the Dockerfile instead of trying to download a pre-built image.

### What Changed

**Before** (line 25):
```yaml
image: ghcr.io/yourusername/wyoming-cloudflare-bridge-{arch}
```

**After** (removed):
```yaml
# Line removed - Home Assistant will build locally
```

## Steps to Fix

### Step 1: Commit and Push Changes

```bash
cd wyoming-cloudflare-bridge
git add addon/config.yaml
git commit -m "Fix: Remove image reference for local build"
git push
```

### Step 2: Refresh Add-on Store in Home Assistant

1. Go to **Settings** → **Add-ons** → **Add-on Store**
2. Click **⋮** (top right) → **Reload**
3. Or refresh your browser (Ctrl+F5 / Cmd+Shift+R)

### Step 3: Try Installing Again

1. Find "Wyoming Cloudflare Bridge" in your add-on store
2. Click on it
3. Click **Install**
4. It should now build locally! ✅

## What's Happening Now

Home Assistant will:
1. Clone your repository
2. Read `addon/Dockerfile`
3. Build the Docker image locally on your Pi
4. Install the add-on

**This may take 5-10 minutes** on a Raspberry Pi 5 as it compiles everything.

## Monitoring the Build

### Watch Build Progress

1. While installing, click on the add-on
2. Go to the **Log** tab
3. You'll see build output like:
   ```
   Building image...
   Sending build context...
   Step 1/10 : FROM...
   ```

### If Build Fails

Check the logs for errors. Common issues:

#### Error: "server/ not found"

The Dockerfile expects the `server/` directory. Make sure your repository has:
```
addon/
├── Dockerfile
├── config.yaml
└── ...
server/           ← Must be here!
├── __init__.py
├── __main__.py
├── handler.py
└── requirements.txt
```

If missing, push it:
```bash
git add server/
git commit -m "Add server directory"
git push
```

Then reload the add-on store and try again.

#### Error: "Python package not found"

The build might be missing dependencies. Check `server/requirements.txt` exists:
```bash
ls -la server/requirements.txt
cat server/requirements.txt
```

Should contain:
```
wyoming>=1.5.0
aiohttp>=3.9.0
```

#### Error: "Out of memory" or "Build timeout"

Building on a Pi can be resource-intensive. Try:
1. Close other apps
2. Reboot the Pi
3. Try installing again
4. Consider using the workaround below

## Alternative: Quick Workaround

If the build is taking too long or failing, use the Terminal method instead:

See: **[QUICK_HAOS_WORKAROUND.md](QUICK_HAOS_WORKAROUND.md)**

This runs the bridge without building a Docker image - much faster!

## Verifying Repository Structure

Before trying again, verify your GitHub repository has this structure:

```
https://github.com/KJegen149/wyoming-cloudflare-bridge
├── repository.json      ✓ (for HA add-on store)
├── addon/
│   ├── config.yaml     ✓ (updated, no image line)
│   ├── Dockerfile      ✓
│   ├── run.sh          ✓
│   ├── build.yaml      ✓
│   ├── README.md
│   └── DOCS.md
├── server/             ✓ (required by Dockerfile)
│   ├── __init__.py
│   ├── __main__.py
│   ├── handler.py
│   └── requirements.txt
└── workers/
    └── ...
```

Check this by visiting:
https://github.com/KJegen149/wyoming-cloudflare-bridge

## Quick Check Commands

From your computer:

```bash
cd wyoming-cloudflare-bridge

# Verify structure
ls -la addon/
ls -la server/

# Check config.yaml doesn't have image line
grep -n "^image:" addon/config.yaml
# Should return nothing

# Check Dockerfile references are correct
grep "COPY server/" addon/Dockerfile
# Should show: COPY server/ ./server/

# Verify all files are committed
git status
# Should be clean or show only new changes

# Push everything
git add .
git commit -m "Fix add-on configuration for local build"
git push
```

## Expected Install Time

On Raspberry Pi 5:
- **First install**: 5-10 minutes (building image)
- **Updates**: 2-5 minutes (using cache)
- **Restarts**: Instant (image already built)

## What to Expect During Install

1. **Cloning repository** (30 seconds)
2. **Building base image** (2-3 minutes)
3. **Installing Python packages** (2-4 minutes)
4. **Finalizing image** (1 minute)
5. **Starting add-on** (10 seconds)

## Success Indicators

You'll know it worked when:
- ✅ Log shows "INFO - Starting Wyoming Cloudflare Bridge..."
- ✅ Add-on shows "Started" status
- ✅ No error messages in logs

## After Successful Install

1. Configure the add-on:
   ```yaml
   stt_url: "https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev"
   tts_url: "https://wyoming-tts.YOUR-SUBDOMAIN.workers.dev"
   log_level: INFO
   ```

2. Save and start the add-on

3. Add Wyoming integration:
   - Host: `f02c1104-wyoming-cloudflare-bridge`
   - Port: `10300`

## Still Having Issues?

Try the **Terminal & SSH workaround**:
1. Much faster (no Docker build)
2. Same functionality
3. Good for testing

See: [QUICK_HAOS_WORKAROUND.md](QUICK_HAOS_WORKAROUND.md)

Then come back to the add-on once you've verified everything works!
