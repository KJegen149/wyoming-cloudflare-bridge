# Publishing Your Home Assistant Add-on

Quick guide to make your add-on available in Home Assistant.

## Option 1: GitHub Repository (Recommended)

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository:
   - Name: `wyoming-cloudflare-bridge`
   - Description: "Wyoming Protocol bridge to Cloudflare Workers AI"
   - Public or Private (both work)
3. Click **Create repository**

### Step 2: Push Code to GitHub

```bash
cd wyoming-cloudflare-bridge

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Wyoming Cloudflare Bridge add-on"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/wyoming-cloudflare-bridge.git

# Push
git branch -M main
git push -u origin main
```

### Step 3: Add Repository to Home Assistant

1. Open Home Assistant
2. Go to **Settings** → **Add-ons** → **Add-on Store**
3. Click the **⋮** menu (top right)
4. Select **Repositories**
5. Add your repository URL:
   ```
   https://github.com/YOUR_USERNAME/wyoming-cloudflare-bridge
   ```
6. Click **Add**
7. Close the dialog

### Step 4: Install Your Add-on

1. The add-on should now appear in your add-on store
2. Scroll down to find "Wyoming Cloudflare Bridge"
3. Click on it
4. Click **Install**
5. Configure and start!

## Option 2: Local Add-on (Quick Testing)

For testing without GitHub:

### Step 1: Enable Advanced Mode

1. Click your profile (bottom left)
2. Enable **Advanced Mode**

### Step 2: Create Local Add-on

Using SSH/Terminal add-on:

```bash
# Copy add-on to local add-ons directory
mkdir -p /addons/wyoming-cloudflare-bridge
cp -r /path/to/addon/* /addons/wyoming-cloudflare-bridge/
cp -r /path/to/server /addons/wyoming-cloudflare-bridge/
```

### Step 3: Reload Add-ons

1. Go to **Settings** → **Add-ons**
2. Click **⋮** → **Check for updates**
3. Your local add-on should appear under "Local add-ons"

## Option 3: Use Existing Add-on (Until You Publish)

Temporary workaround using Terminal & SSH add-on:

### Step 1: Install Terminal & SSH Add-on

1. Settings → Add-ons → Add-on Store
2. Search "Terminal & SSH"
3. Install "Terminal & SSH" by Home Assistant Community Add-ons
4. Configure with a password:
   ```yaml
   password: "YOUR_SECURE_PASSWORD"
   ```
5. Start the add-on

### Step 2: Click "Open Web UI"

You'll get a terminal in your browser.

### Step 3: Install Dependencies

```bash
# Install Python pip
apk add --no-cache python3 py3-pip

# Install Wyoming
pip3 install wyoming aiohttp
```

### Step 4: Create Directory

```bash
mkdir -p /config/wyoming-cloudflare-bridge
cd /config/wyoming-cloudflare-bridge
```

### Step 5: Create server files

You'll need to create the Python files manually, or use `wget` to download them:

```bash
# If you've pushed to GitHub:
wget https://raw.githubusercontent.com/YOUR_USERNAME/wyoming-cloudflare-bridge/main/server/__init__.py
wget https://raw.githubusercontent.com/YOUR_USERNAME/wyoming-cloudflare-bridge/main/server/__main__.py
wget https://raw.githubusercontent.com/YOUR_USERNAME/wyoming-cloudflare-bridge/main/server/handler.py
```

Or copy-paste the files using the terminal editor:

```bash
nano __init__.py
# Paste content from server/__init__.py
# Ctrl+X, Y, Enter to save

nano __main__.py
# Paste content from server/__main__.py
# Ctrl+X, Y, Enter to save

nano handler.py
# Paste content from server/handler.py
# Ctrl+X, Y, Enter to save
```

### Step 6: Run Manually

```bash
cd /config/wyoming-cloudflare-bridge

python3 -m . \
  --uri tcp://0.0.0.0:10300 \
  --stt-url "https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev" \
  --tts-url "https://wyoming-tts.YOUR-SUBDOMAIN.workers.dev"
```

**Note**: This runs in the terminal window and stops when you close it. This is why the proper add-on (Option 1) is better!

## Recommended Path

For Home Assistant OS users:

1. **Quick Start**: Use Option 3 to test everything works
2. **Proper Setup**: Then do Option 1 to create a permanent add-on
3. **Benefit**: One-click install, auto-start, proper management

## Publishing to Home Assistant Community Add-ons

To make your add-on available to everyone:

1. Fork the [Home Assistant Community Add-ons](https://github.com/hassio-addons/repository) repository
2. Add your add-on to the repository
3. Submit a pull request
4. Wait for review

**Requirements**:
- Well-documented
- Follows add-on guidelines
- Tested and working
- Maintained

See: https://developers.home-assistant.io/docs/add-ons/

## Updating Your Add-on

### Update Version

Edit `addon/config.yaml`:
```yaml
version: "1.0.1"  # Increment version
```

### Push Updates

```bash
git add .
git commit -m "Update: your changes"
git push
```

### Update in Home Assistant

Users can click **Update** in the add-on page when a new version is available.

## Support

Include in your repository:
- README.md with setup instructions
- CHANGELOG.md with version history
- Issue tracker enabled on GitHub
- License file (MIT recommended)

## Next Steps

1. Choose your deployment method (GitHub recommended)
2. Test the add-on thoroughly
3. Write good documentation
4. Share with the community!
