import { describe, it, expect } from 'vitest'

describe('api service — exports', () => {
  it('exporta reviewCode', async () => {
    const mod = await import('../api')
    expect(typeof mod.reviewCode).toBe('function')
  })

  it('exporta reviewCodeStream', async () => {
    const mod = await import('../api')
    expect(typeof mod.reviewCodeStream).toBe('function')
  })

  it('exporta reviewFromImage', async () => {
    const mod = await import('../api')
    expect(typeof mod.reviewFromImage).toBe('function')
  })

  it('exporta explainSuggestion', async () => {
    const mod = await import('../api')
    expect(typeof mod.explainSuggestion).toBe('function')
  })
})
