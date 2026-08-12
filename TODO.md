# TODO / Notas técnicas

## Pylance — suprimir errores en dicts anidados pasados al SDK de Anthropic

Cuando `messages=[...]` con content blocks anidados genera múltiples squiggles en Pylance
(porque el SDK tipea `messages` como `Iterable[MessageParam]` y los dicts no matchean exacto),
el `# type: ignore[arg-type]` solo suprime la línea donde está pero no los dicts internos.

**Solución limpia:** asignar el payload a una variable tipada como `Any` antes de pasarla:

```python
from typing import Any

img_messages: Any = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": request.mime_type,
                    "data": request.image_base64,
                }
            },
            {
                "type": "text",
                "text": "..."
            }
        ]
    }
]

message = client.messages.create(
    model=model,
    max_tokens=settings.max_tokens,
    system=SYSTEM_PROMPT,
    messages=img_messages   # ← sin type: ignore, Pylance no se queja
)
```

**Por qué funciona:** al tipar la variable como `Any`, Pylance deja de inferir
el tipo de los dicts internos. Equivale al `dynamic` de C#.

**Aplica a:** `features/code_review/service.py` → método `review_from_image()`

---

## Tests pendientes

### Backend — `tests/features/explain/`

Crear `tests/features/explain/test_service.py` y `test_router.py` siguiendo el mismo patrón
que los tests del slice `code_review`.

**test_service.py — casos a cubrir:**
- `_extract_json` strip de markdown fences (igual que en code_review)
- `ExplainService` con provider Ollama: llama a `client.chat.completions.create`
- `ExplainService` con provider Anthropic: llama a `client.messages.create`
- Respuesta correcta devuelve `ExplainResponse` con los campos esperados
- Error de autenticación → `AIAuthenticationError`
- Error de conexión → `AIUnavailableError`

**test_router.py — casos a cubrir:**
- `POST /explain` con mock service → 200 y estructura correcta
- `POST /explain` con `original_code` demasiado corto → 422
- `POST /explain` sin `suggestion` → 422

**Fixtures necesarias en `tests/conftest.py`:**
```python
MOCK_EXPLAIN = {
    "why_it_matters": "...",
    "detailed_explanation": "...",
    "example_fix": "...",
    "references": ["PEP 484"]
}

@pytest.fixture
def mock_explain_service(mock_ollama_client):
    return ExplainService(mock_ollama_client, AIProvider.ollama)
```

**`app.dependency_overrides`** para test_router:
```python
from features.explain.router import get_explain_service
app.dependency_overrides[get_explain_service] = lambda: mock_explain_service
```

---

### Backend — tests de `review_from_image`

En `tests/features/code_review/test_service.py` agregar:
- `review_from_image` con provider Ollama → lanza `AIUnavailableError` (no soportado)
- `review_from_image` con provider Anthropic → devuelve `ReviewResponse`

---

### Frontend — tests con Vitest + React Testing Library

Setup:
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

Agregar en `vite.config.js`:
```js
test: {
  environment: 'jsdom',
  globals: true,
  setupFiles: './src/test/setup.js'
}
```

Crear `src/test/setup.js`:
```js
import '@testing-library/jest-dom'
```

**Casos a cubrir:**

`src/components/__tests__/ModelSelector.test.jsx`
- Renderiza el dropdown con opción "Rápido" seleccionada por defecto
- Al cambiar a "Profundo" llama a onChange con `true`

`src/components/__tests__/SuggestionCard.test.jsx`
- Renderiza severidad, categoría y descripción
- Muestra "Click para explicación detallada" cuando no hay explicación
- Llama a onClick al hacer click
- Muestra el contenido de `explanation` cuando se pasa

`src/components/__tests__/ReviewResult.test.jsx`
- Renderiza score con color correcto (verde ≥7, naranja 4-6, rojo <4)
- Renderiza todas las sugerencias
- Muestra el código refactorizado

`src/services/__tests__/api.test.js`
- Mockear axios y verificar que `reviewCode` llama a POST /reviews con el body correcto
- Verificar que `explainSuggestion` llama a POST /explain con el body correcto

---

## Docker — modo producción (pendiente)

Ya tenemos docker-compose funcionando en modo dev (uvicorn --reload + vite dev server).

Falta armar variante de producción:
- Frontend: build con `npm run build` → servir con nginx usando `nginx.conf` (ya existe en el repo, config lista con SPA routing + cache + gzip)
- Backend: correr uvicorn sin --reload, posiblemente con más workers
- Un `docker-compose.prod.yml` separado, o profiles en el mismo compose

No urgente, probar cuando haga falta un entorno más realista.
