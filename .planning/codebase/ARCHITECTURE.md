<!-- refreshed: 2026-05-27 -->
# Architecture

**Analysis Date:** 2026-05-27

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Three Execution Paths                                │
├──────────────────────┬──────────────────────┬─────────────────────────────┤
│   CLI Path           │   Bulk Path          │   WebUI Path                 │
│  run_refchecker.py   │  bulk_pipeline.py    │  run_webui.py               │
│  (single paper)      │  (batch processing)  │  (FastAPI + React)          │
└──────────┬───────────┴──────────┬───────────┴──────────┬──────────────────┘
           │                      │                       │
           └──────────────────────┼───────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Shared Core: ArxivReferenceChecker                        │
│              src/refchecker/core/refchecker.py (7944 lines)                  │
│  • Paper loading (ArXiv/PDF/LaTeX/URL)                                       │
│  • Bibliography extraction (regex/LLM/GROBID)                                │
│  • Reference verification orchestration                                      │
│  • Error classification & report generation                                  │
└──────────────────────────────────────────────────────────────────────────────┘
           │                      │                       │
           ▼                      ▼                       ▼
┌──────────────────┐  ┌────────────────────┐  ┌────────────────────────────┐
│ LLM Extraction   │  │ Hybrid Checker     │  │ Hallucination Policy       │
│ llm/base.py      │  │ checkers/          │  │ core/hallucination_policy  │
│ • Multi-provider │  │ enhanced_hybrid    │  │ • Pre-screening            │
│ • Chunking       │  │ • EnhancedHybrid   │  │ • LLM assessment           │
│ • Parsing        │  │   ReferenceChecker │  │ • Verdict application      │
└──────────────────┘  └────────────────────┘  └────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Verification Sources (Cascading)                        │
│  Local DBs → ArXiv API → Semantic Scholar → OpenAlex → CrossRef             │
│  (checkers/: local_semantic_scholar, arxiv_citation, semantic_scholar, etc.) │
└─────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Storage / Cache                                                             │
│  • SQLite DBs (Semantic Scholar, OpenAlex, CrossRef, DBLP)                   │
│  • LLM response cache (cache_utils.py)                                       │
│  • WebUI: database.py (check history + usage tracking)                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| ArxivReferenceChecker | Single-paper verification orchestration | `src/refchecker/core/refchecker.py` |
| ProgressRefChecker | WebUI wrapper with async progress callbacks | `backend/refchecker_wrapper.py` |
| BulkPipeline | Multi-paper batching, aggregation, cross-paper cache | `src/refchecker/core/bulk_pipeline.py` |
| EnhancedHybridReferenceChecker | Cascading verification across multiple APIs/DBs | `src/refchecker/checkers/enhanced_hybrid_checker.py` |
| LLMProvider / ReferenceExtractor | Multi-provider LLM bibliography extraction | `src/refchecker/llm/base.py`, `llm/providers.py` |
| HallucinationPolicy | LLM-based fabrication detection | `src/refchecker/core/hallucination_policy.py` |
| ParallelReferenceProcessor | Thread-pool-based parallel reference verification | `src/refchecker/core/parallel_processor.py` |
| ReportBuilder | Structured output generation (JSON/text reports) | `src/refchecker/core/report_builder.py` |
| FastAPI Backend | HTTP/WebSocket API for WebUI | `backend/main.py` |
| React Frontend | Interactive UI (Vite + Zustand + Tailwind) | `web-ui/src/` |

## Pattern Overview

**Overall:** Three-path architecture with shared core

**Key Characteristics:**
- Path parity: CLI, bulk, and WebUI must call identical verification logic
- All paths invoke `ArxivReferenceChecker` for single-paper checks
- Path-specific code limited to I/O, presentation, orchestration
- No duplication of checking/scoring/prompting logic across paths

## Layers

**Entry Points (Path-Specific Orchestration):**
- Purpose: Argument parsing, input handling, progress reporting, result formatting
- Locations:
  - CLI: `run_refchecker.py` → `src/refchecker/core/refchecker.py:main()`
  - Bulk: `src/refchecker/core/bulk_pipeline.py:process_paper_list()`
  - WebUI: `run_webui.py` → `backend/main.py` + `backend/refchecker_wrapper.py:ProgressRefChecker`
- Contains: CLI arg parsers, FastAPI routes, WebSocket handlers, progress formatters
- Depends on: Shared core (`ArxivReferenceChecker`)
- Used by: End users (CLI), batch scripts, web browser

