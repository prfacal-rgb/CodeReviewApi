import { useState } from 'react'

export default function CodeBlock({ code }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      /* clipboard puede fallar en contextos inseguros */
    }
  }

  return (
    <div className="rounded-xl overflow-hidden border border-slate-700">
      {/* Barra estilo editor */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-800 border-b border-slate-700">
        <div className="flex gap-1.5">
          <span className="w-3 h-3 rounded-full bg-red-500"   aria-hidden />
          <span className="w-3 h-3 rounded-full bg-amber-400" aria-hidden />
          <span className="w-3 h-3 rounded-full bg-green-500" aria-hidden />
        </div>
        <button
          onClick={handleCopy}
          className="text-xs text-slate-400 hover:text-slate-200 transition-colors px-2 py-1 rounded-md hover:bg-slate-700"
        >
          {copied ? '✅ Copiado' : '📋 Copiar'}
        </button>
      </div>

      <pre className="bg-slate-950 text-slate-200 p-4 text-sm font-mono leading-relaxed overflow-x-auto whitespace-pre-wrap break-words">
        {code}
      </pre>
    </div>
  )
}
