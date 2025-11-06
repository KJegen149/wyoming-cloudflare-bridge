#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant Add-on: Wyoming Cloudflare Bridge
# Runs the Wyoming Protocol bridge to Cloudflare Workers AI
# ==============================================================================

bashio::log.info "Starting Wyoming Cloudflare Bridge..."

# Get configuration
STT_URL=$(bashio::config 'stt_url')
TTS_URL=$(bashio::config 'tts_url')
LOG_LEVEL=$(bashio::config 'log_level')

# Validate configuration
if [[ -z "${STT_URL}" ]]; then
    bashio::log.fatal "STT URL is not configured!"
    bashio::log.fatal "Please configure the add-on with your Cloudflare STT Worker URL"
    exit 1
fi

if [[ -z "${TTS_URL}" ]]; then
    bashio::log.fatal "TTS URL is not configured!"
    bashio::log.fatal "Please configure the add-on with your Cloudflare TTS Worker URL"
    exit 1
fi

bashio::log.info "STT URL: ${STT_URL}"
bashio::log.info "TTS URL: ${TTS_URL}"
bashio::log.info "Log Level: ${LOG_LEVEL}"

# Start the Wyoming bridge
bashio::log.info "Starting Wyoming Protocol server on port 10300..."

cd /app

exec python3 -m server \
    --uri tcp://0.0.0.0:10300 \
    --stt-url "${STT_URL}" \
    --tts-url "${TTS_URL}" \
    --log-level "${LOG_LEVEL}"
