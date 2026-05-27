# Codebase Concerns

**Analysis Date:** 2026-05-27

## Tech Debt

**Legacy test setup pattern in enhanced hybrid checker:**
- Issue: `_iter_local_db_checkers()` contains a fallback to `self.local_db` for backward compatibility with older tests
- Files: `src/refchecker/checkers/enhanced_hybrid_checker.py:277-283`
- Impact: Dual initialization paths make the checker harder to maintain and test reliably
- Fix approach: Migrate all dependent tests to use `local_db_checkers` parameter, then remove the `self.local_db` fallback

**Complex author parsing scenarios not fully handled:**
- Issue: BibTeX format parsing for complex author lists (e.g., Vivit paper with "12 cited vs 6 correct", Safaei paper with "8 cited vs 4 correct") remains incomplete
- Files: `tests/unit/test_bibtex_cleaning.py:235-246` (commented-out test cases)
- Impact: Potential false positives on author mismatch errors for papers with complex author formatting
- Fix approach: Enhance BibTeX parser to handle edge cases in author field parsing, particularly with special formatting and multiple authors

**Legacy markup normalization in local database:**
- Issue: Multiple title normalization strategies required to handle historical database entries with different normalization schemes (DB-style, legacy HTML markup normalization)
- Files: `src/refchecker/checkers/local_semantic_scholar.py:69-71`, `src/refchecker/checkers/local_semantic_scholar.py:423-459`
- Impact: Query performance degradation due to fallback lookups; maintenance burden of multiple normalization code paths
- Fix approach: Regenerate local databases with consistent normalization, then remove legacy normalization fallbacks

**Deprecated parameters in core interfaces:**
- Issue: Several functions maintain deprecated parameters for backward compatibility (e.g., `normalize_func` in text utils, legacy single-error format in bulk pipeline)
- Files: `src/refchecker/core/report_builder.py:30`, `src/refchecker/core/refchecker.py:279`, `src/refchecker/utils/text_utils.py:2488`
- Impact: API surface bloat; confusion about which parameters to use
- Fix approach: Mark with deprecation warnings, add removal timeline in documentation, then remove in next major version

**Debug logging to temp file in production:**
- Issue: Backend wrapper writes debug logs to temp directory unconditionally, not controlled by log level configuration
- Files: `backend/refchecker_wrapper.py:18-22`
- Impact: Disk I/O overhead; potential disk space exhaustion on long-running instances; security risk if debug logs contain sensitive data
- Fix approach: Guard debug logging with configuration flag; implement log rotation; ensure sensitive data is never logged

**Path parity violations across execution paths:**
- Issue: Three execution paths (bulk, CLI, WebUI) are supposed to use identical checking logic, but wrapper code contains path-specific preprocessing (e.g., `backend/refchecker_wrapper.py` has custom reference extraction and hallucination assessment not in core)
- Files: `backend/refchecker_wrapper.py:62-86`, `backend/refchecker_wrapper.py:1213-1276`
- Impact: Results may differ between CLI and WebUI for the same paper; fixes applied to one path may not propagate
- Fix approach: Per AGENTS.md guidance, move all checking logic to shared core (`src/refchecker/`); keep wrapper limited to I/O and progress callbacks

## Known Bugs

**Empty return stubs in error paths:**
- Issue: Over 30 occurrences of `return []` or `return {}` in exception handlers, potentially swallowing important error context
- Files: `src/refchecker/llm/base.py:477,497,503`, `src/refchecker/checkers/local_semantic_scholar.py:72`, `src/refchecker/checkers/openreview_checker.py:338,1031,1122` (and 20+ more locations)
- Impact: Silent failures make debugging difficult; user may not know verification failed
- Fix approach: Log errors before returning empty values; consider returning error dictionaries instead of empty collections

**Bare exception handlers:**
- Issue: Broad `except Exception` clauses (361+ try blocks, many with catch-all handlers) mask specific error types
- Files: `src/refchecker/llm/base.py:377,404,444`, `src/refchecker/llm/providers.py:434,501,550`, `src/refchecker/llm/providers.py:789` (bare `except:`), and many more
- Impact: Unexpected exceptions (e.g., KeyboardInterrupt, SystemExit) may be caught unintentionally; harder to diagnose root causes
- Fix approach: Replace with specific exception types where possible; use `except Exception` only when truly needed and log full traceback

