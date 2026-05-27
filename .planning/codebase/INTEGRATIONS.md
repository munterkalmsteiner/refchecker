# External Integrations

**Analysis Date:** 2026-05-27

## APIs & External Services

**LLM Providers:**
- OpenAI - GPT models for reference extraction and verification
  - SDK/Client: `openai>=2.33.0`
  - Auth: `OPENAI_API_KEY` env var
  - Implementation: `src/refchecker/llm/providers.py` (OpenAIProvider, AzureOpenAIProvider, vLLMProvider classes)
  - Supports: GPT-4, GPT-5, o3/o4 reasoning models, Azure OpenAI endpoints, local vLLM servers
- Anthropic Claude - Alternative LLM for extraction
  - SDK/Client: `anthropic>=0.97.0`
  - Auth: `ANTHROPIC_API_KEY` env var
  - Implementation: `src/refchecker/llm/providers.py` (AnthropicProvider)
- Google Gemini - Alternative LLM for extraction
  - SDK/Client: `google-genai>=1.73.1`
  - Auth: `GOOGLE_API_KEY` env var
  - Implementation: `src/refchecker/llm/providers.py` (GoogleProvider)
  - Special: Custom retry logic in `src/refchecker/llm/google_retry.py`

**Academic APIs:**
- Semantic Scholar - Primary paper metadata and citation verification
  - Connection: Direct HTTPS API calls via `requests`
  - Client: Custom implementation in `src/refchecker/checkers/semantic_scholar.py`
  - Auth: `SEMANTIC_SCHOLAR_API_KEY` env var (optional, increases rate limits)
  - Rate limiting: 100 requests/5min (unauthenticated), 5000 requests/5min (authenticated)
- Crossref - DOI resolution and paper metadata
  - Endpoint: `https://api.crossref.org`
  - Client: `src/refchecker/checkers/crossref.py`
  - Auth: None (open API)
- OpenAlex - Alternative paper metadata source
  - Endpoint: `https://api.openalex.org`
  - Client: `src/refchecker/checkers/openalex.py`
  - Auth: None (open API, polite pool with email in User-Agent recommended)
- arXiv - Preprint metadata and full-text access
  - SDK/Client: `arxiv>=3.0.0`
  - Client: `src/refchecker/checkers/arxiv_citation.py`, `src/refchecker/utils/arxiv_utils.py`
  - Auth: None (open API)
  - Rate limiting: Custom limiter in `src/refchecker/utils/arxiv_rate_limiter.py`
- DBLP - Computer science bibliography
  - Endpoint: `https://dblp.org/search/publ/api`
  - Client: `src/refchecker/checkers/dblp.py`
  - Auth: None (open API)
- OpenReview - Conference review platform metadata
  - Client: `src/refchecker/checkers/openreview_checker.py`
  - Auth: None (open API)
- ACL Anthology - NLP/CL paper metadata
  - Client: `src/refchecker/checkers/acl_anthology.py`
  - Auth: None (open API)
- GitHub - Repository verification (for software citations)
  - Client: `src/refchecker/checkers/github_checker.py`
  - Auth: None (unauthenticated API calls)

**PDF Processing:**
- GROBID - PDF reference extraction service (fallback when no LLM configured)
  - Connection: `GROBID_URL` env var (defaults to `http://grobid:8070` in Docker Compose)
  - Client: Custom wrapper in `src/refchecker/utils/grobid.py`
  - Deployment: Docker container `lfoppiano/grobid:0.8.2` (orchestrated via `docker-compose.yml`)
  - Used by: `src/refchecker/core/refchecker.py`, `src/refchecker/core/bulk_pipeline.py`

## Data Storage

**Databases:**
- SQLite (via aiosqlite)
  - Connection: File-based, path set by `REFCHECKER_DATA_DIR` env var
  - Client: `aiosqlite>=0.22.1`
  - Schema: Managed in `backend/database.py`
  - Tables: `checks` (check history), `llm_configs` (saved LLM configurations), `users` (multi-user mode)
  - Location: `{REFCHECKER_DATA_DIR}/refchecker.db` (default: `backend/data/refchecker.db` or `/app/data/refchecker.db` in Docker)
  - Encryption: API keys encrypted with Fernet (`cryptography` library), key stored in `{REFCHECKER_DATA_DIR}/.secret.key`

**File Storage:**
- Local filesystem only
  - Uploaded PDFs: `backend/uploads/` or Docker volume mount
  - Thumbnails: `{REFCHECKER_DATA_DIR}/thumbnails/` (generated via `backend/thumbnail.py`)
  - Logs: `{REFCHECKER_DATA_DIR}/logs/` (usage tracking, check logs)
  - Cache: `{REFCHECKER_DATA_DIR}/llm_cache/` (optional LLM response caching)

**Caching:**
- LLM response caching - Optional filesystem cache for LLM extraction responses
  - Location: Configured per-check via `--cache` flag or WebUI setting
  - Implementation: `src/refchecker/utils/cache_utils.py`
