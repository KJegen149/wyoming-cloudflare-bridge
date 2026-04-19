export default {
  async fetch(request, env) {
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      });
    }

    try {
      const body = await request.json();
      const text = body.text;

      if (!text || text.trim().length === 0) {
        return new Response(JSON.stringify({ error: 'No text provided' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      const response = await env.AI.run('@cf/deepgram/aura-2-en', {
        text: text,
      });

      // CF returns raw PCM linear16 — wrap it in a WAV container
      const pcmData = new Uint8Array(await new Response(response).arrayBuffer());
      const sampleRate = 24000;
      const channels = 1;
      const bitsPerSample = 16;
      const wavData = buildWav(pcmData, sampleRate, channels, bitsPerSample);

      return new Response(wavData, {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'audio/wav' },
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

function buildWav(pcmData, sampleRate, channels, bitsPerSample) {
  const header = new ArrayBuffer(44);
  const view = new DataView(header);
  const str = (offset, s) => { for (let i = 0; i < s.length; i++) view.setUint8(offset + i, s.charCodeAt(i)); };

  str(0, 'RIFF');
  view.setUint32(4, 36 + pcmData.byteLength, true);
  str(8, 'WAVE');
  str(12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);                                          // PCM
  view.setUint16(22, channels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * channels * bitsPerSample / 8, true);  // byte rate
  view.setUint16(32, channels * bitsPerSample / 8, true);               // block align
  view.setUint16(34, bitsPerSample, true);
  str(36, 'data');
  view.setUint32(40, pcmData.byteLength, true);

  const wav = new Uint8Array(44 + pcmData.byteLength);
  wav.set(new Uint8Array(header), 0);
  wav.set(pcmData, 44);
  return wav;
}
