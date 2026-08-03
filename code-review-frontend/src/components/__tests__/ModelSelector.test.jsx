import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ModelSelector from '../ModelSelector'

// Mock del módulo completo de api
vi.mock('../../services/api', () => ({
  fetchModels: vi.fn(),
}))

import { fetchModels } from '../../services/api'

const MOCK_MODELS = [
  { id: 'ollama-fast', display_name: 'Ollama — qwen2.5-coder:14b (Rápido)', group: 'local' },
  { id: 'ollama-deep', display_name: 'Ollama — qwen2.5-coder:32b (Profundo)', group: 'local' },
  { id: 'groq',        display_name: 'Groq — Llama 3.3 70B',                 group: 'cloud' },
  { id: 'anthropic',   display_name: 'Anthropic — Claude Haiku',              group: 'cloud' },
]

describe('ModelSelector', () => {
  beforeEach(() => {
    fetchModels.mockResolvedValue(MOCK_MODELS)
  })

  it('deshabilita el select mientras carga', () => {
    // Promise que nunca resuelve → estado loading perpetuo
    fetchModels.mockReturnValue(new Promise(() => {}))
    render(<ModelSelector value="ollama-fast" onChange={() => {}} />)
    expect(screen.getByRole('combobox')).toBeDisabled()
  })

  it('muestra las opciones después de cargar', async () => {
    render(<ModelSelector value="ollama-fast" onChange={() => {}} />)
    await waitFor(() => {
      expect(screen.getByRole('option', { name: /qwen2\.5-coder:14b/ })).toBeInTheDocument()
      expect(screen.getByRole('option', { name: /Groq/ })).toBeInTheDocument()
    })
  })

  it('refleja el value seleccionado en el select', async () => {
    render(<ModelSelector value="groq" onChange={() => {}} />)
    await waitFor(() => {
      expect(screen.getByRole('combobox')).toHaveValue('groq')
    })
  })

  it('llama onChange con el model_id como string al cambiar', async () => {
    const onChange = vi.fn()
    render(<ModelSelector value="ollama-fast" onChange={onChange} />)
    await waitFor(() => {
      expect(screen.getByRole('option', { name: /Groq/ })).toBeInTheDocument()
    })
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'groq' } })
    expect(onChange).toHaveBeenCalledWith('groq')   // string, no boolean
  })

  it('habilita el select después de cargar', async () => {
    render(<ModelSelector value="ollama-fast" onChange={() => {}} />)
    await waitFor(() => {
      expect(screen.getByRole('combobox')).not.toBeDisabled()
    })
  })
})
