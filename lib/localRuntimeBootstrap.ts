export interface LocalRuntimeModelConfig {
  provider: 'gemini' | 'ollama';
  geminiApiKey?: string;
  ollamaEndpoint: string;
  ollamaModel: string;
}

export const LOCAL_RUNTIME_CONFIG_KEY = 'mirrorme_model_config';
export const MKULTRA_LOCAL_CONFIG: LocalRuntimeModelConfig = {
  provider: 'ollama',
  geminiApiKey: '',
  ollamaEndpoint: 'http://localhost:8765',
  ollamaModel: 'mkultra:0.3',
};

const LEGACY_LOCAL_MODELS = new Set(['mirrorme', 'llama3.1:8b']);
const LEGACY_LOCAL_ENDPOINTS = new Set([
  'http://localhost:8765',
  'http://127.0.0.1:8765',
  'http://localhost:11434',
  'http://127.0.0.1:11434',
]);

function isLegacyDefault(config: Partial<LocalRuntimeModelConfig>): boolean {
  const providerLooksLocal =
    config.provider === undefined ||
    config.provider === 'ollama' ||
    (config.provider === 'gemini' && !config.geminiApiKey);
  const endpoint = config.ollamaEndpoint?.replace(/\/$/, '');
  const endpointLooksDefault = !endpoint || LEGACY_LOCAL_ENDPOINTS.has(endpoint);
  const modelLooksDefault = !config.ollamaModel || LEGACY_LOCAL_MODELS.has(config.ollamaModel);

  return providerLooksLocal && endpointLooksDefault && modelLooksDefault;
}

/**
 * Seed or migrate only the repository's historical local defaults.
 * Explicit custom endpoints, models, and cloud selections are preserved.
 */
export function bootstrapLocalRuntimeConfig(): void {
  if (typeof window === 'undefined') return;

  try {
    const raw = window.localStorage.getItem(LOCAL_RUNTIME_CONFIG_KEY);
    if (!raw) {
      window.localStorage.setItem(LOCAL_RUNTIME_CONFIG_KEY, JSON.stringify(MKULTRA_LOCAL_CONFIG));
      return;
    }

    const parsed = JSON.parse(raw) as Partial<LocalRuntimeModelConfig>;
    if (isLegacyDefault(parsed)) {
      window.localStorage.setItem(LOCAL_RUNTIME_CONFIG_KEY, JSON.stringify(MKULTRA_LOCAL_CONFIG));
    }
  } catch {
    window.localStorage.setItem(LOCAL_RUNTIME_CONFIG_KEY, JSON.stringify(MKULTRA_LOCAL_CONFIG));
  }
}
