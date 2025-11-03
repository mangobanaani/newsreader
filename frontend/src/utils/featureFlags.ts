export const ENABLE_LLM_FEATURES =
  (import.meta.env.VITE_ENABLE_LLM_FEATURES ?? 'false').toString().toLowerCase() === 'true';
