# Technology Stack

**Analysis Date:** 2026-05-27

## Languages

**Primary:**
- Python 3.11+ (requires >=3.11, tested up to 3.14) - Backend, core logic, CLI
- JavaScript (ES modules) - Frontend web UI

**Secondary:**
- Shell scripts - Deployment and workflow automation

## Runtime

**Environment:**
- Python 3.11+ runtime
- Node.js 20.19.0 (specified in `web-ui/.nvmrc`)

**Package Manager:**
- Python: pip (with optional virtual environment)
- Node.js: npm
- Lockfiles: `package-lock.json` present for frontend

## Frameworks

**Core:**
- FastAPI 0.136.1+ - Web UI backend API server (`backend/main.py`)
- React 19.2.5 - Frontend UI framework (`web-ui/`)
- Uvicorn 0.46.0+ - ASGI server for FastAPI

**Testing:**
- pytest 9.0.3+ - Python unit/integration tests (`tests/`, `pytest.ini`)
- Vitest 4.1.5+ - JavaScript unit tests (`web-ui/`)
- Playwright 1.59.1+ - E2E browser tests (`web-ui/`)
- pytest-cov 7.1.0+ - Coverage reporting

**Build/Dev:**
- Vite 8.0.10+ - Frontend build tool and dev server (`web-ui/vite.config.js`)
- TailwindCSS 4.2.4+ - CSS framework (`web-ui/tailwind.config.js`)
- ESLint 10.2.1+ - JavaScript linting (`web-ui/eslint.config.js`)

## Key Dependencies

**Critical:**
- `openai` 2.33.0+ - OpenAI API client for LLM-based reference extraction (`src/refchecker/llm/providers.py`)
- `anthropic` 0.97.0+ - Anthropic Claude API client for LLM extraction (`src/refchecker/llm/providers.py`)
- `google-genai` 1.73.1+ - Google Gemini API client for LLM extraction (`src/refchecker/llm/providers.py`)
- `requests` 2.33.1+ - HTTP client for external API calls (Crossref, OpenAlex, arXiv, etc.)
- `arxiv` 3.0.0+ - arXiv API wrapper for paper metadata (`src/refchecker/core/refchecker.py`)
- `pypdf` 6.10.2+ - PDF text extraction (`requirements.txt`)
- `pdfplumber` 0.11.9+ - Enhanced PDF parsing (`requirements.txt`)
- `pymupdf` 1.27.2.3+ - PDF thumbnail generation (`backend/thumbnail.py`)

**Infrastructure:**
- `aiosqlite` 0.22.1+ - Async SQLite database for check history and user data (`backend/database.py`)
- `httpx` 0.27.0+ - Async HTTP client for OAuth flows (`backend/auth.py`)
- `python-jose[cryptography]` 3.5.0+ - JWT token creation/validation for multi-user auth (`backend/auth.py`)
- `cryptography` 47.0.0+ - API key encryption in database (`backend/database.py`)
- `beautifulsoup4` 4.14.3+ - HTML parsing for web scraping (`requirements.txt`)
- `pandas` 3.0.2+ - Data manipulation and analysis (`requirements.txt`)
- `pybtex` 0.26.1+ - BibTeX parsing for arXiv citations (`requirements.txt`)

**Frontend:**
- `axios` 1.15.2+ - HTTP client for API calls (`web-ui/package.json`)
- `zustand` 5.0.12+ - State management (`web-ui/package.json`)

**Optional:**
- `vllm` 0.20.0+ - Local model inference (optional, not in default requirements) (`pyproject.toml[vllm]`)
- `huggingface_hub` 1.12.0+ - HuggingFace model downloads for local inference (`requirements.txt`)
- `torch` 2.11.0+ - PyTorch for vLLM (optional) (`pyproject.toml[vllm]`)
- `nltk` 3.9.4+ - Natural language processing enhancements (`requirements.txt`)
- `scikit-learn` 1.8.0+ - ML features (optional) (`requirements.txt`)
- `lxml` 6.1.0+ - XML/HTML parsing (`requirements.txt`)
- `pikepdf` 10.5.1+ - Advanced PDF manipulation (`requirements.txt`)

## Configuration

**Environment:**
- Configuration via environment variables (`.env` file or system env)
- Example configuration: `.env.example`
- Key configs required:
  - LLM API keys: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY` (at least one)
  - Multi-user mode (optional): `REFCHECKER_MULTIUSER=true`
  - OAuth credentials (if multi-user): `GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID`, `MS_CLIENT_ID`, etc.
  - JWT secret: `JWT_SECRET_KEY` (auto-generated if not set)
  - Data directory: `REFCHECKER_DATA_DIR` (defaults to `backend/data` or `/app/data` in Docker)
  - GROBID server: `GROBID_URL` (optional, for PDF fallback extraction)

**Build:**
- Python: `pyproject.toml` (setuptools backend) defines project metadata and dependencies
- Frontend: `web-ui/vite.config.js` for build configuration
- Docker: `Dockerfile` (multi-stage build) and `docker-compose.yml`
- Requirements split:
  - `requirements.txt` - Full development/local install
  - `requirements-docker.txt` - Lightweight Docker image (excludes vLLM/torch)
  - `requirements-dev.txt` - Development tools (if exists)

## Platform Requirements

**Development:**
- Python 3.11+ interpreter
- Node.js 20.19.0+ (for frontend development)
- Optional: Docker + Docker Compose (for GROBID service)
- Optional: CUDA-capable GPU + torch + vLLM (for local model inference)

**Production:**
- Deployment target: Docker container (`ghcr.io/markrussinovich/refchecker:latest`)
- Container runtime: Python 3.11-slim base image
- Port: 8000 (configurable via `PORT` env var)
- Platform support: Linux (primary), Windows, macOS (development)
- Container orchestration: Docker Compose with GROBID sidecar service
- External dependency: GROBID service (Docker image `lfoppiano/grobid:0.8.2`) for PDF reference extraction fallback

---

*Stack analysis: 2026-05-27*