**Shared Core (Business Logic):**
- Purpose: Paper processing, bibliography extraction, reference verification orchestration
- Location: `src/refchecker/core/refchecker.py`
- Contains: `ArxivReferenceChecker` class (7944 lines) — the canonical single-paper checker
- Depends on: Checkers, LLM modules, utils
- Used by: All three execution paths
- State Management: Instance-based (one checker per paper in CLI/bulk; reused in WebUI wrapper)

**Verification Checkers (Data Source Adapters):**
- Purpose: Adapt multiple external APIs/databases to unified verification interface
- Location: `src/refchecker/checkers/`
- Contains: 13 checker classes (one per source: ArXiv, Semantic Scholar, OpenAlex, CrossRef, DBLP, ACL, GitHub, OpenReview, etc.)
- Depends on: HTTP clients, local SQLite DBs, utils
- Used by: `EnhancedHybridReferenceChecker` (orchestrator)
- Pattern: Each checker implements `verify_reference(reference) -> (verified_data, errors, url)`

**LLM Providers (External AI Integration):**
- Purpose: LLM-based bibliography extraction and hallucination detection
- Location: `src/refchecker/llm/`
- Contains: Provider adapters (OpenAI, Anthropic, Google, Azure, vLLM), prompt templates, chunking logic
- Depends on: Provider SDKs (openai, anthropic, google-genai)
- Used by: `ArxivReferenceChecker` (for extraction), `HallucinationPolicy` (for assessment)

**Utilities (Cross-Cutting Concerns):**
- Purpose: Text processing, URL handling, caching, database config
- Location: `src/refchecker/utils/`
- Contains: 19 utility modules (text_utils, url_utils, cache_utils, database_config, etc.)
- Depends on: Standard library, third-party libs (requests, pypdf, fuzzywuzzy)
- Used by: All layers

**Backend API (WebUI Server):**
- Purpose: HTTP/WebSocket API for web frontend
- Location: `backend/`
- Contains: FastAPI app, auth, WebSocket manager, thumbnail generation, usage tracking
- Depends on: Shared core, database (aiosqlite)
- Used by: React frontend (`web-ui/`)

**Frontend (WebUI Client):**
- Purpose: Interactive UI for reference checking
- Location: `web-ui/src/`
- Contains: React components, Zustand stores, API client
- Depends on: Backend API
- Used by: End users (browser)

## Data Flow

### Primary Request Path (CLI)

1. **Entry:** `run_refchecker.py` → `refchecker.core.refchecker:main()` (`src/refchecker/core/refchecker.py:7668`)
2. **Parse input:** `resolve_input_spec()` → ArXiv ID, PDF path, or URL (`refchecker.py:180`)
3. **Load paper:** `get_arxiv_paper_by_id()` or `_create_local_paper_object()` (`refchecker.py:6972, 7037`)
4. **Extract bibliography:**
   - Try regex extraction first (`_extract_bibliography_from_text()`, `refchecker.py:2127`)
   - Fallback to LLM extraction (`_extract_references_llm()`, `refchecker.py:2473`)
   - Last resort: GROBID (`extract_pdf_references_with_grobid_fallback()`, utils)
5. **Verify references:** Loop over bibliography
   - Parallel: `ParallelReferenceProcessor.verify_references_parallel()` (`core/parallel_processor.py:86`)
   - Sequential: `verify_reference()` → `verify_reference_standard()` (`refchecker.py:3209, 3566`)
   - Per reference: `EnhancedHybridReferenceChecker.verify_reference()` → cascade through checkers
6. **Assess hallucination:** `run_hallucination_check()` → `LLMHallucinationVerifier` (`core/hallucination_policy.py`)
7. **Generate report:** `ReportBuilder.build_report()` → JSON/text output (`core/report_builder.py`)

### WebUI Path

1. **HTTP POST `/api/check`:** User submits paper (`backend/main.py:1278`)
2. **Create WebSocket:** Client connects to `/ws/{check_id}` (`backend/main.py:650`)
3. **Queue check:** Concurrency limiter queues request (`backend/concurrency.py`)
4. **Execute:** `ProgressRefChecker.check_paper()` (`backend/refchecker_wrapper.py:564`)
   - Calls same extraction/verification methods as CLI
   - Sends progress events via WebSocket callback
5. **Store results:** Write to SQLite (`backend/database.py:create_check()`)
6. **Frontend update:** Zustand stores update (`web-ui/src/stores/useCheckStore.js`)

### Bulk Path

