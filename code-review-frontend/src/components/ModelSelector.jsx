// Props:
//   deep: boolean — false = fast, true = deep
//   onChange: función que recibe el nuevo valor boolean
export default function ModelSelector({ deep, onChange }) {
  return (
    <div style={{ marginBottom: '12px' }}>
      <label style={{ fontWeight: 'bold', marginRight: '8px' }}>
        Modelo:
      </label>
      <select
        value={deep ? 'deep' : 'fast'}
        onChange={e => onChange(e.target.value === 'deep')}
        style={{
          padding: '6px 12px',
          borderRadius: '6px',
          border: '1px solid #ccc',
          fontSize: '14px'
        }}
      >
        <option value="fast">Rápido — qwen2.5-coder:14b</option>
        <option value="deep">Profundo — qwen2.5-coder:32b</option>
      </select>
    </div>
  )
}