import { GoogleGenAI } from "@google/genai";
import { Message, Role, AuditMetadata } from "../types";

type Provider = 'gemini' | 'ollama';

interface ModelConfig {
  provider: Provider;
  geminiApiKey?: string;
  ollamaEndpoint?: string;
  ollamaModel?: string;
}

interface StreamResult {
  text: string;
  done: boolean;
  audit?: AuditMetadata;
}

const MODEL_CONFIG_KEY = 'mirrorme_model_config';
const DEFAULT_LOCAL_BRIDGE_ENDPOINT = 'http://localhost:8765';
const DEFAULT_LOCAL_MODEL = 'mirrorme';

function normalizeStoredConfig(parsed: Partial<ModelConfig>): ModelConfig {
  const defaults: ModelConfig = {
    provider: 'ollama',
    ollamaEndpoint: DEFAULT_LOCAL_BRIDGE_ENDPOINT,
    ollamaModel: DEFAULT_LOCAL_MODEL,
  };

  const legacyDefault =
    parsed.provider === 'gemini' &&
    !parsed.geminiApiKey &&
    (!parsed.ollamaEndpoint || parsed.ollamaEndpoint === 'http://localhost:11434') &&
    (!parsed.ollamaModel || parsed.ollamaModel === 'llama3.1:8b');

  if (legacyDefault) return defaults;

  const merged: ModelConfig = { ...defaults, ...parsed };

  if (
    merged.provider === 'ollama' &&
    merged.ollamaEndpoint === 'http://localhost:11434' &&
    merged.ollamaModel === 'llama3.1:8b'
  ) {
    return defaults;
  }

  return merged;
}

function loadModelConfig(): ModelConfig {
  const defaults: ModelConfig = {
    provider: 'ollama',
    ollamaEndpoint: DEFAULT_LOCAL_BRIDGE_ENDPOINT,
    ollamaModel: DEFAULT_LOCAL_MODEL,
  };

  if (typeof window === 'undefined') return defaults;

  try {
    const raw = window.localStorage.getItem(MODEL_CONFIG_KEY);
    if (!raw) return defaults;
    const parsed = JSON.parse(raw) as Partial<ModelConfig>;
    const normalized = normalizeStoredConfig(parsed);

    if (JSON.stringify(normalized) !== JSON.stringify(parsed)) {
      window.localStorage.setItem(MODEL_CONFIG_KEY, JSON.stringify(normalized));
    }

    return normalized;
  } catch {
    window.localStorage.removeItem(MODEL_CONFIG_KEY);
    return defaults;
  }
}

function getBrowserGeminiApiKey(configuredKey?: string): string | undefined {
  return configuredKey || import.meta.env.VITE_GEMINI_API_KEY;
}

function extractAuditFromText(fullText: string): AuditMetadata | undefined {
  const auditMatch = fullText.match(/AUDIT_BLOCK:\s*(\{[\s\S]*?\})/);
  if (!auditMatch) return undefined;

  try {
    return JSON.parse(auditMatch[1]) as AuditMetadata;
  } catch (e) {
    console.warn('Audit extraction failed', e);
    return undefined;
  }
}

async function* streamWithGemini(
  contents: Array<{ role: 'user' | 'model'; parts: Array<{ text: string }> }>,
  systemInstruction: string,
  apiKey?: string
): AsyncGenerator<StreamResult> {
  const resolvedKey = getBrowserGeminiApiKey(apiKey);
  if (!resolvedKey) {
    yield {
      text: 'Gemini API key missing. Configure it in Settings/local storage or set VITE_GEMINI_API_KEY in .env.local for local browser testing.',
      done: true,
    };
    return;
  }

  const ai = new GoogleGenAI({ apiKey: resolvedKey });
  const streamResponse = await ai.models.generateContentStream({
    model: 'gemini-3-pro-preview',
    contents: contents as any,
    config: {
      systemInstruction,
      temperature: 0.1,
    },
  });

  let fullAccumulated = '';
  for await (const chunk of streamResponse) {
    const text = chunk.text;
    if (text) {
      fullAccumulated += text;
      yield { text, done: false };
    }
  }

  yield {
    text: '',
    done: true,
    audit: extractAuditFromText(fullAccumulated),
  };
}

