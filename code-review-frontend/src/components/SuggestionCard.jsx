const SEVERITY = {
  critical: {
    border:  'border-l-red-500',
    badge:   'bg-red-100 dark:bg-red-950/60 text-red-700 dark:text-red-400',
    label:   '🔴 CRÍTICO',
  },
  warning: {
    border:  'border-l-amber-400',
    badge:   'bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400',
    label:   '🟡 ADVERTENCIA',
  },
  info: {
    border:  'border-l-blue-400',
    badge:   'bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400',
    label:   '🔵 INFO',
  },
}

export default function SuggestionCard({ suggestion, onClick, isLoading, explanation }) {
  const cfg        = SEVERITY[suggestion.severity] || SEVERITY.info
  const hasExplain = !!explanation

  return (
    <div className={`rounded-xl border border-l-4 ${cfg.border} border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 overflow-hidden transition-shadow hover:shadow-sm`}>

      {/* ── Body ────────────────────────────────────────────────────── */}
      <div className="p-4 space-y-3">

        {/* Badges */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${cfg.badge}`}>
            {cfg.label}
          </span>
          <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            {suggestion.category}
          </span>
        </div>

        {/* Description */}
        <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed">
          {suggestion.description}
        </p>

        {/* How to fix */}
        {suggestion.how_to_fix && (
          <div className="space-y-1">
            <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Cómo corregirlo
            </p>
            <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              {suggestion.how_to_fix}
            </p>
          </div>
        )}

        {/* Example fix */}
        {suggestion.example_fix && (
          <pre className="text-xs font-mono bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-lg p-3 overflow-x-auto leading-relaxed">
            {suggestion.example_fix}
          </pre>
        )}

        {/* Explain button */}
        <button
          onClick={onClick}
          disabled={isLoading}
          className={[
            'text-xs font-medium px-3 py-1.5 rounded-lg transition-all duration-150',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            hasExplain
              ? 'bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400 hover:bg-indigo-200 dark:hover:bg-indigo-900'
              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-600',
          ].join(' ')}
        >
          {isLoading ? '⏳ Explicando…' : hasExplain ? '▲ Cerrar explicación' : '✨ Explicar en detalle'}
        </button>
      </div>

      {/* ── Explanation panel ────────────────────────────────────────── */}
      {hasExplain && (
        <div className="border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/60 p-4 space-y-4">

          <Section label="¿Por qué importa?">
            <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              {explanation.why_it_matters}
            </p>
          </Section>

          <Section label="Explicación detallada">
            <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
              {explanation.detailed_explanation}
            </p>
          </Section>

          {explanation.example_fix && (
            <Section label="Ejemplo corregido">
              <pre className="text-xs font-mono bg-slate-950 text-green-400 rounded-lg p-3 overflow-x-auto leading-relaxed">
                {explanation.example_fix}
              </pre>
            </Section>
          )}

          {explanation.references?.length > 0 && (
            <Section label="Referencias">
              <ul className="space-y-0.5">
                {explanation.references.map((ref, i) => (
                  <li key={i} className="text-xs text-indigo-600 dark:text-indigo-400">• {ref}</li>
                ))}
              </ul>
            </Section>
          )}
        </div>
      )}
    </div>
  )
}

function Section({ label, children }) {
  return (
    <div className="space-y-1">
      <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
        {label}
      </p>
      {children}
    </div>
  )
}
