# Coding Conventions

**Analysis Date:** 2026-05-27

## Naming Patterns

**Files:**
- Python modules: `snake_case.py` (e.g., `error_utils.py`, `text_utils.py`, `arxiv_citation.py`)
- Test files: `test_*.py` for unit tests (e.g., `test_error_utils.py`, `test_arxiv_citation_checker.py`)
- React components: `PascalCase.jsx` (e.g., `ReferenceCard.jsx`, `MainPanel.jsx`)
- React utilities: `camelCase.js` (e.g., `referenceStatus.js`, `formatters.js`)
- Test files (web-ui): `*.test.js` or `*.test.jsx` co-located with source

**Functions:**
- Python: `snake_case` (e.g., `clean_author_name()`, `normalize_text()`, `create_author_error()`)
- JavaScript/React: `camelCase` (e.g., `formatAuthors()`, `getEffectiveReferenceStatus()`)
- React components: `PascalCase` (e.g., `ReferenceCard`, `StatusIndicator`)

**Variables:**
- Python: `snake_case` for variables and module-level constants (e.g., `rate_limiter`, `similarity_threshold`)
- Python: `SCREAMING_SNAKE_CASE` for true constants (e.g., `SIMILARITY_THRESHOLD`, `JWT_ALGORITHM`, `DEFAULT_MAX_CONCURRENT`)
- JavaScript: `camelCase` for variables (e.g., `checkStore`, `authRequired`)

**Classes:**
- Python: `PascalCase` with descriptive suffixes (e.g., `ArXivCitationChecker`, `EnhancedHybridReferenceChecker`, `LocalNonArxivReferenceChecker`)
- Pydantic models: `PascalCase` (e.g., `UserInfo`, `CheckRequest`, `CheckHistoryItem`)
- React functional components: `PascalCase` (standard React convention)

**Types:**
- Python: Type hints from `typing` module (e.g., `Dict[str, Any]`, `List[str]`, `Optional[str]`, `Tuple[Optional[str], Optional[str]]`)
- JavaScript: No TypeScript; JSDoc comments used sparingly

## Code Style

**Formatting (Python):**
- Tool: `black` (configured in `pyproject.toml` dev dependencies)
- Line length: Not explicitly configured, black defaults apply
- Indentation: 4 spaces (Python standard)
- String quotes: Mixed single and double quotes; no enforced preference

**Formatting (JavaScript/React):**
- No prettier configuration detected
- Indentation: 2 spaces (standard React/Vite convention)
- String quotes: Mixed single and double quotes; single preferred in newer code

**Linting (Python):**
- Tools: `flake8`, `mypy`, `isort` (configured in `pyproject.toml` dev dependencies)
- Python version: `>=3.11` (supports modern type hints and match statements)

**Linting (JavaScript/React):**
- Tool: ESLint with flat config (`eslint.config.js`)
- Extends: `@eslint/js` recommended, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`
- Key rules:
  - `no-unused-vars`: Error, but ignores args starting with `_`, caught errors starting with `_`, and vars matching `^[A-Z_]` (constants)
  - `react-hooks/refs`: Off
  - `react-hooks/set-state-in-effect`: Off
- ECMAScript version: 2020/latest with JSX support

## Import Organization

**Python Order:**
1. Standard library imports (e.g., `import os`, `import re`, `import logging`)
2. Third-party imports (e.g., `import requests`, `import pandas`, `from fastapi import FastAPI`)
3. Local package imports (e.g., `from refchecker.utils.text_utils import ...`, `from refchecker.checkers.arxiv_citation import ...`)

**Example from `src/refchecker/checkers/arxiv_citation.py`:**
```python
import re
import logging
import requests
import html
import time
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional, Any

from pybtex.database import parse_string
from pybtex.exceptions import PybtexError

from refchecker.utils.arxiv_rate_limiter import ArXivRateLimiter, arxiv_cached_get
from refchecker.utils.text_utils import normalize_text, compare_authors
from refchecker.utils.error_utils import format_title_mismatch, validate_year
from refchecker.config.settings import get_config
```

**JavaScript Order (web-ui):**
1. React imports (e.g., `import { useState, useEffect } from 'react'`)
2. Third-party library imports (e.g., `import axios from 'axios'`)
3. Local component imports (e.g., `import Sidebar from './components/Sidebar/Sidebar'`)
4. Utility/store imports (e.g., `import { logger } from './utils/logger'`, `import { useAuthStore } from './stores/useAuthStore'`)

**Path Aliases:**
- Python: No path aliases; relative imports from `refchecker.*` namespace
- JavaScript: No path aliases configured; relative imports used (e.g., `../../utils/formatters`)

## Error Handling

**Python Patterns:**
- Use standard exceptions with descriptive messages
- Custom error utilities in `src/refchecker/utils/error_utils.py` create standardized error dictionaries:
  - `create_author_error()`, `create_year_warning()`, `create_doi_error()`, `create_title_error()`, `create_venue_warning()`
  - Error/warning dictionaries contain: `error_type`/`warning_type`, `error_details`/`warning_details`, and correction fields (e.g., `ref_authors_correct`)
- HTTP errors: FastAPI raises `HTTPException` with status codes and detail messages
- Network errors: Wrapped with logging and retries where appropriate (e.g., `ArXivRateLimiter`)
- LLM provider errors: Handled per-provider with specific error messages and fallback behavior

**JavaScript/React Patterns:**
- Try-catch blocks for async operations (e.g., API calls)
- Error state managed in Zustand stores
- Logger utility (`utils/logger.js`) for consistent error logging with levels (debug, info, warn, error)
- Network errors logged with full response context

**Example from `backend/main.py`:**
```python
if not arxiv_id and not pdf_file and not text_input:
    raise HTTPException(
        status_code=400,
        detail="Must provide arxiv_id, PDF file, or bibliography text"
    )