1. **Entry:** `bulk_pipeline.process_paper_list()` (`src/refchecker/core/bulk_pipeline.py:1174`)
2. **Load paper specs:** Parse file with ArXiv IDs or URLs
3. **Thread pool:** Execute papers concurrently (`ThreadPoolExecutor`)
4. **Per paper:** Call `ArxivReferenceChecker` (same as CLI)
5. **Cross-paper cache:** `BulkVerificationCache` deduplicates reference checks (`bulk_pipeline.py:91`)
6. **Aggregate:** Collect errors/warnings across all papers
7. **Checkpoint:** Periodic state saves for resume capability (`bulk_pipeline.py:809`)

**State Management:**
- CLI/Bulk: Instance per paper, no shared state between papers (except bulk cache)
- WebUI: Per-check state stored in SQLite, in-memory active check tracking (`backend/database.py`)
- LLM cache: Disk-based (keyed by prompt hash) — shared across all paths (`utils/cache_utils.py`)

## Key Abstractions

**ArxivReferenceChecker:**
- Purpose: Single-paper verification coordinator
- Examples: `src/refchecker/core/refchecker.py:274`
- Pattern: Stateful class encapsulating entire verification pipeline for one paper
- Methods: `check_paper()`, `verify_reference()`, `extract_references()`, `_extract_bibliography_from_text()`

**EnhancedHybridReferenceChecker:**
- Purpose: Multi-source verification with cascading fallback
- Examples: `src/refchecker/checkers/enhanced_hybrid_checker.py:41`
- Pattern: Strategy pattern — tries local DBs first, then APIs in priority order
- Methods: `verify_reference()`, `_verify_with_local_dbs()`, `_verify_with_apis()`

**LLMProvider:**
- Purpose: Abstract LLM interface for multi-provider support
- Examples: `src/refchecker/llm/base.py:15` (base class), `llm/providers.py` (implementations)
- Pattern: Abstract base class with provider-specific subclasses (OpenAIProvider, AnthropicProvider, etc.)
- Methods: `extract_references(bibliography_text)`, `_call_llm(prompt)`, `_chunk_bibliography()`

**ReferenceExtractor:**
- Purpose: High-level extraction orchestrator (wraps LLMProvider)
- Examples: `src/refchecker/llm/base.py:318`
- Pattern: Facade — handles chunking, parallel processing, result aggregation
- Methods: `extract_references_from_bibliography()`, `extract_references_from_chunks_parallel()`

**BulkVerificationCache:**
- Purpose: Cross-paper reference deduplication
- Examples: `src/refchecker/core/bulk_pipeline.py:91`
- Pattern: Thread-safe in-memory cache keyed by (title, first_author_last, year)
- Methods: `get(reference)`, `put(reference, result)`

## Entry Points

**CLI Entry Point:**
- Location: `run_refchecker.py` → `refchecker.core.refchecker:main()`
- Triggers: User invokes `python run_refchecker.py --paper SPEC` or `academic-refchecker --paper SPEC`
- Responsibilities:
  - Parse CLI args (`argparse`)
  - Initialize `ArxivReferenceChecker` with config
  - Call `check_paper(paper_id)` or `check_paper_from_local_pdf(path)`
  - Print results to stdout/file

**WebUI Backend Entry Point:**
- Location: `run_webui.py` → `backend.main:app` (FastAPI)
- Triggers: HTTP request to `/api/check` or WebSocket connection to `/ws/{check_id}`
- Responsibilities:
  - Accept paper uploads or URLs
  - Spawn `ProgressRefChecker.check_paper()` in background
  - Stream progress via WebSocket
  - Store results in SQLite

**Bulk Pipeline Entry Point:**
- Location: `src/refchecker/core/bulk_pipeline.py:process_paper_list()`
- Triggers: Called by external scripts (e.g., `_workspace/openreview.sh` or custom batch scripts)
- Responsibilities:
  - Load paper list from file
  - Execute papers concurrently with thread pool
  - Aggregate results across papers
  - Save checkpoint for resume

**Package Entry Points (pyproject.toml):**
- `academic-refchecker` → `refchecker.core.refchecker:main` (CLI)
- `refchecker-webui` → `backend.cli:main` (WebUI launcher)

## Architectural Constraints

