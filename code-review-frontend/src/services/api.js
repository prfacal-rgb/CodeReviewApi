import axios from 'axios'

const BASE_URL = 'http://localhost:8000'
const api = axios.create({ baseURL: BASE_URL })

// ── Modelos disponibles ───────────────────────────────────────────────────────

export const fetchModels = async () => {
  const { data } = await api.get('/reviews/models')
  return data
}

// ── Review (non-streaming) ────────────────────────────────────────────────────

export const reviewCode = async (code, language, modelId) => {
  const { data } = await api.post('/reviews', { code, language, model_id: modelId })
  return data
}

// ── Review con streaming ──────────────────────────────────────────────────────

export const reviewCodeStream = async (code, language, modelId, onChunk) => {
  const response = await fetch(`${BASE_URL}/reviews/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, language, model_id: modelId }),
  })

  if (!response.ok) throw new Error(`HTTP ${response.status}`)

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let accumulated = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    accumulated += decoder.decode(value, { stream: true })
    onChunk(accumulated)
  }

  return accumulated
}

// ── Explain ───────────────────────────────────────────────────────────────────

export const explainSuggestion = async (originalCode, language, suggestion, modelId) => {
  const { data } = await api.post('/explain', {
    original_code: originalCode,
    language,
    suggestion: {
      severity:    suggestion.severity,
      category:    suggestion.category,
      description: suggestion.description,
      how_to_fix:  suggestion.how_to_fix,
      example_fix: suggestion.example_fix,
    },
    model_id: modelId,
  })
  return data
}

// ── Review desde imagen ───────────────────────────────────────────────────────

export const reviewFromImage = async (imageBase64, mimeType, modelId) => {
  const { data } = await api.post('/reviews/image', {
    image_base64: imageBase64,
    mime_type:    mimeType,
    model_id:     modelId,
  })
  return data
}