```

## Logging

**Python Framework:**
- Standard library `logging` module
- Loggers created per-module: `logger = logging.getLogger(__name__)`
- Levels used: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- Configuration in entry points (e.g., `backend/main.py` configures format and level)

**Python Format:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**JavaScript Framework:**
- Custom logger utility: `web-ui/src/utils/logger.js`
- Levels: `debug`, `info`, `warn`, `error`
- Format: `[LEVEL] ModuleName: message`

**When to Log:**
- Python: Log API calls, database operations, verification steps, errors/warnings, cache hits/misses
- JavaScript: Log state changes, WebSocket events, API errors, user actions (at debug level)

## Comments

**When to Comment:**
- Module/file docstrings: All Python modules have triple-quoted docstrings describing purpose and usage
- Function docstrings: Complex functions include docstrings with Args/Returns sections
- Inline comments: Used to explain non-obvious logic, especially regex patterns, error handling edge cases, and business logic
- TODO/FIXME: Used to mark technical debt or incomplete implementations

**Python Docstring Style:**
- Google-style docstrings (Args, Returns, Raises sections)

**Example from `src/refchecker/llm/providers.py`:**
```python
def _openai_token_kwargs(model: str, max_tokens: int) -> dict:
    """Return the right max-token kwarg for OpenAI models.

    GPT-5 family models require ``max_completion_tokens``
    and do not support custom temperature;
    older models use ``max_tokens``.
    """
    if model and ('gpt-5' in model or 'o3' in model or 'o4' in model):
        return {'max_completion_tokens': max_tokens}
    return {'max_tokens': max_tokens}
```

**JavaScript Comment Style:**
- Brief inline comments for complex logic
- JSDoc comments rarely used; not enforced
- Component-level comments describe behavior (e.g., "Belt-and-braces alongside the global capture-phase handler")

## Function Design

**Python Size:**
- Small utility functions (10-50 lines) preferred
- Complex checkers/processors may have longer functions (100-200 lines) when they implement sequential verification steps
- Very long functions (500+ lines) exist in core modules (`refchecker.py`) and entry points (`backend/main.py`) — candidates for refactoring

**JavaScript Size:**
- React components: 100-500 lines typical, including JSX
- Utility functions: 10-50 lines
- Custom hooks: 20-100 lines

**Parameters:**
- Python: Prefer keyword arguments for clarity; use type hints consistently
- Use `Optional[T]` for nullable parameters
- Default values documented in docstrings
- JavaScript: Destructuring commonly used for object parameters (e.g., `{ user, authRequired, isLoading }`)

**Return Values:**
- Python: Tuple unpacking for multiple returns (e.g., `Tuple[Optional[str], Optional[str]]`)
- Dictionaries for complex structured returns (e.g., verification results with `{'status': ..., 'errors': ..., 'warnings': ...}`)
- JavaScript: Object returns for multiple values (e.g., `{ status, errors, warnings }`)

## Module Design

**Python Exports:**
- Public API exported via `__init__.py` in each package
- Example from `src/refchecker/utils/__init__.py`:
  ```python
  from .text_utils import (
      clean_author_name,
      clean_title,
      normalize_text,
  )
  from .url_utils import extract_arxiv_id_from_url
  from .author_utils import compare_authors, levenshtein_distance
  ```

**JavaScript Exports:**
- Named exports preferred (e.g., `export function formatAuthors() {...}`)
- Default exports for React components (e.g., `export default ReferenceCard`)
- Barrel files: Not used; direct imports from source files

**Path Parity Requirement (Critical):**
- All three execution paths (bulk, CLI, WebUI) **must** call the same core logic in `src/refchecker/`
- Path-specific code limited to I/O, presentation, orchestration (argument parsing, HTTP transport, rendering)
- Configuration, prompts, model selection, verification logic must be shared
- See `AGENTS.md` for detailed path parity requirements

**Shared Core Pattern:**
- Core verification: `src/refchecker/core/refchecker.py`, `src/refchecker/checkers/`
- WebUI wrapper: `backend/refchecker_wrapper.py` (thin orchestration layer)
- CLI entry: `run_refchecker.py` (argument parsing only)
- Bulk scripts: Call into core modules directly

---

*Convention analysis: 2026-05-27*
