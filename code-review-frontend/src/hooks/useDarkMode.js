import { useState, useEffect } from 'react'

/**
 * Hook para dark/light mode con persistencia en localStorage.
 * Arranca respetando la preferencia del sistema si no hay nada guardado.
 *
 * @returns {[boolean, Function]} [isDark, setDark]
 */
export function useDarkMode() {
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem('theme')
    if (saved) return saved === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  return [dark, setDark]
}
