/**
 * Cloudflare Worker for Text-to-Speech using Deepgram Aura
 * Receives text and returns audio data
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
      // Get the text data from the request
      const body = await request.json();
      const text = body.text;
      const voice = body.voice || 'default';  // Voice selection if supported

      if (!text || text.trim().length === 0) {
        return new Response(JSON.stringify({ error: 'No text provided' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      // Call Cloudflare Workers AI TTS model
      // Using Deepgram Aura for natural-sounding speech
      const response = await env.AI.run('@cf/deepgram/aura-2-en', {
        text: text,
      });

      // The response should be audio data
      // Return as binary audio
      return new Response(response, {
        status: 200,
        headers: {
          ...corsHeaders,
          'Content-Type': 'audio/wav',
        },
      });

    } catch (error) {
      console.error('TTS Error:', error);
      return new Response(JSON.stringify({
        error: 'Text-to-speech failed',
        details: error.message,
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }
  },
};
