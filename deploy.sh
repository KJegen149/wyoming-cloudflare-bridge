#!/bin/bash

# Wyoming Cloudflare Bridge - Deployment Script

set -e

echo "==================================="
echo "Wyoming Cloudflare Bridge Deployer"
echo "==================================="
echo ""

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "Error: wrangler CLI is not installed"
    echo "Install it with: npm install -g wrangler"
    echo "Then run: wrangler login"
    exit 1
fi

# Check if logged in to Cloudflare
if ! wrangler whoami &> /dev/null; then
    echo "Error: Not logged in to Cloudflare"
    echo "Run: wrangler login"
    exit 1
fi

echo "✓ Wrangler CLI found and authenticated"
echo ""

# Deploy STT Worker
echo "Deploying STT Worker..."
cd workers
STT_OUTPUT=$(wrangler deploy --config wrangler-stt.toml 2>&1)
STT_URL=$(echo "$STT_OUTPUT" | grep -oP 'https://[^\s]+workers\.dev' | head -1)

if [ -z "$STT_URL" ]; then
    echo "Error: Failed to deploy STT worker"
    echo "$STT_OUTPUT"
    exit 1
fi

echo "✓ STT Worker deployed: $STT_URL"
echo ""

# Deploy TTS Worker
echo "Deploying TTS Worker..."
TTS_OUTPUT=$(wrangler deploy --config wrangler-tts.toml 2>&1)
TTS_URL=$(echo "$TTS_OUTPUT" | grep -oP 'https://[^\s]+workers\.dev' | head -1)

if [ -z "$TTS_URL" ]; then
    echo "Error: Failed to deploy TTS worker"
    echo "$TTS_OUTPUT"
    exit 1
fi

echo "✓ TTS Worker deployed: $TTS_URL"
echo ""

cd ..

# Create .env file
echo "Creating .env file..."
cat > .env << EOF
# Cloudflare Worker URLs (auto-generated)
STT_URL=$STT_URL
TTS_URL=$TTS_URL

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
EOF

echo "✓ .env file created"
echo ""

echo "==================================="
echo "Deployment Complete!"
echo "==================================="
echo ""
echo "Your Cloudflare Workers are deployed:"
echo "  STT: $STT_URL"
echo "  TTS: $TTS_URL"
echo ""
echo "Next steps:"
echo "1. Start the bridge server:"
echo "   docker-compose up -d"
echo ""
echo "2. Add Wyoming integration in Home Assistant:"
echo "   Settings → Devices & Services → Add Integration → Wyoming Protocol"
echo "   Enter your server's IP address and port 10300"
echo ""
echo "3. Configure your Wyoming Satellites to connect to port 10300"
echo ""
echo "For more details, see README.md"