**WebSocket message buffer unbounded growth risk:**
- Issue: Pending message buffer caps at 500 messages per session, but session cleanup only happens on eviction check (5-minute timeout)
- Files: `backend/websocket_manager.py:24,76-84`
- Impact: If many sessions start checks but never connect WebSocket, memory usage grows until timeout
- Fix approach: Add periodic cleanup task; implement maximum total buffer size across all sessions

## Security Considerations

**Subprocess shell invocation patterns:**
- Issue: Multiple subprocess calls to `pkill` and vLLM server commands; while no `shell=True` found, command construction should be validated
- Files: `src/refchecker/llm/providers.py:701,786,794-830`, `src/refchecker/scripts/start_vllm_server.py:19`
- Current mitigation: Commands use list form (not shell strings); no user input in command construction
- Recommendations: Document that vLLM server management is trusted code path only; ensure model names are validated before being passed to subprocess

**API keys in client-side localStorage (WebUI multi-user mode):**
- Issue: User-provided API keys stored in browser localStorage and sent with each request
- Files: `web-ui/src/stores/useKeyStore.test.js`, backend API endpoints accepting `api_key` parameters
- Current mitigation: Keys never persisted on server in multi-user mode; HttpOnly cookies for session auth
- Recommendations: Document security model clearly; consider warning users that keys are accessible to browser extensions; implement key encryption at rest in localStorage

**OAuth state token storage in memory:**
- Issue: CSRF state tokens stored in module-level dict without cleanup mechanism for expired states
- Files: `backend/auth.py:82-89`
- Current mitigation: State tokens are short-lived (used once during OAuth flow)
- Recommendations: Add expiration timestamp check; implement periodic cleanup of stale states; add maximum size limit to prevent memory exhaustion

**JWT secret key generation:**
- Issue: If `JWT_SECRET_KEY` env var not set, falls back to `secrets.token_hex(32)` which generates a new key on each server restart (invalidating all sessions)
- Files: `backend/auth.py:39`
- Current mitigation: Documentation requires setting in production
- Recommendations: Fail loudly if JWT_SECRET_KEY not set in multi-user mode; add startup validation check

**Database encryption key management:**
- Issue: Secret key for encrypting LLM API keys in database is auto-generated and stored in data directory if not provided via env var
- Files: `backend/database.py:39-52`
- Current mitigation: File permissions set to 0600 on Unix; key persists across restarts
- Recommendations: Document key backup requirements; implement key rotation mechanism; add warning if using auto-generated key in production

## Performance Bottlenecks

**SQLite normalized title lookups with multiple fallbacks:**
- Issue: Local database queries try up to 4 different normalization strategies sequentially (normalized, DB-style, legacy markup variants) if initial lookup fails
- Files: `src/refchecker/checkers/local_semantic_scholar.py:403-463`
- Cause: Historical database inconsistencies require multiple query patterns
- Improvement path: Pre-normalize database on load; add compound index on all normalization variants; profile query times and optimize most common case

**Main refchecker.py file size (7944 lines):**
- Problem: Single file contains entry point, reference extraction, verification orchestration, CLI parsing, and multiple helper functions
- Files: `src/refchecker/core/refchecker.py`
- Cause: Organic growth without refactoring
- Scaling path: Extract reference extraction to dedicated module; split ArXiv and non-ArXiv verification into separate classes; move CLI parsing to separate file

**Synchronous arXiv rate limiting:**
- Problem: Global 3-second rate limit enforced via semaphore blocks all arXiv API calls, even when using parallel processing
- Files: `src/refchecker/checkers/arxiv_citation.py:78,210`, `src/refchecker/checkers/enhanced_hybrid_checker.py:205`
- Cause: ArXiv API rate limit requirement
- Improvement path: Pre-fetch arXiv metadata for all references in batch before starting verification; use bulk API endpoints where available

**Backend main.py file size (4195 lines):**
- Problem: Single file contains all API endpoints, WebSocket handling, OAuth flows, settings management, and database operations
- Files: `backend/main.py`
- Cause: FastAPI encourages single-file applications for small projects; grew organically
- Scaling path: Split into routers (auth, checks, settings, history, admin); extract OAuth flows to separate module; create service layer for business logic

