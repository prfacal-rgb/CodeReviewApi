import { useState } from 'react'

// Saca los markdown fences si el modelo los incluye (```python ... ```)
function stripFences(text) {
  if (!text) return ''
  return text
    .replace(/^```[\w]*\n?/, '')   // saca el ``` del inicio
    .replace(/\n?```\s*$/, '')     // saca el ``` del final
    .trim()
}

export default function CodeBlock({ code }) {
  const [copied, setCopied] = useState(false)
  const clean = stripFences(code)

  const handleCopy = () => {
    navigator.clipboard.writeText(clean)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div style={{ position: 'relative', margin: '8px 0' }}>
      <button
        onClick={e => { e.stopPropagation(); handleCopy() }}
        style={{
          position: 'absolute', top: '8px', right: '8px',
          padding: '3px 10px', fontSize: '11px',
          background: copied ? '#22c55e' : '#374151',
          color: 'white', border: 'none',
          borderRadius: '4px', cursor: 'pointer',
          transition: 'background 0.2s'
        }}
      >
        {copied ? '✓ Copiado' : 'Copiar'}
      </button>
      <pre style={{
        background: '#1e1e1e',
        color: '#d4d4d4',
        margin: 0,
        padding: '36px 16px 16px 16px',   // espacio arriba para el botón
        borderRadius: '8px',
        fontSize: '13px',
        lineHeight: '1.6',
        overflow: 'auto',
        textAlign: 'left',                  // ← fix del centrado
        whiteSpace: 'pre',                  // preserva tabs y espacios exactos
        fontFamily: "'Consolas', 'Monaco', 'Courier New', monospace"
      }}>
        {clean}
      </pre>
    </div>
  )
}
