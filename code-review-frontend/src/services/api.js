import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000' })

// POST /reviews — sin streaming (se mantiene por si se necesita)
export const reviewCode = (code, language, deep) =>
  api.post('/reviews', { code, language, deep })

// POST /reviews/stream — streaming con ReadableStream
// onChunk(text) se llama cada vez que llega un pedazo nuevo
export const reviewCodeStream = async (code, language, deep, onChunk) => {
  const response = await fetch('http://localhost:8000/reviews/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, language, deep })
  })

  if (!response.ok) throw new Error(`HTTP ${response.status}`)

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let full = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    full += decoder.decode(value)
    onChunk(full)   // notificá al componente con el texto acumulado
  }

  return full   // texto completo al final
}

// POST /reviews/from-image
export const reviewFromImage = (imageBase64, mimeType, deep) =>
  api.post('/reviews/from-image', {
    image_base64: imageBase64,
    mime_type: mimeType,
    deep
  })

// POST /explain
export const explainSuggestion = (suggestion, originalCode, language, deep) =>
  api.post('/explain', {
    suggestion,
    original_code: originalCode,
    language,
    deep
  })
  