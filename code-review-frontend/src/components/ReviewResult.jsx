import { useState } from 'react'
import SuggestionCard from './SuggestionCard'
import CodeBlock from './CodeBlock'    // ← agregar import arriba
import { explainSuggestion } from '../services/api'

export default function ReviewResult({ result, originalCode }) {
  // Mapa de índice → respuesta del /explain (para toggle expandir/cerrar)
  const [explanations, setExplanations] = useState({})
  const [loadingIdx,   setLoadingIdx]   = useState(null)

  if (!result) return null

  const handleExplain = async (suggestion, index) => {
    // Si ya está explicada, toggle para cerrar
    if (explanations[index]) {
      setExplanations(prev => {
        const next = { ...prev }
        delete next[index]
        return next
      })
      return
    }

    setLoadingIdx(index)
    try {
      const res = await explainSuggestion(
        suggestion,
        originalCode,
        result.language_detected,
        false
      )
      setExplanations(prev => ({ ...prev, [index]: res.data }))
    } catch (e) {
      console.error('Error al explicar sugerencia:', e)
    } finally {
      setLoadingIdx(null)
    }
  }

  const scoreColor = result.overall_score >= 7 ? 'green'
                   : result.overall_score >= 4 ? 'orange'
                   : 'red'

  return (
    <div style={{ marginTop: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>Resultado</h2>
        <span style={{ fontSize: '28px', fontWeight: 'bold', color: scoreColor }}>
          {result.overall_score}/10
        </span>
      </div>

      <p style={{ color: '#444', margin: '8px 0 20px' }}>{result.summary}</p>

      <h3>Sugerencias ({result.suggestions.length})</h3>
      {result.suggestions.map((s, i) => (
        <SuggestionCard
          key={i}
          suggestion={s}
          onClick={() => handleExplain(s, i)}
          isLoading={loadingIdx === i}
          explanation={explanations[i]}
        />
      ))}

      <h3>Código refactorizado</h3>
      <CodeBlock code={result.refactored_code} />
    </div>
  )
}
