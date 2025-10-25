import fetch from "node-fetch";

const MODEL_PRIMARY = process.env.CAS_MODEL_ID || "gpt-4o-mini";
const MODEL_FALLBACK = "gpt-4o";
const OPENAI_URL = "https://api.openai.com/v1/chat/completions";
const KEY = process.env.OPENAI_API_KEY as string;

export async function chatLLM(userPrompt: string, systemPrompt: string) {
  async function call(model: string) {
    const r = await fetch(OPENAI_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model,
        temperature: 0.4,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ]
      })
    });
    if (!r.ok) throw new Error(`OpenAI ${r.status}`);
    return r.json();
  }
  try {
    return await call(MODEL_PRIMARY);
  } catch {
    return await call(MODEL_FALLBACK);
  }
}

export function safeJson(text: string | undefined, fallback: any) {
  try { return JSON.parse(text || ""); } catch { return fallback; }
}