- **Threading:** Python threading model — ThreadPoolExecutor used for parallel reference checks (configurable max_workers, default 6). WebUI uses asyncio event loop with ThreadPoolExecutor for blocking operations.
- **Global state:** Minimal — logger instances are module-level singletons. Cache directory and DB paths are resolved at initialization. No mutable global state shared across papers.
- **Circular imports:** Avoided via deferred imports (e.g., `from refchecker.core.hallucination_policy import ...` inside methods, not at module level)
- **Path parity requirement:** All three paths MUST call the same core verification methods. Any behavior change must be applied to all paths or documented as path-specific. See `AGENTS.md` for enforcement policy.
- **Database concurrency:** Local SQLite DBs are read-only from checker perspective. WebUI's check history DB uses `aiosqlite` for async writes with connection pooling.
- **LLM non-determinism:** Same inputs may produce different outputs across runs due to sampling. Determinism is not guaranteed unless temperature=0 and fixed seed (provider-dependent).

## Anti-Patterns

### Path-Specific Verification Logic

**What happens:** Duplicating reference checking, error classification, or scoring logic in `backend/refchecker_wrapper.py` or `bulk_pipeline.py` instead of using the shared core.
**Why it's wrong:** Breaks path parity — CLI and WebUI produce different results for the same paper. Creates maintenance burden (fixes must be applied 3x).
**Do this instead:** Put logic in `src/refchecker/core/refchecker.py:ArxivReferenceChecker` or a shared utility module. Path-specific code should only handle I/O, progress reporting, and presentation.

### Direct Checker Instantiation in Business Logic

**What happens:** Creating checker instances (e.g., `SemanticScholarChecker()`) directly inside `ArxivReferenceChecker` methods instead of using `EnhancedHybridReferenceChecker`.
**Why it's wrong:** Bypasses the cascading fallback logic. Fragile to API failures (no automatic retry with alternate source).
**Do this instead:** Always route through `EnhancedHybridReferenceChecker.verify_reference()` (`src/refchecker/checkers/enhanced_hybrid_checker.py:270`). It handles source selection, retries, and error aggregation.

### Ignoring Cache Keys

**What happens:** Calling LLM providers without going through `cache_utils.py` caching layer.
**Why it's wrong:** Wastes API quota and increases latency. LLM extraction can cost $0.01-0.10 per paper.
**Do this instead:** Use `cached_bibliography()` and `cache_bibliography()` wrappers (`src/refchecker/utils/cache_utils.py:98`). They hash prompts and store responses on disk.

## Error Handling

**Strategy:** Layered error handling with graceful degradation

**Patterns:**
- **API failures:** Caught by individual checkers, logged as warnings. Checker returns `(None, [{"type": "api_error", "message": "..."}], None)`. Hybrid checker proceeds to next source.
- **LLM extraction failures:** Fall back to regex extraction, then GROBID. Track extraction method in `last_bibliography_extraction_method` field.
- **Paper download failures:** Return early with `fatal_error = True` and descriptive `fatal_error_message`. No verification attempted.
- **Invalid references:** Logged as warnings, skipped from verification. Not counted as errors.
- **Threading errors:** Caught by `ParallelReferenceProcessor`, logged with traceback. Failed references marked with "processing_error" type.

## Cross-Cutting Concerns

**Logging:**
- Strategy: Python `logging` module with per-module loggers
- Configuration: `setup_logging(debug_mode)` in `refchecker.py:123`
- Levels: DEBUG (file only), INFO (console), WARNING/ERROR (always)
- Suppression: ArXiv client, HTTP libs (httpx/httpcore) suppressed to WARNING unless debug mode

**Validation:**
- Input validation: `ConfigValidator` class (`utils/config_validator.py`)
- URL validation: `validate_remote_fetch_url()` in `utils/url_utils.py`
- Reference field validation: Implicit via normalization functions in `text_utils.py`

**Authentication (WebUI only):**
- Strategy: Optional OAuth2 (Google/GitHub/Microsoft) + JWT tokens
- Implementation: `backend/auth.py` — multiuser mode enabled via env vars
- Token storage: HTTP-only secure cookies
- Single-user mode: No auth required (default)

**Caching:**
- LLM responses: Disk cache keyed by prompt hash (`utils/cache_utils.py`)
- Bulk cross-paper: In-memory cache (`BulkVerificationCache`)
- WebUI check history: SQLite (`backend/database.py`)

**Rate Limiting:**
- ArXiv API: 3-second delay between requests (`arxiv.Client(delay_seconds=3)`)
- Semantic Scholar: Exponential backoff on 429 errors (`checkers/semantic_scholar.py`)
- WebUI concurrent checks: Configurable limiter (`backend/concurrency.py`)

---

*Architecture analysis: 2026-05-27*
