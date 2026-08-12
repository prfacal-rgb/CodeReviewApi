import { useState } from 'react'
import SuggestionCard from './SuggestionCard'
import CodeBlock      from './CodeBlock'
import { explainSuggestion } from '../services/api'

function scoreStyle(score) {
  if (score >= 8) return { ring: 'border-green-500 text-green-600 dark:text-green-400',  bg: 'bg-green-50  dark:bg-green-950/20  border-green-200  dark:border-green-800'  }
  if (score >= 5) return { ring: 'border-amber-400 text-amber-600 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800' }
  return               { ring: 'border-red-500   text-red-600   dark:text-red-400',   bg: 'bg-red-50   dark:bg-red-950/20   border-red-200   dark:border-red-800'   }
}

export default function ReviewResult({ result, originalCode, modelId }) {
  const [explanations, setExplanations] = useState({})
  const [loadingIdx,   setLoadingIdx]   = useState(null)

  if (!result) return null

  const handleExplain = async (suggestion, index) => {
    if (explanations[index]) {
      setExplanations(prev => { const next = { ...prev }; delete next[index]; return next })
      return
    }
    setLoadingIdx(index)
    try {
      const res = await explainSuggestion(originalCode, result.language_detected, suggestion, modelId)
      setExplanations(prev => ({ ...prev, [index]: res }))
    } catch (e) {
      console.error('Error al explicar sugerencia:', e)
    } finally {
      setLoadingIdx(null)
    }
  }

  const { ring, bg } = scoreStyle(result.overall_score)

  const criticalCount = result.suggestions.filter(s => s.severity === 'critical').length
  const warningCount  = result.suggestions.filter(s => s.severity === 'warning').length

  return (
    <div className="space-y-8">

      {/* ── Score + summary ─────────────────────────────────────────── */}
      <div className={`rounded-xl border-2 p-6 ${bg}`}>
        <div className="flex items-start gap-6">

          {/* Score ring */}
          <div className={`shrink-0 w-20 h-20 rounded-full border-4 flex flex-col items-center justify-center ${ring}`}>
            <span className="text-2xl font-bold leading-none">{result.overall_score}</span>
            <span className="text-xs font-medium opacity-70">/10</span>
          </div>

          {/* Summary */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <h2 className="text-base font-bold">Resultado del análisis</h2>
              <span className="text-xs font-mono bg-white/60 dark:bg-black/20 px-2 py-0.5 rounded-full text-slate-600 dark:text-slate-400">
                {result.language_detected}
              </span>
            </div>
            <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              {result.summary}
            </p>
            <div className="flex flex-wrap gap-4 mt-3 text-xs font-medium">
              {criticalCount > 0 && (
                <span className="text-red-600 dark:text-red-400">
                  🔴 {criticalCount} crítico{criticalCount !== 1 ? 's' : ''}
                </span>
              )}
              {warningCount > 0 && (
                <span className="text-amber-600 dark:text-amber-400">
                  🟡 {warningCount} advertencia{warningCount !== 1 ? 's' : ''}
                </span>
              )}
              <span className="text-slate-500 dark:text-slate-400">
                {result.suggestions.length} sugerencia{result.suggestions.length !== 1 ? 's' : ''} en total
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ── Suggestions ─────────────────────────────────────────────── */}
      <div className="space-y-4">
        <h3 className="font-semibold text-base">
          Sugerencias{' '}
          <span className="text-slate-400 dark:text-slate-500 font-normal text-sm">
            ({result.suggestions.length})
          </span>
        </h3>
        {result.suggestions.map((s, i) => (
          <SuggestionCard
            key={i}
            suggestion={s}
            onClick={() => handleExplain(s, i)}
            isLoading={loadingIdx === i}
            explanation={explanations[i]}
          />
        ))}
      </div>

      {/* ── Refactored code ─────────────────────────────────────────── */}
      <div className="space-y-3">
        <h3 className="font-semibold text-base">Código refactorizado</h3>
        <CodeBlock code={result.refactored_code} />
      </div>

    </div>
  )
}