**ThreadPoolExecutor usage without backpressure:**
- Problem: Multiple ThreadPoolExecutor instances created without coordination; potential for thread exhaustion when processing large bibliographies
- Files: `src/refchecker/llm/base.py:385` (max 4 workers), `src/refchecker/checkers/enhanced_hybrid_checker.py:623` (max 2 workers), `src/refchecker/core/parallel_processor.py:130` (max 6 workers)
- Cause: Each component manages its own thread pool
- Improvement path: Implement global thread pool budget; add queue-based backpressure; monitor and log active thread count

## Fragile Areas

**LLM provider initialization with subprocess management:**
- Files: `src/refchecker/llm/providers.py:775-869`
- Why fragile: Spawns vLLM server process with complex environment cleanup, timeouts, and signal handling; process lifetime tied to Python process
- Safe modification: Never modify subprocess launch code without testing on target GPU hardware; ensure cleanup handlers run even on exceptions
- Test coverage: Integration tests skip vLLM scenarios (require GPU); unit tests mock subprocess calls

**Hallucination policy assessment chain:**
- Files: `src/refchecker/core/hallucination_policy.py` (2028 lines), `src/refchecker/llm/hallucination_verifier.py` (1381 lines)
- Why fragile: Complex decision tree with multiple screening phases, LLM fallback logic, and verdict precedence rules; changes to one phase affect downstream phases
- Safe modification: Always run full hallucination test suite; verify precedence rules in `AGENTS.md` still apply; check that stats aggregation remains consistent
- Test coverage: 91 test files total; hallucination-specific tests in `tests/unit/test_hallucination_*.py` and `tests/integration/test_live_hallucination_*.py`

**WebSocket manager buffering and replay logic:**
- Files: `backend/websocket_manager.py:28-46`
- Why fragile: Early messages buffered before WebSocket connects, then replayed; timing-dependent behavior; buffer eviction logic runs inline
- Safe modification: Test both cases (WebSocket connects before first message, WebSocket connects after multiple messages); verify stale buffer eviction doesn't drop active session messages
- Test coverage: No dedicated WebSocket manager tests; covered by integration tests

**Parallel reference processor ordered output:**
- Files: `src/refchecker/core/parallel_processor.py`
- Why fragile: Worker threads complete in arbitrary order but results must print in original order; uses result buffer and sentinel values to coordinate shutdown
- Safe modification: Never modify worker loop or sentinel handling without testing with 20+ references; verify no deadlocks on error conditions
- Test coverage: `tests/unit/test_parallel_processor_regression.py`

**Text normalization utilities (5802 lines):**
- Files: `src/refchecker/utils/text_utils.py`
- Why fragile: Handles LaTeX parsing, Unicode normalization, author name parsing, title similarity, BibTeX cleaning; many regex patterns and edge cases
- Safe modification: Add regression tests before modifying normalization logic; verify changes don't affect existing test fixtures
- Test coverage: Extensive unit tests in `tests/unit/test_*_utils.py`, `tests/unit/test_latex_*.py`, `tests/unit/test_unicode_*.py`

## Scaling Limits

**In-memory WebSocket message buffer:**
- Current capacity: 500 messages per session, unbounded number of sessions until 5-minute timeout
- Limit: With 100 concurrent sessions starting checks, up to 50,000 messages could be buffered in memory before eviction
- Scaling path: Implement Redis-backed message queue for multi-instance deployments; add hard limit on total buffered messages across all sessions

**SQLite connection-per-thread model:**
- Current capacity: One SQLite connection per worker thread; with max_workers=6, up to 6 connections per database
- Limit: SQLite supports ~1000 concurrent connections, but performance degrades beyond 50-100 concurrent readers
- Scaling path: For high-concurrency deployments, migrate to PostgreSQL; implement connection pool with max size limit; add read replica support for local database

**Single-process FastAPI backend:**
- Current capacity: All API requests, WebSocket connections, and background checks run in single process
- Limit: CPU-bound reference checking blocks API responsiveness; GIL limits parallel Python execution
- Scaling path: Move background checks to separate worker processes via Celery or similar; run multiple backend instances behind load balancer; use Redis for session state sharing

