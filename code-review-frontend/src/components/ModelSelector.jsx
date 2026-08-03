import { useEffect, useState } from 'react'
import { fetchModels } from '../services/api'

export default function ModelSelector({ value, onChange, disabled }) {
  const [models, setModels]   = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchModels()
      .then(setModels)
      .catch(() => setModels([]))
      .finally(() => setLoading(false))
  }, [])

  // Agrupa los modelos por el campo "group": { local: [...], cloud: [...] }
  const groups = models.reduce((acc, m) => {
    const g = m.group ?? 'cloud'
    if (!acc[g]) acc[g] = []
    acc[g].push(m)
    return acc
  }, {})

  const groupLabel = { local: '💻 Local', cloud: '☁️ Cloud' }

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled || loading}
      style={{ padding: '6px 10px', borderRadius: '6px', fontSize: '0.9rem' }}
    >
      {loading && <option>Cargando modelos...</option>}
      {Object.entries(groups).map(([group, items]) => (
        <optgroup key={group} label={groupLabel[group] ?? group}>
          {items.map((m) => (
            <option key={m.id} value={m.id}>
              {m.display_name}
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  )
}
