import { useState, useRef } from 'react'
import CodeInput     from './components/CodeInput'
import ModelSelector from './components/ModelSelector'
import ReviewResult  from './components/ReviewResult'
import { reviewCodeStream, reviewFromImage } from './services/api'

// Saca el JSON de dentro de ```json ... ``` si el modelo lo envuelve
function extractJson(text) {
  const match = text.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/)
  return match ? match[1] : text.trim()
}

export default function App() {
  const [code,       setCode]       = useState('')
  const [modelId,    setModelId]    = useState('ollama-fast')   // ← antes: deep (bool)
  const [result,     setResult]     = useState(null)
  const [loading,    setLoading]    = useState(false)
  const [error,      setError]      = useState(null)
  const [streamText, setStreamText] = useState('')
  const [elapsed,    setElapsed]    = useState(0)

  const timerRef = useRef(null)

  const startTimer = () => {
    setElapsed(0)
    timerRef.current = setInterval(() => setElapsed(s => s + 1), 1000)
  }

  const stopTimer = () => {
    clearInterval(timerRef.current)
  }

  const handleReview = async () => {
    if (!code.trim()) return
    const CHAR_LIMIT = 3000
    if (code.length > CHAR_LIMIT) {
      const ok = window.confirm(
        `El archivo tiene ${code.length} caracteres. Con Ollama local puede tardar más de 3 minutos. ¿Continuar?`
      )
      if (!ok) return
    }
    setLoading(true)
    setError(null)
    setResult(null)
    setStreamText('')
    startTimer()

    try {
      const raw = await reviewCodeStream(
        code,
        'auto',
        modelId,                              // ← antes: deep
        (text) => setStreamText(text)
      )
      try {
        const parsed = JSON.parse(extractJson(raw))
        setResult(parsed)
        setStreamText('')
      } catch (parseErr) {
        setError('El modelo respondió pero no pudo parsearse. Intentá con un archivo más corto.')
      }
    } catch (e) {
      setError(e.message || 'Error al conectar con la API')
    } finally {
      setLoading(false)
      stopTimer()
    }
  }

  const handleImage = async (base64, mimeType) => {
    setLoading(true)
    setError(null)
    setResult(null)
    setStreamText('')
    setCode('')
    startTimer()

    try {
      const res = await reviewFromImage(base64, mimeType, modelId)  // ← antes: deep
      setResult(res)                                                  // ← antes: res.data
    } catch (e) {
      setError(e.response?.data?.detail || 'Error procesando la imagen')
    } finally {
      setLoading(false)
      stopTimer()
    }
  }

  return (
    <div style={{ maxWidth: '860px', margin: '0 auto', padding: '32px 16px', fontFamily: 'sans-serif' }}>
      <h1 style={{ marginBottom: '4px' }}>🔍 Code Review AI</h1>
      <p style={{ color: '#666', marginBottom: '24px' }}>
        Pegá código, subí un archivo o una foto para obtener un review automático.
      </p>

      {/* ← value/onChange en lugar de deep/onChange */}
      <ModelSelector value={modelId} onChange={setModelId} disabled={loading} />

      <CodeInput
        code={code}
        onChange={setCode}
        onFileUpload={setCode}
        onImageUpload={handleImage}
      />

      <button
        onClick={handleReview}
        disabled={loading || !code.trim()}
        style={{
          marginTop: '12px',
          padding: '10px 28px',
          fontSize: '15px',
          background: loading ? '#6b7280' : '#2563eb',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: loading ? 'not-allowed' : 'pointer',
          transition: 'background 0.2s'
        }}
      >
        {loading ? `⏳ Analizando... ${elapsed}s` : 'Revisar código'}
      </button>

      {loading && streamText && (
        <div style={{ marginTop: '16px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
            Respuesta en tiempo real:
          </div>
          <pre style={{
            background: '#0f172a',
            color: '#4ade80',
            padding: '12px',
            borderRadius: '8px',
            fontSize: '12px',
            overflow: 'auto',
            maxHeight: '220px',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word'
          }}>
            {streamText}
          </pre>
        </div>
      )}

      {error && (
        <div style={{
          marginTop: '16px',
          color: '#dc2626',
          background: '#fee2e2',
          padding: '12px',
          borderRadius: '8px'
        }}>
          ❌ {error}
        </div>
      )}

      {/* modelId se pasa para que ReviewResult lo use al llamar a explainSuggestion */}
      <ReviewResult result={result} originalCode={code} language="auto" modelId={modelId} />
    </div>
  )
}