async function* streamWithOllama(
  history: Message[],
  systemInstruction: string,
  endpoint: string,
  model: string
): AsyncGenerator<StreamResult> {
  const normalizedEndpoint = endpoint.replace(/\/$/, '');
  const response = await fetch(`${normalizedEndpoint}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      stream: true,
      messages: [
        { role: 'system', content: systemInstruction },
        ...history.map(m => ({
          role: m.role === Role.USER ? 'user' : 'assistant',
          content: m.content,
        })),
      ],
    }),
  });

  if (!response.ok || !response.body) {
    const detail = await response.text().catch(() => '');
    throw new Error(
      `Local MirrorME request failed (${response.status}) for model "${model}" at ${normalizedEndpoint}. ${detail}`.trim()
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let fullAccumulated = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const parsed = JSON.parse(line) as {
          done?: boolean;
          message?: { content?: string };
        };
        const token = parsed.message?.content || '';
        if (token) {
          fullAccumulated += token;
          yield { text: token, done: false };
        }
      } catch {
        // Ignore malformed partial lines and continue consuming the stream.
      }
    }
  }

  if (buffer.trim()) {
    try {
      const parsed = JSON.parse(buffer) as { message?: { content?: string } };
      const token = parsed.message?.content || '';
      if (token) {
        fullAccumulated += token;
        yield { text: token, done: false };
      }
    } catch {
      // A trailing malformed fragment is non-fatal after the streamed response ends.
    }
  }

  yield {
    text: '',
    done: true,
    audit: extractAuditFromText(fullAccumulated),
  };
}

export async function* sendMessageStream(history: Message[], currentMetrics?: any) {
  const config = loadModelConfig();

  const contents = history.map(m => ({
    role: m.role === Role.USER ? 'user' : 'model',
    parts: [{ text: m.content }]
  }));

  const systemInstruction = `You are the MKone-CFR-01 Cognitive Flight Recorder Auditor.
  
  Your role is to design, debug, and audit neural state orchestration for the MirrorMe console.
  
  Axioms:
  A1_traceability: Every claim must cite inputs, tool calls, or specific memory/metric refs.
  A2_consistency: Contradictions must be flagged via "Contradiction Trap Resolution" protocol and sandboxed or repaired using First-Order Logic (FOL).
  A3_robustness: System must remain stable under perturbation.
  
  Operational Context:
  - Stability Threshold (v_min): 0.99
  - Max Drift (drift_max_seconds): 0.00001
  - Reasoning Error Max (epsilon_max): 0.05
  - Target Sync (Gamma): 42Hz
  
  MANDATORY OUTPUT FORMAT:
  1. Primary response in detached, rigorous engineering prose.
  2. A trailing block labeled "AUDIT_BLOCK" followed by a JSON object matching AuditMetadata.
  
  Example AUDIT_BLOCK:
  AUDIT_BLOCK: {
    "module_id": "MKone-CFR-01",
    "assumptions": ["Axiom X is stable"],
    "constraints_checked": ["Non-contradiction"],
    "violations": [],
    "confidence": 0.98,
    "refs": ["MKone_Audit_772"]
  }
  
  Current Telemetry: ${JSON.stringify(currentMetrics || {})}
  
  If stability (v) < 0.99 or error (ε) > 0.05, prioritize identifying the failure vector over general conversation.`;

  try {
    if (config.provider === 'ollama') {
      const endpoint = config.ollamaEndpoint || DEFAULT_LOCAL_BRIDGE_ENDPOINT;
      const model = config.ollamaModel || DEFAULT_LOCAL_MODEL;
      for await (const chunk of streamWithOllama(history, systemInstruction, endpoint, model)) {
        yield chunk;
      }
      return;
    }

    for await (const chunk of streamWithGemini(contents as any, systemInstruction, config.geminiApiKey)) {
      yield chunk;
    }
  } catch (error) {
    console.error('Model stream error:', error);
    const endpoint = config.ollamaEndpoint || DEFAULT_LOCAL_BRIDGE_ENDPOINT;
    const model = config.ollamaModel || DEFAULT_LOCAL_MODEL;
    const detail = error instanceof Error ? error.message : String(error);
    yield {
      text: `MirrorME stream interrupted. Expected local route: ${endpoint} using model "${model}". Start Ollama, confirm \`ollama list\` contains \`${model}\`, then run \`python local_bridge/mirrorme_bridge.py --model ${model}\`. ${detail}`,
      done: true,
    };
  }
}
