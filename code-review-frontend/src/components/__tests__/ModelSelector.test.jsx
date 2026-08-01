import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ModelSelector from '../ModelSelector'

describe('ModelSelector', () => {
  it('muestra opción Rápido seleccionada por defecto', () => {
    render(<ModelSelector deep={false} onChange={() => {}} />)
    expect(screen.getByRole('combobox')).toHaveValue('fast')
  })

  it('muestra opción Profundo cuando deep=true', () => {
    render(<ModelSelector deep={true} onChange={() => {}} />)
    expect(screen.getByRole('combobox')).toHaveValue('deep')
  })

  it('llama onChange con true al seleccionar Profundo', () => {
    const onChange = vi.fn()
    render(<ModelSelector deep={false} onChange={onChange} />)
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'deep' } })
    expect(onChange).toHaveBeenCalledWith(true)
  })

  it('llama onChange con false al seleccionar Rápido', () => {
    const onChange = vi.fn()
    render(<ModelSelector deep={true} onChange={onChange} />)
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'fast' } })
    expect(onChange).toHaveBeenCalledWith(false)
  })
})
