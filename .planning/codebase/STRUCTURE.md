# Codebase Structure

**Analysis Date:** 2026-05-27

## Directory Layout

```
refchecker/
├── src/refchecker/            # Core Python package
│   ├── core/                  # Verification pipeline & orchestration
│   ├── checkers/              # API/DB adapters (13 sources)
│   ├── llm/                   # LLM providers & extraction
│   ├── utils/                 # Text processing, caching, config
│   ├── services/              # PDF processing
│   ├── database/              # DB downloaders & updaters
│   ├── config/                # Settings & provider config
│   └── scripts/               # Utility scripts (vLLM server, etc.)
├── backend/                   # FastAPI WebUI server
│   ├── main.py                # HTTP/WebSocket routes
│   ├── refchecker_wrapper.py # Progress-aware wrapper
│   ├── database.py            # Check history storage
│   ├── auth.py                # OAuth2/JWT auth
│   └── static/                # Served frontend build
├── web-ui/                    # React frontend (Vite)
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── stores/            # Zustand state management
│   │   └── utils/             # API client, helpers
│   └── public/                # Static assets
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   ├── e2e/                   # End-to-end tests
│   └── fixtures/              # Test data
├── scripts/                   # Development/build scripts
├── tauri-app/                 # Desktop app (Tauri wrapper)
├── docs/                      # Documentation
├── paper/                     # Research paper source
├── run_refchecker.py          # CLI entry point
├── run_webui.py               # WebUI launcher
├── run_webui_check.py         # WebUI path test harness
├── pyproject.toml             # Python package config
└── requirements*.txt          # Dependency specs
```

## Directory Purposes

**`src/refchecker/`:**
- Purpose: Core Python package — all verification logic lives here
- Contains: 7 subdirectories with 50+ modules
- Key files:
  - `__init__.py`: Package root
  - `__version__.py`: Version string
  - `__main__.py`: Module entry point (`python -m refchecker`)

**`src/refchecker/core/`:**
- Purpose: Pipeline orchestration and single-paper verification
- Contains: Main checker class, bulk processing, parallel execution, hallucination policy, report generation
- Key files:
  - `refchecker.py`: `ArxivReferenceChecker` class (7944 lines) — the canonical single-paper checker
  - `bulk_pipeline.py`: Multi-paper batch processing (1625 lines)
  - `parallel_processor.py`: Thread-pool-based parallel verification (460 lines)
  - `hallucination_policy.py`: LLM-based fabrication detection (2028 lines)
  - `report_builder.py`: JSON/text report generation (17348 lines)
  - `db_connection_pool.py`: Thread-safe DB connection management

**`src/refchecker/checkers/`:**
- Purpose: External API and database adapters
- Contains: 13 checker classes — one per source (ArXiv, Semantic Scholar, OpenAlex, CrossRef, DBLP, ACL Anthology, GitHub, OpenReview, DBLP, webpage, PDF, web search)
- Key files:
  - `enhanced_hybrid_checker.py`: Cascading multi-source checker (1598 lines)
  - `local_semantic_scholar.py`: Local SQLite DB checker
  - `semantic_scholar.py`: Semantic Scholar API client
  - `arxiv_citation.py`: ArXiv metadata verifier
  - `openalex.py`: OpenAlex API client
  - `crossref.py`: CrossRef API client

**`src/refchecker/llm/`:**
- Purpose: LLM-based extraction and hallucination verification
- Contains: Multi-provider abstraction, prompt templates, chunking logic
- Key files:
  - `base.py`: `LLMProvider` ABC, `ReferenceExtractor` (526 lines)
  - `providers.py`: Provider implementations (OpenAI, Anthropic, Google, Azure, vLLM)
  - `hallucination_verifier.py`: LLM hallucination assessment
  - `google_retry.py`: Google Gemini retry logic with quota handling

**`src/refchecker/utils/`:**
- Purpose: Shared utilities for text processing, caching, URL handling, config
- Contains: 19 utility modules
- Key files:
  - `text_utils.py`: Bibliography parsing, text normalization, similarity scoring
  - `url_utils.py`: ArXiv ID extraction, URL validation, PDF downloading
  - `cache_utils.py`: LLM response caching, artifact storage
  - `database_config.py`: DB path resolution, update order
  - `arxiv_utils.py`: ArXiv API helpers
  - `grobid.py`: GROBID PDF extraction fallback

**`src/refchecker/services/`:**
- Purpose: High-level services
- Contains: `pdf_processor.py` (PDF text extraction)

**`src/refchecker/database/`:**
- Purpose: Local database management
- Contains: Semantic Scholar DB downloader, update scripts
- Key files:
  - `download_semantic_scholar_db.py`: DB download utility
  - `local_database_updater.py`: Incremental DB update logic

