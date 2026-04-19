/**
 * Jarvis LLM Worker
 * Routing chain: Gemini 2.0 Flash → Groq Llama → CF Llama (neuron fallback)
 * Gemini + Groq are free external APIs — CF AI neurons only burn if both fail.
 */

const GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';
const GROQ_URL   = 'https://api.groq.com/openai/v1/chat/completions';
const GROQ_MODEL = 'llama-3.3-70b-versatile';

// ── Gemini ────────────────────────────────────────────────────────────────────
async function callGemini(messages, apiKey) {
  const system  = messages.find(m => m.role === 'system');
  const history = messages.filter(m => m.role !== 'system');

  const body = {
    contents: history.map(m => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }],
    })),
    generationConfig: { maxOutputTokens: 256, temperature: 0.7 },
  };
  if (system) body.systemInstruction = { parts: [{ text: system.content }] };

  const res = await fetch(`${GEMINI_URL}?key=${apiKey}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Gemini ${res.status}`);
  const data = await res.json();
  return data.candidates?.[0]?.content?.parts?.[0]?.text ?? '';
}

// ── Groq ──────────────────────────────────────────────────────────────────────
async function callGroq(messages, apiKey) {
  const res = await fetch(GROQ_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
    body: JSON.stringify({ model: GROQ_MODEL, messages, max_tokens: 256, temperature: 0.7 }),
  });
  if (!res.ok) throw new Error(`Groq ${res.status}`);
  const data = await res.json();
  return data.choices?.[0]?.message?.content ?? '';
}

// ── CF Llama (neuron fallback) ─────────────────────────────────────────────────
async function callCFLlama(messages, env) {
  const res = await env.AI.run('@cf/meta/llama-3.1-8b-instruct-fast', {
    messages, max_tokens: 256, temperature: 0.7,
  });
  return res?.response ?? res?.choices?.[0]?.message?.content ?? '';
}

// ── System prompt ─────────────────────────────────────────────────────────────
function buildSystemPrompt(deviceList) {
  const devices = deviceList.length > 0
    ? `\nHome devices you are aware of:\n${deviceList.map(d => `- ${d.name} (${d.entity_id}): ${d.state}`).join('\n')}`
    : '';
  return `You are Jarvis, a capable AI assistant integrated into the user's home. You are confident, slightly dry, and efficient — like a butler who actually has a personality.

ALWAYS respond with a valid JSON object — no prose outside the JSON:
{
  "speech": "What you say out loud",
  "service": null
}

Speech guidelines:
- Smart home commands: 1 sentence, confirm the action naturally ("Done." / "Lights off." / "Locking up.")
- Questions and conversation: 2-4 sentences, be direct but warm — no hollow filler like "Great question!" or "Certainly!"
- Jokes: deliver setup, then "(pause)" to indicate natural breath, then punchline — keep it one fluid response spoken aloud
- Never read out raw data — interpret it ("It's a bit warm in here" not "The temperature is 74.2 degrees Fahrenheit")
- Recipes, instructions, or lists: give complete useful answers, spoken naturally as if reading aloud — skip markdown, use "first... then... finally..."

When controlling a device:
{
  "speech": "Done.",
  "service": {
    "domain": "light",
    "service": "turn_on",
    "entity_id": "light.living_room",
    "data": {}
  }
}

Rules:
- service must be null for ANYTHING that is not directly controlling a home device
- NEVER use service for questions, conversation, recipes, timers, or general knowledge
- use exact entity_ids, own your actions, resolve pronouns from history, ask if unsure which device is meant.${devices}`;
}
// ── Main handler ──────────────────────────────────────────────────────────────
export default {
  async fetch(request, env) {
    const cors = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') return new Response(null, { headers: cors });
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405, headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }

    let conversationId = null;

    try {
      const body        = await request.json();
      const text        = body.text?.trim();
      conversationId    = body.conversation_id ?? null;
      const history     = body.history     ?? [];
      const deviceList  = body.device_list ?? [];
      const sysOverride = body.system_prompt ?? null;

      if (!text) {
        return new Response(JSON.stringify({ error: 'No text provided' }), {
          status: 400, headers: { ...cors, 'Content-Type': 'application/json' },
        });
      }

      const messages = [
        { role: 'system', content: sysOverride ?? buildSystemPrompt(deviceList) },
        ...history,
        { role: 'user', content: text },
      ];

      let responseText = '';
      let modelUsed    = '';

      // 1. Gemini (free, best quality)
      if (env.GEMINI_API_KEY) {
        try {
          responseText = await callGemini(messages, env.GEMINI_API_KEY);
          modelUsed = 'gemini-2.0-flash';
        } catch (e) { console.warn('Gemini failed:', e.message); }
      }

      // 2. Groq (free, fast)
      if (!responseText && env.GROQ_API_KEY) {
        try {
          responseText = await callGroq(messages, env.GROQ_API_KEY);
          modelUsed = 'llama-3.3-70b (groq)';
        } catch (e) { console.warn('Groq failed:', e.message); }
      }

      // 3. CF Llama (burns neurons — last resort only)
      if (!responseText) {
        responseText = await callCFLlama(messages, env);
        modelUsed = 'llama-3.1-8b (cf-fallback)';
      }

      responseText = responseText.trim() || "I'm not sure how to respond to that.";
      console.log(`[${modelUsed}] ${responseText.substring(0, 60)}`);

      return new Response(JSON.stringify({ text: responseText, conversation_id: conversationId, model: modelUsed }), {
        status: 200, headers: { ...cors, 'Content-Type': 'application/json' },
      });

    } catch (err) {
      console.error('LLM error:', err.message);
      return new Response(JSON.stringify({
        text: 'I encountered an error. Please try again.',
        conversation_id: conversationId,  // fixed: was undefined in original
        error: err.message,
      }), {
        status: 200, headers: { ...cors, 'Content-Type': 'application/json' },
      });
    }
  },
};
