#!/bin/bash

# Test script for Cloudflare Workers

set -e

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    echo "Run ./deploy.sh first to deploy workers and create .env"
    exit 1
fi

echo "=============================="
echo "Testing Cloudflare Workers"
echo "=============================="
echo ""

# Check if URLs are set
if [ -z "$STT_URL" ] || [ -z "$TTS_URL" ]; then
    echo "Error: STT_URL or TTS_URL not set in .env"
    exit 1
fi

# Test STT Worker
echo "Testing STT Worker..."
echo "URL: $STT_URL"
echo ""

# Create a simple test audio file (silence)
# For real testing, use actual audio
dd if=/dev/zero bs=1024 count=32 2>/dev/null | \
  sox -t raw -r 16000 -b 16 -c 1 -e signed-integer - -t wav - 2>/dev/null > test-audio.wav

echo "Sending test audio to STT worker..."
STT_START=$(date +%s.%N)
STT_RESPONSE=$(curl -s -X POST "$STT_URL" \
  --data-binary @test-audio.wav \
  -H "Content-Type: audio/wav" \
  -w "\nHTTP_CODE:%{http_code}")
STT_END=$(date +%s.%N)
STT_TIME=$(echo "$STT_END - $STT_START" | bc)

STT_HTTP_CODE=$(echo "$STT_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
STT_BODY=$(echo "$STT_RESPONSE" | grep -v "HTTP_CODE:")

if [ "$STT_HTTP_CODE" == "200" ]; then
    echo "✓ STT Worker is working! (${STT_TIME}s)"
    echo "Response: $STT_BODY"
else
    echo "✗ STT Worker failed with HTTP $STT_HTTP_CODE"
    echo "Response: $STT_BODY"
fi

echo ""

# Clean up test audio
rm -f test-audio.wav

# Test TTS Worker
echo "Testing TTS Worker..."
echo "URL: $TTS_URL"
echo ""

echo "Sending test text to TTS worker..."
TTS_START=$(date +%s.%N)
TTS_HTTP_CODE=$(curl -s -X POST "$TTS_URL" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, this is a test"}' \
  -o test-output.wav \
  -w "%{http_code}")
TTS_END=$(date +%s.%N)
TTS_TIME=$(echo "$TTS_END - $TTS_START" | bc)

if [ "$TTS_HTTP_CODE" == "200" ]; then
    OUTPUT_SIZE=$(stat -f%z test-output.wav 2>/dev/null || stat -c%s test-output.wav 2>/dev/null)
    echo "✓ TTS Worker is working! (${TTS_TIME}s)"
    echo "Audio file size: $OUTPUT_SIZE bytes"

    # Try to play it (optional)
    if command -v aplay &> /dev/null; then
        echo "Playing audio (press Ctrl+C to skip)..."
        aplay test-output.wav 2>/dev/null || true
    fi
else
    echo "✗ TTS Worker failed with HTTP $TTS_HTTP_CODE"
fi

echo ""

# Clean up
rm -f test-output.wav

echo "=============================="
echo "Testing Complete!"
echo "=============================="
echo ""
echo "STT Latency: ${STT_TIME}s"
echo "TTS Latency: ${TTS_TIME}s"
echo ""
echo "Next steps:"
echo "1. Start bridge server: docker-compose up -d"
echo "2. Check logs: docker-compose logs -f"
echo "3. Add Wyoming integration to Home Assistant"
