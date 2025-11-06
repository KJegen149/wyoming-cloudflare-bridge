/**
 * Cloudflare Worker for Speech-to-Text using Whisper
 * Receives audio data and returns transcribed text
 */

export default {
  async fetch(request, env) {
    // CORS headers for all responses
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Only allow POST requests
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    try {
      // Get the audio data from the request
      const audioData = await request.arrayBuffer();

      if (!audioData || audioData.byteLength === 0) {
        return new Response(JSON.stringify({ error: 'No audio data provided' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      // Prepare the audio for Whisper
      // Whisper expects audio in various formats (wav, mp3, etc.)
      const formData = new FormData();
      formData.append('file', new Blob([audioData], { type: 'audio/wav' }), 'audio.wav');

      // Call Cloudflare Workers AI Whisper model
      // Using whisper-large-v3-turbo for best performance
      const response = await env.AI.run('@cf/openai/whisper', {
        audio: Array.from(new Uint8Array(audioData)),
      });

      // Return the transcription
      return new Response(JSON.stringify({
        text: response.text || '',
        language: response.language || 'en',
      }), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });

    } catch (error) {
      console.error('STT Error:', error);
      return new Response(JSON.stringify({
        error: 'Transcription failed',
        details: error.message,
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }
  },
};
