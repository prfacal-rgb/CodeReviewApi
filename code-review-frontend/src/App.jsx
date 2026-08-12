import { useState, useRef } from 'react'
import CodeInput     from './components/CodeInput'
import ModelSelector from './components/ModelSelector'
import ReviewResult  from './components/ReviewResult'
import { reviewCodeStream, reviewFromImage } from './services/api'
import { useDarkMode } from './hooks/useDarkMode'

function extractJson(text) {
  const match = text.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/)
  return match ? match[1] : text.trim()
}

export default function App() {
  const [code,       setCode]       = useState('')
  const [modelId,    setModelId]    = useState('ollama-fast')
  const [result,     setResult]     = useState(null)
  const [loading,    setLoading]    = useState(false)
  const [error,      setError]      = useState(null)
  const [streamText, setStreamText] = useState('')
  const [elapsed,    setElapsed]    = useState(0)
  const [dark,       setDark]       = useDarkMode()
  const timerRef = useRef(null)

  const startTimer = () => {
    setElapsed(0)
    timerRef.current = setInterval(() => setElapsed(s => s + 1), 1000)
  }
  const stopTimer = () => clearInterval(timerRef.current)

  const handleReview = async () => {
    if (!code.trim()) return
    const CHAR_LIMIT = 3000
    if (code.length > CHAR_LIMIT) {
      const ok = window.confirm(
        `El archivo tiene ${code.length} caracteres. Con Ollama local puede tardar más de 3 minutos. ¿Continuar?`
      )
      if (!ok) return
    }
    setLoading(true); setError(null); setResult(null); setStreamText('')
    startTimer()

    try {
      const raw = await reviewCodeStream(code, 'auto', modelId, (text) => setStreamText(text))
      try {
        setResult(JSON.parse(extractJson(raw)))
        setStreamText('')
      } catch {
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
    setLoading(true); setError(null); setResult(null); setStreamText(''); setCode('')
    startTimer()
    try {
      setResult(await reviewFromImage(base64, mimeType, modelId))
    } catch (e) {
      setError(e.response?.data?.detail || 'Error procesando la imagen')
    } finally {
      setLoading(false)
      stopTimer()
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 transition-colors duration-300">

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-10 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">🔍</span>
            <span className="font-semibold text-base tracking-tight">Code Review AI</span>
          </div>
          <button
            onClick={() => setDark(d => !d)}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
            title={dark ? 'Modo claro' : 'Modo oscuro'}
          >
            {dark ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {/* ── Main ──────────────────────────────────────────────────────── */}
      <main className="max-w-4xl mx-auto px-4 py-10 space-y-6">

        <div>
          <h1 className="text-2xl font-bold tracking-tight mb-1">Análisis de código</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Pegá código, subí un archivo o una imagen para obtener un review automático.
          </p>
        </div>

        <ModelSelector value={modelId} onChange={setModelId} disabled={loading} />

        <CodeInput
          code={code}
          onChange={setCode}
          onFileUpload={setCode}
          onImageUpload={handleImage}
          disabled={loading}
        />

        <button
          onClick={handleReview}
          disabled={loading || !code.trim()}
          className={[
            'inline-flex items-center gap-2 px-8 py-3 rounded-xl font-semibold text-sm transition-all duration-200',
            loading || !code.trim()
              ? 'bg-slate-200 dark:bg-slate-700 text-slate-400 dark:text-slate-500 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700 active:scale-95 text-white shadow-md hover:shadow-lg'
          ].join(' ')}
        >
          {loading ? (
            <>
              <svg className="animate-spin w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Analizando… {elapsed}s
            </>
          ) : 'Revisar código'}
        </button>

        {/* Stream en vivo */}
        {loading && streamText && (
          <div className="rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
            <div className="px-4 py-2 flex items-center gap-2 bg-slate-100 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"/>
              <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Generando respuesta…</span>
            </div>
            <pre className="bg-slate-950 text-green-400 p-4 text-xs overflow-auto max-h-52 whitespace-pre-wrap break-words font-mono leading-relaxed">
              {streamText}
            </pre>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-start gap-3 p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800">
            <span className="text-lg shrink-0">❌</span>
            <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
          </div>
        )}

        <ReviewResult result={result} originalCode={code} modelId={modelId} />
      </main>
    </div>
  )
}
