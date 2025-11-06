# SystemD Installation Guide

For running the bridge server as a native system service (without Docker).

## Prerequisites

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## Installation Steps

### 1. Create User

```bash
sudo useradd -r -s /bin/false wyoming
```

### 2. Install Application

```bash
# Create directory
sudo mkdir -p /opt/wyoming-cloudflare-bridge
sudo cp -r server /opt/wyoming-cloudflare-bridge/
cd /opt/wyoming-cloudflare-bridge

# Create virtual environment
sudo python3 -m venv venv
sudo venv/bin/pip install -r server/requirements.txt

# Set permissions
sudo chown -R wyoming:wyoming /opt/wyoming-cloudflare-bridge
```

### 3. Configure Service

```bash
# Copy service file
sudo cp systemd/wyoming-cloudflare-bridge.service /etc/systemd/system/

# Edit service file with your Cloudflare Worker URLs
sudo nano /etc/systemd/system/wyoming-cloudflare-bridge.service
```

Update the Environment variables:
```
Environment="STT_URL=https://wyoming-stt.YOUR_SUBDOMAIN.workers.dev"
Environment="TTS_URL=https://wyoming-tts.YOUR_SUBDOMAIN.workers.dev"
```

### 4. Enable and Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable wyoming-cloudflare-bridge

# Start service
sudo systemctl start wyoming-cloudflare-bridge

# Check status
sudo systemctl status wyoming-cloudflare-bridge
```

## Management Commands

```bash
# View logs
sudo journalctl -u wyoming-cloudflare-bridge -f

# Restart service
sudo systemctl restart wyoming-cloudflare-bridge

# Stop service
sudo systemctl stop wyoming-cloudflare-bridge

# Disable service
sudo systemctl disable wyoming-cloudflare-bridge
```

## Updating

```bash
# Stop service
sudo systemctl stop wyoming-cloudflare-bridge

# Update code
cd /opt/wyoming-cloudflare-bridge
sudo -u wyoming git pull  # If using git
# Or manually copy updated files

# Update dependencies
sudo -u wyoming venv/bin/pip install --upgrade -r server/requirements.txt

# Start service
sudo systemctl start wyoming-cloudflare-bridge
```

## Troubleshooting

### Service won't start

```bash
# Check logs
sudo journalctl -u wyoming-cloudflare-bridge -n 50

# Verify Python can run the module
sudo -u wyoming /opt/wyoming-cloudflare-bridge/venv/bin/python -m server --help
```

### Permission denied

```bash
# Fix permissions
sudo chown -R wyoming:wyoming /opt/wyoming-cloudflare-bridge
```

### Port already in use

```bash
# Check what's using port 10300
sudo netstat -tlnp | grep 10300

# Kill the process or change port in service file
```
