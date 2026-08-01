import { useRef } from 'react'

export default function CodeInput({ code, onChange, onFileUpload, onImageUpload }) {
  const fileRef = useRef()   // referencia al input[type=file] oculto para código
  const imgRef  = useRef()   // referencia al input[type=file] oculto para imágenes

  // Lee el archivo de texto y pasa el contenido al padre
  const handleFile = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => onFileUpload(ev.target.result)
    reader.readAsText(file)
  }

  // Lee la imagen, la convierte a base64 y pasa al padre
  const handleImage = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      // ev.target.result = "data:image/png;base64,ABC123..."
      // necesitamos solo "ABC123..." (lo que está después de la coma)
      const base64 = ev.target.result.split(',')[1]
      onImageUpload(base64, file.type)
    }
    reader.readAsDataURL(file)
  }

  return (
    <div>
      {/* Botones que disparan los inputs ocultos */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
        <button onClick={() => fileRef.current.click()} style={btnStyle}>
          📄 Subir archivo
        </button>
        <button onClick={() => imgRef.current.click()} style={btnStyle}>
          🖼️ Subir imagen
        </button>
      </div>

      {/* Inputs ocultos — el usuario los "ve" a través de los botones de arriba */}
      <input
        ref={fileRef}
        type="file"
        accept=".py,.js,.cs,.ts,.java,.go,.rs"
        style={{ display: 'none' }}
        onChange={handleFile}
      />
      <input
        ref={imgRef}
        type="file"
        accept="image/*"
        style={{ display: 'none' }}
        onChange={handleImage}
      />

      <textarea
        value={code}
        onChange={e => onChange(e.target.value)}
        placeholder="Pegá tu código aquí..."
        rows={14}
        style={{
          width: '100%',
          fontFamily: 'monospace',
          fontSize: '13px',
          padding: '12px',
          borderRadius: '8px',
          border: '1px solid #ccc',
          boxSizing: 'border-box',
          resize: 'vertical'
        }}
      />
    </div>
  )
}

const btnStyle = {
  padding: '6px 14px',
  borderRadius: '6px',
  border: '1px solid #ccc',
  cursor: 'pointer',
  background: '#f5f5f5',
  fontSize: '13px'
}