**`backend/`:**
- Purpose: FastAPI web server for WebUI
- Contains: 12 modules (4195 lines in main.py alone)
- Key files:
  - `main.py`: FastAPI app, HTTP routes, WebSocket handlers (4195 lines)
  - `refchecker_wrapper.py`: `ProgressRefChecker` — async wrapper with progress callbacks (2076 lines)
  - `database.py`: SQLite check history, usage tracking (75555 lines)
  - `auth.py`: OAuth2/JWT authentication (18643 lines)
  - `websocket_manager.py`: WebSocket connection management (6059 lines)
  - `concurrency.py`: Request rate limiting (3428 lines)
  - `thumbnail.py`: Paper thumbnail generation (24225 lines)
  - `usage_tracking.py`: Analytics and metrics (18204 lines)
  - `cli.py`: WebUI CLI launcher (3542 lines)
  - `models.py`: Pydantic models (2591 lines)

**`web-ui/`:**
- Purpose: React-based web frontend
- Contains: Vite project with React 19, Zustand state management, Tailwind CSS
- Key files:
  - `src/App.jsx`: Root component (163 lines)
  - `src/main.jsx`: React entry point
  - `src/components/`: UI components (30+ files)
  - `src/stores/`: Zustand stores (useCheckStore, useHistoryStore, useAuthStore)
  - `src/utils/api.js`: Backend API client
  - `package.json`: NPM dependencies (React 19, Vite 8, Zustand 5, Tailwind 4)

**`tests/`:**
- Purpose: Test suite (pytest + Playwright)
- Contains: unit/, integration/, e2e/, fixtures/
- Key files:
  - `unit/`: Python unit tests
  - `integration/`: API integration tests
  - `e2e/`: Playwright browser tests (web-ui/e2e/)
  - `fixtures/`: Test data (PDFs, bibliography samples)

**`scripts/`:**
- Purpose: Development utilities
- Contains:
  - `download_db.py`: Database download script
  - `update_local_database.py`: DB update automation
  - `generate_assessment_graphs.py`: Visualization scripts
  - `start_vllm_server.py`: vLLM server launcher

**`tauri-app/`:**
- Purpose: Desktop application (Electron alternative)
- Contains: Tauri wrapper around web-ui + Python backend
- Key files:
  - `src-tauri/`: Rust Tauri backend
  - `frontend/`: Symlink/copy of web-ui
  - `python/`: Bundled Python runtime + refchecker

## Key File Locations

**Entry Points:**
- `run_refchecker.py`: CLI entry point (27 lines) — imports and runs `refchecker.core.refchecker:main`
- `run_webui.py`: WebUI launcher (68 lines) — starts uvicorn with `backend.main:app`
- `run_webui_check.py`: WebUI path test harness (89 lines) — drives `ProgressRefChecker` directly for comparison testing
- `src/refchecker/__main__.py`: Module entry point for `python -m refchecker`
- `backend/__main__.py`: Module entry point for `python -m backend`

**Configuration:**
- `pyproject.toml`: Python package metadata, dependencies, entry points (105 lines)
- `requirements.txt`: Core dependencies (1055 lines)
- `requirements-dev.txt`: Dev dependencies (pytest, black, mypy)
- `requirements-docker.txt`: Docker-specific deps
- `.env.example`: Example environment variables
- `src/refchecker/config/settings.py`: Runtime config resolver

**Core Logic:**
- `src/refchecker/core/refchecker.py`: Main verification pipeline (7944 lines) — most important file
- `src/refchecker/checkers/enhanced_hybrid_checker.py`: Multi-source checker (1598 lines)
- `src/refchecker/core/hallucination_policy.py`: Hallucination detection (2028 lines)
- `backend/refchecker_wrapper.py`: WebUI async wrapper (2076 lines)

**Testing:**
- `pytest.ini`: Pytest configuration
- `tests/unit/`: Unit tests
- `tests/integration/`: Integration tests
- `web-ui/playwright.config.js`: E2E test config
- `web-ui/e2e/`: Playwright tests

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` (e.g., `enhanced_hybrid_checker.py`, `text_utils.py`)
- React components: `PascalCase.jsx` (e.g., `MainPanel.jsx`, `StatsSection.jsx`)
- Test files: `test_*.py` or `*.test.jsx` (e.g., `test_bulk_pipeline.py`, `StatsSection.test.jsx`)
- Config files: Lowercase with hyphens or dots (e.g., `pyproject.toml`, `pytest.ini`, `playwright.config.js`)

**Functions:**
- Python: `snake_case` (e.g., `verify_reference()`, `extract_arxiv_id_from_url()`)
- JavaScript: `camelCase` (e.g., `fetchHistory()`, `getCheckDetail()`)
- Private Python: Leading underscore `_snake_case` (e.g., `_extract_bibliography_from_text()`)

**Variables:**
- Python: `snake_case` (e.g., `source_paper`, `verified_data`, `llm_extractor`)
- JavaScript: `camelCase` (e.g., `selectedCheckId`, `isLoading`, `statusMessage`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_WORKERS`, `DATABASE_LABELS`, `API_TIMEOUT`)

