import CodeBlock from './CodeBlock'    // ← agregar import arriba
const colors = { critical: '#fee2e2', warning: '#fef9c3', info: '#dbeafe' }
const icons  = { critical: '🔴', warning: '🟡', info: '🔵' }

export default function SuggestionCard({ suggestion, onClick, isLoading, explanation }) {
  return (
    <div
      onClick={onClick}
      onMouseEnter={e => e.currentTarget.style.borderColor = '#93c5fd'}
      onMouseLeave={e => e.currentTarget.style.borderColor = 'transparent'}
      style={{
        background: colors[suggestion.severity] || '#f5f5f5',
        borderRadius: '8px',
        padding: '12px',
        marginBottom: '10px',
        cursor: 'pointer',
        border: '2px solid transparent',
        transition: 'border-color 0.15s',
      }}
    >
      {/* Cabecera de la sugerencia */}
      <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
        {icons[suggestion.severity]} [{suggestion.category}] {suggestion.description}
      </div>
      {suggestion.line_hint && (
        <div style={{ fontSize: '12px', color: '#555' }}>📍 {suggestion.line_hint}</div>
      )}

      {/* Hint de que es clickeable */}
      {!isLoading && !explanation && (
        <div style={{ marginTop: '6px', fontSize: '11px', color: '#888' }}>
          🔎 Click para explicación detallada
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div style={{ marginTop: '8px', fontSize: '13px', color: '#555' }}>
          ⏳ Generando explicación...
        </div>
      )}

      {/* Explicación expandida */}
      {explanation && (
        <div style={{
          marginTop: '12px',
          borderTop: '1px solid rgba(0,0,0,0.1)',
          paddingTop: '10px'
        }}>
          <div style={{ marginBottom: '10px' }}>
            <strong>¿Por qué importa?</strong>
            <p style={{ margin: '4px 0', fontSize: '13px' }}>{explanation.why_it_matters}</p>
          </div>

          <div style={{ marginBottom: '10px' }}>
            <strong>Explicación</strong>
            <p style={{ margin: '4px 0', fontSize: '13px' }}>{explanation.detailed_explanation}</p>
          </div>

          <div style={{ marginBottom: '10px' }}>
            <strong>Cómo corregirlo</strong>
            <CodeBlock code={explanation.example_fix} />
          </div>

          {explanation.references?.length > 0 && (
            <div>
              <strong>Referencias</strong>
              <ul style={{ margin: '4px 0', paddingLeft: '20px', fontSize: '13px' }}>
                {explanation.references.map((ref, i) => <li key={i}>{ref}</li>)}
              </ul>
            </div>
          )}

          <div style={{ marginTop: '8px', fontSize: '11px', color: '#888' }}>
            🔼 Click para cerrar
          </div>
        </div>
      )}
    </div>
  )
}
