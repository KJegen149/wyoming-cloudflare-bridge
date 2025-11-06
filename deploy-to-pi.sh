#!/bin/bash

# Deploy Wyoming Cloudflare Bridge to Raspberry Pi 5

set -e

echo "=========================================="
echo "Deploy to Raspberry Pi 5"
echo "=========================================="
echo ""

# Get Pi IP address
read -p "Enter your Raspberry Pi IP address (e.g., 192.168.1.100): " PI_IP

# Get Pi username (default: pi)
read -p "Enter Pi username [pi]: " PI_USER
PI_USER=${PI_USER:-pi}

echo ""
echo "Deploying to: $PI_USER@$PI_IP"
echo ""

# Test connection
echo "Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 $PI_USER@$PI_IP "echo 'Connected!'" 2>/dev/null; then
    echo "Error: Cannot connect to Pi"
    echo "Make sure SSH is enabled and you can access the Pi"
    exit 1
fi

echo "✓ SSH connection successful"
echo ""

# Copy server files
echo "Copying server files..."
ssh $PI_USER@$PI_IP "mkdir -p /tmp/wyoming-cloudflare-bridge"
scp -r server $PI_USER@$PI_IP:/tmp/wyoming-cloudflare-bridge/

echo "✓ Files copied"
echo ""

# Install on Pi
echo "Installing on Pi..."
ssh $PI_USER@$PI_IP << 'ENDSSH'
set -e

# Install dependencies
echo "Installing dependencies..."
sudo apt-get update -qq
sudo apt-get install -y python3-pip python3-venv

# Create directory
sudo mkdir -p /opt/wyoming-cloudflare-bridge
sudo cp -r /tmp/wyoming-cloudflare-bridge/server /opt/wyoming-cloudflare-bridge/
sudo chown -R $USER:$USER /opt/wyoming-cloudflare-bridge

# Create virtual environment
cd /opt/wyoming-cloudflare-bridge
python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r server/requirements.txt

echo "✓ Installation complete"
ENDSSH

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Get your Cloudflare Worker URLs:"
echo "   Run: ./deploy.sh"
echo ""
echo "2. SSH into your Pi:"
echo "   ssh $PI_USER@$PI_IP"
echo ""
echo "3. Create systemd service:"
echo "   Follow the instructions in RASPBERRY_PI_SETUP.md"
echo "   Section: 'Step 3: Create SystemD Service'"
echo ""
echo "Or test manually first:"
echo "   cd /opt/wyoming-cloudflare-bridge"
echo "   source venv/bin/activate"
echo "   python3 -m server --stt-url YOUR_STT_URL --tts-url YOUR_TTS_URL"
echo ""
