import { useState, useEffect } from 'react'
import { fetchModels } from '../services/api'

export default function ModelSelector({ value, onChange, disabled }) {
  const [models,  setModels]  = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchModels()
      .then(setModels)
      .catch(() => setModels([]))
      .finally(() => setLoading(false))
  }, [])

  const groups = models.reduce((acc, m) => {
    acc[m.group] = acc[m.group] || []
    acc[m.group].push(m)
    return acc
  }, {})

  const groupLabel = { local: '💻 Local', cloud: '☁️ Cloud' }

  return (
    <div className="space-y-1.5">
      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
        Modelo
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled || loading}
        className="
          w-full px-3 py-2.5 rounded-xl border text-sm
          bg-white dark:bg-slate-800
          border-slate-300 dark:border-slate-600
          text-slate-900 dark:text-slate-100
          focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors duration-150
        "
      >
        {loading && <option>Cargando modelos…</option>}
        {Object.entries(groups).map(([group, items]) => (
          <optgroup key={group} label={groupLabel[group] || group}>
            {items.map((m) => (
              <option key={m.id} value={m.id}>{m.display_name}</option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  )
}