**Classes:**
- Python: `PascalCase` (e.g., `ArxivReferenceChecker`, `EnhancedHybridReferenceChecker`, `LLMProvider`)
- React components: `PascalCase` (e.g., `Sidebar`, `MainPanel`, `ReferenceList`)

**Directories:**
- Lowercase with hyphens for multi-word (e.g., `web-ui`, `tauri-app`)
- Lowercase single word for Python packages (e.g., `refchecker`, `backend`, `checkers`)

## Where to Add New Code

**New Verification Source (e.g., new API):**
- Primary code: `src/refchecker/checkers/new_source_checker.py`
- Integration: Add to `EnhancedHybridReferenceChecker.__init__()` in `src/refchecker/checkers/enhanced_hybrid_checker.py`
- Tests: `tests/unit/test_new_source_checker.py`

**New LLM Provider:**
- Implementation: Add class to `src/refchecker/llm/providers.py`
- Factory: Update `create_llm_provider()` in `src/refchecker/llm/base.py`
- Config: Add env var mappings to `src/refchecker/config/settings.py`
- Tests: `tests/unit/test_llm_providers.py`

**New CLI Option:**
- Argument parser: Add to `main()` function in `src/refchecker/core/refchecker.py` (around line 7668)
- Pass to checker: Update `ArxivReferenceChecker.__init__()` signature (line 275)
- Documentation: Update README.md and module docstring

**New WebUI Feature:**
- Backend route: Add endpoint to `backend/main.py`
- Frontend component: Add to `web-ui/src/components/` (organize by feature: MainPanel/, Sidebar/, Auth/, etc.)
- State management: Update or create Zustand store in `web-ui/src/stores/`
- API client: Add method to `web-ui/src/utils/api.js`

**New Utility Function:**
- Text processing: `src/refchecker/utils/text_utils.py`
- URL handling: `src/refchecker/utils/url_utils.py`
- Caching: `src/refchecker/utils/cache_utils.py`
- Database config: `src/refchecker/utils/database_config.py`

**New Test:**
- Unit test: `tests/unit/test_<module>.py`
- Integration test: `tests/integration/test_<feature>.py`
- E2E test (WebUI): `web-ui/e2e/<feature>.spec.js`
- Fixtures: `tests/fixtures/<data_type>/`

## Special Directories

**`backend/static/`:**
- Purpose: Served frontend build artifacts (production)
- Generated: Yes (via `npm run build` in web-ui/)
- Committed: Partial (empty structure committed, assets generated at build time)
- Location: `backend/static/` and `backend/static/assets/`

**`src/refchecker/__pycache__/`:**
- Purpose: Python bytecode cache
- Generated: Yes (automatically by Python)
- Committed: No (.gitignore excludes __pycache__)

**`web-ui/node_modules/`:**
- Purpose: NPM dependencies
- Generated: Yes (via `npm install`)
- Committed: No (.gitignore excludes node_modules/)

**`.opencode/`:**
- Purpose: OpenCode agent configuration and hooks
- Generated: No (manually configured)
- Committed: Yes
- Contains: GSD hooks, agent configs, skill definitions

**`.planning/`:**
- Purpose: GSD codebase documentation
- Generated: Yes (by `/gsd-map-codebase` command)
- Committed: Yes
- Contains: ARCHITECTURE.md, STRUCTURE.md, STACK.md, etc.

**`tests/fixtures/test_cache/`:**
- Purpose: Test-specific LLM response cache
- Generated: Yes (by tests)
- Committed: Partial (structure committed, cache files excluded)

**`.venv/`:**
- Purpose: Python virtual environment
- Generated: Yes (via `python -m venv .venv`)
- Committed: No (.gitignore excludes .venv/)

**`logs/`:**
- Purpose: Debug logs (when `--debug` flag is used)
- Generated: Yes (by `setup_logging()` in debug mode)
- Committed: No (.gitignore excludes logs/)

**`output/`:**
- Purpose: Verification output files (when `--output-file` is specified)
- Generated: Yes (by `ReportBuilder`)
- Committed: No (.gitignore excludes output/)

---

*Structure analysis: 2026-05-27*
