# Code Review API

AI-powered code review tool with a FastAPI backend and a React frontend. Supports multiple LLM providers (Anthropic, Groq, Google AI Studio, and local Ollama) through a unified, swappable provider abstraction.

Herramienta de revisión de código asistida por IA, con backend en FastAPI y frontend en React. Soporta múltiples proveedores de LLM (Anthropic, Groq, Google AI Studio, y Ollama local) mediante una capa de abstracción intercambiable.

---

## Features / Características

- **Code review**: paste code, upload a file, or upload an image of code and get a structured review — score, warnings, and suggested fixes.
- **Explain mode**: get a deeper, plain-language explanation of a specific suggestion.
- **Multi-provider**: switch between Anthropic, Groq, Google AI Studio, and a local Ollama instance from the UI, with automatic fallback handling.
- **Dark mode** in the frontend.
- Full test suite: `pytest` on the backend, `vitest` + React Testing Library on the frontend.

- **Revisión de código**: pegá código, subí un archivo, o subí una imagen de código y obtené un review estructurado — score, advertencias y sugerencias de corrección.
- **Modo explicación**: obtené una explicación más profunda y en lenguaje simple sobre una sugerencia puntual.
- **Multi-proveedor**: cambiá entre Anthropic, Groq, Google AI Studio, y una instancia local de Ollama desde la interfaz, con manejo automático de fallback.
- **Modo oscuro** en el frontend.
- Suite de tests completa: `pytest` en el backend, `vitest` + React Testing Library en el frontend.

---

## Tech stack

**Backend**
- Python 3.12, FastAPI, Uvicorn
- Pydantic / Pydantic Settings
- Anthropic SDK, OpenAI SDK (used as an OpenAI-compatible client for Groq, Google AI Studio, and Ollama)

**Frontend**
- React 19, Vite
- Tailwind CSS
- Axios
- Vitest, React Testing Library

**Infrastructure**
- Docker & Docker Compose (development mode with hot-reload)
- nginx config included for a future production build

---

## Getting started / Cómo empezar

### Requirements / Requisitos

- Docker Engine + Docker Compose v2
- API keys for the providers you want to use (Anthropic, Groq, and/or Google AI Studio), and/or a reachable Ollama instance

### Environment variables / Variables de entorno

Create a `.env` file in the project root (never commit this file):

Creá un archivo `.env` en la raíz del proyecto (nunca se sube al repo):

```env
ANTHROPIC_API_KEY=
GROQ_API_KEY=
GROQ_BASE_URL=https://api.groq.com/openai/v1
GOOGLE_API_KEY=
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
OLLAMA_BASE_URL=http://<host>:11434/v1
MAX_TOKENS=4096
```

### Run with Docker / Correr con Docker

```bash
docker compose up --build
```

- Backend: `http://localhost:8000` (health check at `/health`)
- Frontend: `http://localhost:5173`

This runs in **development mode**: uvicorn with `--reload` and the Vite dev server, both with hot-reload via mounted volumes.

Esto corre en **modo desarrollo**: uvicorn con `--reload` y el servidor de desarrollo de Vite, ambos con hot-reload vía volúmenes montados.

### Run locally without Docker / Correr localmente sin Docker

**Backend**
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend**
```bash
cd code-review-frontend
npm install
npm run dev
```

---

## Project structure / Estructura del proyecto

```
.
├── main.py                          # FastAPI app entrypoint
├── core/                            # Config, logging, exception handlers, provider abstraction
├── features/
│   ├── code_review/                 # Code review endpoint & service
│   └── explain/                     # Explain endpoint & service
├── tests/                           # Backend test suite (pytest)
├── code-review-frontend/            # React + Vite frontend
├── Dockerfile                       # Backend image
├── code-review-frontend/Dockerfile  # Frontend image (dev server)
├── docker-compose.yml
└── nginx.conf                       # For a future production frontend build
```

---

## Testing / Tests

**Backend**
```bash
pytest
```

**Frontend**
```bash
cd code-review-frontend
npm run test
```

---

## Roadmap

See [TODO.md](./TODO.md) for pending work, including a production Docker setup (nginx-served frontend build + non-reload backend).

Ver [TODO.md](./TODO.md) para el trabajo pendiente, incluyendo un setup de Docker para producción (frontend servido por nginx + backend sin reload).
