import { useRef } from 'react'

const ACCEPT_CODE  = '.py,.js,.ts,.jsx,.tsx,.cs,.java,.go,.rs,.cpp,.c,.php,.rb,.swift,.kt,.sql,.html,.css'
const ACCEPT_IMAGE = 'image/png,image/jpeg,image/webp,image/gif'

export default function CodeInput({ code, onChange, onFileUpload, onImageUpload, disabled }) {
  const fileRef = useRef(null)
  const imgRef  = useRef(null)

  const handleFile = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => onFileUpload(ev.target.result)
    reader.readAsText(file)
    e.target.value = ''
  }

  const handleImage = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      const base64 = ev.target.result.split(',')[1]
      onImageUpload(base64, file.type)
    }
    reader.readAsDataURL(file)
    e.target.value = ''
  }

  const charCount = code.length
  const charColor = charCount > 3000
    ? 'text-red-500'
    : charCount > 1500
    ? 'text-amber-500'
    : 'text-slate-400 dark:text-slate-500'

  return (
    <div className="space-y-1.5">
      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
        Código a revisar
      </label>

      <div className="rounded-xl border border-slate-300 dark:border-slate-600 overflow-hidden focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-transparent transition-all duration-150">
        <textarea
          value={code}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          placeholder="// Pegá tu código aquí, o usá los botones para cargar un archivo o imagen…"
          spellCheck={false}
          className="
            w-full h-72 p-4 resize-none font-mono text-sm leading-relaxed
            bg-white dark:bg-slate-800
            text-slate-900 dark:text-slate-100
            placeholder-slate-400 dark:placeholder-slate-500
            focus:outline-none
            disabled:opacity-60
          "
        />

        {/* Toolbar */}
        <div className="flex items-center justify-between px-4 py-2 bg-slate-50 dark:bg-slate-800/60 border-t border-slate-200 dark:border-slate-700">
          <span className={`text-xs font-mono tabular-nums ${charColor}`}>
            {charCount > 0 ? `${charCount.toLocaleString()} caracteres` : 'Sin contenido'}
          </span>

          <div className="flex gap-2">
            <input ref={fileRef}  type="file" className="hidden" accept={ACCEPT_CODE}  onChange={handleFile} />
            <input ref={imgRef}   type="file" className="hidden" accept={ACCEPT_IMAGE} onChange={handleImage} />

            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              disabled={disabled}
              className="
                flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg
                bg-white dark:bg-slate-700
                border border-slate-300 dark:border-slate-600
                text-slate-600 dark:text-slate-300
                hover:bg-slate-100 dark:hover:bg-slate-600
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-colors duration-150
              "
            >
              📎 Archivo
            </button>

            <button
              type="button"
              onClick={() => imgRef.current?.click()}
              disabled={disabled}
              className="
                flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg
                bg-white dark:bg-slate-700
                border border-slate-300 dark:border-slate-600
                text-slate-600 dark:text-slate-300
                hover:bg-slate-100 dark:hover:bg-slate-600
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-colors duration-150
              "
            >
              📷 Imagen
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