- HTTP caching - None (direct API calls)

## Authentication & Identity

**Auth Provider:**
- Multi-user mode (optional, disabled by default)
  - Implementation: JWT tokens in HttpOnly cookies (`backend/auth.py`)
  - Token signing: `python-jose[cryptography]>=3.5.0`
  - Session duration: 7 days (configurable via `JWT_EXPIRE_SECONDS`)
  - Secret: `JWT_SECRET_KEY` env var (auto-generated if not set)

**OAuth Providers (multi-user mode only):**
- Google OAuth 2.0
  - Credentials: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` env vars
  - Redirect URI: `{SITE_URL}/api/auth/callback/google`
  - Endpoint: `https://accounts.google.com/o/oauth2/v2/auth`
  - Implementation: `backend/auth.py` (functions: `get_google_auth_url`, `exchange_google_code`)
- GitHub OAuth
  - Credentials: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` env vars
  - Redirect URI: `{SITE_URL}/api/auth/callback/github`
  - Endpoint: `https://github.com/login/oauth/authorize`
  - Implementation: `backend/auth.py` (functions: `get_github_auth_url`, `exchange_github_code`)
- Microsoft OAuth (Entra ID / Azure AD)
  - Credentials: `MS_CLIENT_ID`, `MS_CLIENT_SECRET` env vars
  - Redirect URI: `{SITE_URL}/api/auth/callback/microsoft`
  - Endpoint: `https://login.microsoftonline.com/common/oauth2/v2.0/authorize`
  - Implementation: `backend/auth.py` (functions: `get_microsoft_auth_url`, `exchange_microsoft_code`)

**Single-user mode (default):**
- No authentication required
- API keys stored in browser localStorage
- No OAuth, no user sessions

## Monitoring & Observability

**Error Tracking:**
- None (relies on application logging)

**Logs:**
- Python standard logging module
  - Level: INFO (configurable)
  - Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
  - Output: stderr/stdout (Docker logs)
- Usage tracking: Custom event log in `{REFCHECKER_DATA_DIR}/logs/usage.jsonl` (managed by `backend/usage_tracking.py`)

## CI/CD & Deployment

**Hosting:**
- Self-hosted (Docker deployment)
- Container registry: GitHub Container Registry (`ghcr.io/markrussinovich/refchecker`)

**CI Pipeline:**
- GitHub Actions (inferred from container registry, not visible in repo scan)

**Deployment methods:**
- Docker Compose (recommended): `docker-compose.yml`
- Direct Docker: `docker run` with `Dockerfile`
- Local Python: `python -m backend` or `run_webui.py`
- CLI-only: `python run_refchecker.py` (no web UI)

## Environment Configuration

**Required env vars (at least one LLM key):**
- `ANTHROPIC_API_KEY` - Anthropic Claude API key
- `OPENAI_API_KEY` - OpenAI API key
- `GOOGLE_API_KEY` - Google Gemini API key

**Optional env vars:**
- `SEMANTIC_SCHOLAR_API_KEY` - Higher rate limits for Semantic Scholar
- `HF_TOKEN` - HuggingFace token for gated models (vLLM)
- `REFCHECKER_DATA_DIR` - Data directory path
- `GROBID_URL` - GROBID service URL (fallback PDF extraction)

**Multi-user mode env vars (optional):**
- `REFCHECKER_MULTIUSER` - Enable multi-user mode (`true`/`false`)
- `JWT_SECRET_KEY` - Secret for JWT signing (auto-generated if not set)
- `SITE_URL` - Public URL for OAuth redirects
- `HTTPS_ONLY` - Mark cookies as Secure (`true`/`false`)
- `MAX_CHECKS_PER_USER` - Concurrent check limit per user (default: 3)
- `REFCHECKER_ADMINS` - Comma-separated admin identities
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_REDIRECT_URI`
- `MS_CLIENT_ID`, `MS_CLIENT_SECRET`, `MS_REDIRECT_URI`

**Secrets location:**
- Environment variables (`.env` file or system env)
- API keys encrypted in SQLite database (`backend/data/refchecker.db`)
- Secret key for encryption: `{REFCHECKER_DATA_DIR}/.secret.key` or `REFCHECKER_SECRET_KEY` env var

## Webhooks & Callbacks

**Incoming:**
- OAuth callbacks:
  - `GET /api/auth/callback/google` - Google OAuth callback (`backend/main.py:1028`)
  - `GET /api/auth/callback/github` - GitHub OAuth callback (`backend/main.py:1028`)
  - `GET /api/auth/callback/microsoft` - Microsoft OAuth callback (`backend/main.py:1028`)

**Outgoing:**
- None (no external webhook subscriptions)
- Internal callbacks: WebSocket progress events sent to frontend (`backend/websocket_manager.py`)

---

*Integration audit: 2026-05-27*