**Local Semantic Scholar database file size:**
- Current capacity: Database files can be multiple GB; queries are in-memory with 64MB page cache
- Limit: With 100M+ papers in local database, full-text search and title normalization queries can take 10+ seconds
- Scaling path: Implement FTS5 full-text search index; partition database by publication year or venue; add caching layer for frequently checked references

## Dependencies at Risk

**pypdf and pdfplumber PDF parsing:**
- Risk: Both libraries struggle with non-standard PDF encodings and complex layouts; pypdf has had critical bugs in past versions
- Impact: Reference extraction may fail for papers with unusual PDF formatting; silent failures return empty bibliography
- Migration plan: Add pikepdf as third fallback option (already in optional dependencies); consider GROBID as primary PDF parser (already implemented)

**requests library for all HTTP calls:**
- Risk: Not async-native; creates thread overhead in async FastAPI context; no built-in retry logic
- Impact: HTTP requests block event loop when called from backend; rate-limited APIs require manual retry logic
- Migration plan: Gradually migrate to httpx (already a dependency for OAuth); implement shared retry decorator; use httpx.AsyncClient in backend

**python-jose for JWT:**
- Risk: Library is no longer actively maintained; last release was 2021
- Impact: Security vulnerabilities may not be patched; compatibility issues with newer Python versions
- Migration plan: Migrate to PyJWT (industry standard); test thoroughly as token format may differ

**Fernet encryption for API keys:**
- Risk: Basic symmetric encryption; no key rotation mechanism; key compromise exposes all stored secrets
- Impact: If secret key leaks, all API keys in database are exposed
- Migration plan: Implement envelope encryption with per-key DEKs; add key rotation support; consider using OS keyring on desktop deployments

## Missing Critical Features

**No audit log for multi-user mode:**
- Problem: Admin actions (user management, settings changes) are not logged
- Blocks: Compliance requirements, forensic analysis after security incidents
- Priority: High — required for production multi-user deployments

**No rate limiting on API endpoints:**
- Problem: Single user can spam check requests, exhausting backend resources or API quotas
- Blocks: Production deployment without risk of abuse
- Priority: High — critical for open multi-user deployments

**No telemetry or health checks:**
- Problem: No metrics on check success rate, latency percentiles, or error types; no liveness/readiness endpoints for orchestrators
- Blocks: Production monitoring and alerting
- Priority: Medium — can use external monitoring initially

**No bulk database update mechanism in WebUI:**
- Problem: Local database updates require CLI or manual file operations; WebUI settings show database status but can't trigger updates
- Blocks: Non-technical users from maintaining up-to-date local databases
- Priority: Low — CLI workflow is acceptable for advanced users

## Test Coverage Gaps

**WebSocket manager buffering and replay:**
- What's not tested: Buffer eviction timing, concurrent session message ordering, stale buffer cleanup edge cases
- Files: `backend/websocket_manager.py`
- Risk: Race conditions in buffer management could drop or duplicate messages
- Priority: Medium

**OAuth token validation error paths:**
- What's not tested: Malformed provider responses, expired state tokens, concurrent OAuth flows for same user
- Files: `backend/auth.py:213-238`, `backend/main.py:1058-1090`
- Risk: Security vulnerabilities or user lockout scenarios may not be caught
- Priority: High — auth bugs are user-facing

**LLM provider subprocess cleanup on exceptions:**
- What's not tested: vLLM server orphaned process handling, cleanup when parent process crashes, environment variable filtering edge cases
- Files: `src/refchecker/llm/providers.py:775-869`
- Risk: Orphaned GPU processes consume resources indefinitely
- Priority: Medium — manual cleanup possible but annoying

**Parallel processor thread pool exhaustion:**
- What's not tested: Behavior when processing 1000+ references with limited workers, deadlock scenarios when worker exceptions occur, sentinel value race conditions
- Files: `src/refchecker/core/parallel_processor.py`
- Risk: Deadlocks or dropped references in production workloads
- Priority: Medium

**Database encryption key rotation:**
- What's not tested: Re-encrypting existing secrets with new key, handling decryption failures gracefully, key migration between environments
- Files: `backend/database.py:39-100`
- Risk: Users locked out of stored API keys after key change
- Priority: Low — key rotation is future feature

---

*Concerns audit: 2026-05-27*
