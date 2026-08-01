import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import ReviewResult from '../ReviewResult'

// Mockeamos el módulo api para que no intente hacer fetch real
vi.mock('../../services/api', () => ({
  explainSuggestion: vi.fn()
}))

const BASE_RESULT = {
  language_detected: 'python',
  summary: 'El código está bien estructurado.',
  suggestions: [
    { severity: 'warning', category: 'readability', description: 'Usar mejores nombres.', line_hint: 'foo' }
  ],
  refactored_code: 'def better_name(): pass',
  overall_score: 8
}

describe('ReviewResult', () => {
  it('no renderiza nada cuando result es null', () => {
    const { container } = render(<ReviewResult result={null} originalCode="" />)
    expect(container).toBeEmptyDOMElement()
  })

  it('score en verde cuando >= 7', () => {
    render(<ReviewResult result={{ ...BASE_RESULT, overall_score: 8 }} originalCode="code" />)
    expect(screen.getByText('8/10')).toHaveStyle({ color: 'rgb(0, 128, 0)' })
  })

  it('score en naranja cuando entre 4 y 6', () => {
    render(<ReviewResult result={{ ...BASE_RESULT, overall_score: 5 }} originalCode="code" />)
    expect(screen.getByText('5/10')).toHaveStyle({ color: 'rgb(255, 165, 0)' })
  })

  it('score en rojo cuando < 4', () => {
    render(<ReviewResult result={{ ...BASE_RESULT, overall_score: 3 }} originalCode="code" />)
    expect(screen.getByText('3/10')).toHaveStyle({ color: 'rgb(255, 0, 0)' })
  })

  it('renderiza el summary', () => {
    render(<ReviewResult result={BASE_RESULT} originalCode="code" />)
    expect(screen.getByText('El código está bien estructurado.')).toBeInTheDocument()
  })

  it('renderiza todas las sugerencias con el contador', () => {
    const result = {
      ...BASE_RESULT,
      suggestions: [
        { severity: 'warning', category: 'readability', description: 'Problema uno.', line_hint: null },
        { severity: 'critical', category: 'bug', description: 'Problema dos.', line_hint: null }
      ]
    }
    render(<ReviewResult result={result} originalCode="code" />)
    expect(screen.getByText('Sugerencias (2)')).toBeInTheDocument()
    expect(screen.getByText(/Problema uno/)).toBeInTheDocument()
    expect(screen.getByText(/Problema dos/)).toBeInTheDocument()
  })

  it('renderiza el código refactorizado', () => {
    render(<ReviewResult result={BASE_RESULT} originalCode="code" />)
    expect(screen.getByText('def better_name(): pass')).toBeInTheDocument()
  })
})
