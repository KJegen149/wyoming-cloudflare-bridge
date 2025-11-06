# Home Assistant OS Setup Guide

For users running Home Assistant OS (HAOS) on Raspberry Pi 5.

## Understanding Home Assistant OS

Home Assistant OS is a managed operating system where:
- Direct SSH to the host is disabled by default
- System is containerized and managed
- Add-ons run in isolated Docker containers
- Terminal access is through add-ons

## Option 1: Enable SSH Access (Recommended)

### Step 1: Install SSH & Web Terminal Add-on

1. Open Home Assistant
2. Go to **Settings** → **Add-ons**
3. Click **Add-on Store** (bottom right)
4. Search for "**Terminal & SSH**"
5. Click on "**Terminal & SSH**" by Home Assistant Community Add-ons
6. Click **Install**
7. Wait for installation to complete

### Step 2: Configure SSH

1. After installation, click on the **Configuration** tab
2. Set a password or add your SSH key:

```yaml
authorized_keys:
  - ssh-rsa YOUR_PUBLIC_KEY_HERE
password: ""  # Leave empty if using SSH keys
```

Or with password:

```yaml
authorized_keys: []
password: "YOUR_SECURE_PASSWORD"
```

3. Click **Save**
4. Go to **Info** tab
5. Toggle **"Start on boot"** to ON
6. Click **Start**

### Step 3: Test SSH Connection

From your computer:

```bash
# SSH using port 22222 (not 22!)
ssh root@YOUR_PI_IP -p 22222

# Or if you set a password
ssh -p 22222 root@YOUR_PI_IP
```

You should now be in the Home Assistant OS shell!

### Step 4: Install Wyoming Bridge

Now follow the installation steps:

```bash
# You're now in Home Assistant OS
# Install in /root directory
cd /root

# Create directory
mkdir -p wyoming-cloudflare-bridge
cd wyoming-cloudflare-bridge

# You'll need to copy the server files
# From your computer, run:
# scp -P 22222 -r server root@YOUR_PI_IP:/root/wyoming-cloudflare-bridge/
```

**IMPORTANT**: Home Assistant OS is read-only in many areas. You should install in `/root` or `/config`.

## Option 2: Use Terminal Add-on (Web-Based)

If you prefer not to enable SSH, use the web terminal:

### Step 1: Install Advanced SSH & Web Terminal

1. Settings → Add-ons → Add-on Store
2. Search "Advanced SSH & Web Terminal"
3. Install it
4. Start it
5. Click "Open Web UI"

You now have a terminal in your browser!

### Step 2: Limitations

The Terminal add-on has limitations:
- Runs in a container
- Limited system access
- Can't easily install system services

**For this reason, we recommend Option 3 below.**

## Option 3: Home Assistant Add-on (BEST for HAOS!)

The cleanest solution is to run Wyoming Bridge as a native Home Assistant add-on.

### What's a Home Assistant Add-on?

- Containerized application
- Managed by Home Assistant
- Easy to install and configure
- Proper integration with HA

### Installation

I'll create a custom add-on for you. Here's how to use it:

#### Step 1: Install Custom Add-on

1. Go to **Settings** → **Add-ons** → **Add-on Store**
2. Click the **⋮** menu (top right) → **Repositories**
3. Add this repository URL:
   ```
   https://github.com/YOUR_USERNAME/wyoming-cloudflare-bridge
   ```
   *(Note: You'll need to push the add-on to GitHub first - see below)*

4. The add-on will appear in your add-on store
5. Click "Wyoming Cloudflare Bridge"
6. Click **Install**

#### Step 2: Configure Add-on

1. After installation, go to **Configuration** tab
2. Enter your Cloudflare Worker URLs:

```yaml
stt_url: "https://wyoming-stt.YOUR-SUBDOMAIN.workers.dev"
tts_url: "https://wyoming-tts.YOUR-SUBDOMAIN.workers.dev"
log_level: "INFO"
```

3. Click **Save**
4. Go to **Info** tab
5. Toggle **"Start on boot"** to ON
6. Click **Start**

#### Step 3: Configure Home Assistant

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search "Wyoming Protocol"
4. Enter:
   - **Host**: `f02c1104-wyoming-cloudflare-bridge` (add-on hostname)
   - **Port**: `10300`
5. Create voice assistant with cloudflare-whisper/aura

Done! The add-on will auto-start with Home Assistant.

## Creating the Home Assistant Add-on

I'll create the add-on structure for you now:

### Add-on Files Structure

```
addon/
├── config.yaml          # Add-on configuration
├── Dockerfile          # Container image
├── run.sh             # Startup script
└── README.md          # Add-on documentation
```

This allows you to:
- Install with one click
- Configure via UI
- Auto-start with HA
- Easy updates
- Proper logging in HA

## Comparison

| Method | Pros | Cons |
|--------|------|------|
| **SSH Add-on** | Full access, flexible | Requires SSH setup |
| **Web Terminal** | No SSH needed | Limited capabilities |
| **HA Add-on** ⭐ | Native, easy, integrated | Requires custom repo |

## Recommendation

For Home Assistant OS on Pi 5:

1. **Best**: Use the Home Assistant Add-on (Option 3)
   - Native integration
   - Easy management
   - Proper logging
   - Auto-updates

2. **Alternative**: Enable SSH Add-on (Option 1)
   - Full system access
   - More flexibility
   - Manual management

3. **Not Recommended**: Web Terminal (Option 2)
   - Too limited for this use case

## Next Steps

I'll create the Home Assistant add-on files now. This will give you the best experience!

The add-on will:
- ✅ Install with one click
- ✅ Configure via HA UI
- ✅ Auto-start with Home Assistant
- ✅ Proper logging in HA interface
- ✅ Easy updates
- ✅ No SSH needed

Let me create those files...
