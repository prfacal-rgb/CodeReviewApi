import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import SuggestionCard from '../SuggestionCard'

const SUGGESTION = {
  severity: 'warning',
  category: 'readability',
  description: 'Excessive use of casts.',
  line_hint: '_call_anthropic'
}

const EXPLANATION = {
  why_it_matters: 'It matters a lot.',
  detailed_explanation: 'Here is the full explanation.',
  example_fix: 'Use isinstance() instead.',
  references: ['PEP 484']
}

describe('SuggestionCard', () => {
  it('renderiza categoría y descripción', () => {
    render(<SuggestionCard suggestion={SUGGESTION} onClick={() => {}} />)
    expect(screen.getByText(/readability/)).toBeInTheDocument()
    expect(screen.getByText(/Excessive use of casts/)).toBeInTheDocument()
  })

  it('renderiza el line_hint', () => {
    render(<SuggestionCard suggestion={SUGGESTION} onClick={() => {}} />)
    expect(screen.getByText(/_call_anthropic/)).toBeInTheDocument()
  })

  it('muestra hint de click cuando no hay explicación', () => {
    render(<SuggestionCard suggestion={SUGGESTION} onClick={() => {}} />)
    expect(screen.getByText(/Click para explicación detallada/)).toBeInTheDocument()
  })

  it('llama onClick al hacer click', () => {
    const onClick = vi.fn()
    render(<SuggestionCard suggestion={SUGGESTION} onClick={onClick} />)
    fireEvent.click(screen.getByText(/Excessive use of casts/))
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('muestra texto de carga cuando isLoading=true', () => {
    render(<SuggestionCard suggestion={SUGGESTION} onClick={() => {}} isLoading={true} />)
    expect(screen.getByText(/Generando explicación/)).toBeInTheDocument()
  })

  it('muestra la explicación cuando se provee', () => {
    render(<SuggestionCard suggestion={SUGGESTION} onClick={() => {}} explanation={EXPLANATION} />)
    expect(screen.getByText('It matters a lot.')).toBeInTheDocument()
    expect(screen.getByText('Here is the full explanation.')).toBeInTheDocument()
    expect(screen.getByText('PEP 484')).toBeInTheDocument()
  })

  it('muestra hint de cerrar cuando hay explicación', () => {
    render(<SuggestionCard suggestion={SUGGESTION} onClick={() => {}} explanation={EXPLANATION} />)
    expect(screen.getByText(/Click para cerrar/)).toBeInTheDocument()
  })
})
