# Testing Patterns

**Analysis Date:** 2026-05-27

## Test Framework

**Python Runner:**
- pytest >= 9.0.3
- Config: `pytest.ini`
- Coverage: `pytest-cov >= 7.1.0`

**JavaScript Runner:**
- vitest >= 4.1.5
- Config: `vite.config.js` (test section)
- Assertion Library: `@testing-library/jest-dom` (vitest integration)
- Testing Library: `@testing-library/react >= 16.3.2`
- UI: `@vitest/ui >= 4.1.5` for visual test runner

**E2E Framework:**
- Playwright >= 1.59.1
- Config: `web-ui/playwright.config.js`
- Location: `web-ui/e2e/`

**Run Commands (Python):**
```bash
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest --disable-warnings       # Suppress warnings (default in pytest.ini)
pytest -k test_name             # Run specific test by name
pytest tests/unit               # Run unit tests only
pytest --cov=src --cov-report=html  # Generate coverage report
pytest --run-network            # Include live network tests
pytest --run-llm                # Include live LLM tests (requires API keys)
```

**Run Commands (JavaScript):**
```bash
npm test                        # Run vitest tests
npm run test:ui                 # Run with vitest UI
npm run test:e2e                # Run Playwright E2E tests
npm run test:e2e:ui             # Run Playwright with UI
```

## Test File Organization

**Python Location:**
- Co-located with source: No
- Separate test directory: Yes (`tests/`)
- Structure mirrors source: Partially

**Python Directory Structure:**
```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (91 files)
│   ├── test_error_utils.py
│   ├── test_arxiv_citation_checker.py
│   └── test_hallucination_flagging_regression.py
├── integration/             # Integration tests (API, services)
├── e2e/                     # End-to-end workflow tests
└── fixtures/                # Test data files
```

**JavaScript Location:**
- Co-located: Yes
- Pattern: `*.test.js` and `*.test.jsx` files alongside source
- Shared setup: `web-ui/src/test/setup.js`

**JavaScript Structure:**
```
web-ui/src/
├── utils/
│   ├── referenceStatus.js
│   ├── referenceStatus.test.js    # Co-located test
│   ├── formatters.js
│   └── formatters.test.js
├── stores/
│   ├── useCheckStore.js
│   └── useCheckStore.test.js
├── components/
│   ├── ReferenceCard/
│   │   ├── ReferenceCard.jsx
│   │   └── ReferenceCard.test.jsx
│   └── MainPanel/
│       ├── StatusSection.jsx
│       └── StatusSection.test.jsx
└── test/
    └── setup.js               # Global test setup
```

**Naming:**
- Python: `test_*.py` (prefix)
- JavaScript: `*.test.js` or `*.test.jsx` (suffix)

## Test Structure

**Python Suite Organization:**
```python
class TestAuthorError:
    """Test author error creation."""
    
    def test_create_author_error(self):
        """Test creating author error dictionary."""
        authors = [{'name': 'John Smith'}, {'name': 'Jane Doe'}]
        error = create_author_error("First author mismatch", authors)
        
        assert error['error_type'] == 'author'
        assert error['error_details'] == "First author mismatch"
        assert error['ref_authors_correct'] == "John Smith, Jane Doe"
    
    def test_empty_authors_list(self):
        """Test author error with empty authors list."""
        error = create_author_error("No authors found", [])
        assert error['error_type'] == 'author'
        assert error['ref_authors_correct'] == ""
```

**Python Patterns:**
- Test classes group related tests: `class TestAuthorError`, `class TestYearWarning`
- Test functions describe behavior: `test_create_author_error`, `test_empty_authors_list`
- Docstrings describe what is being tested
- Arrange-Act-Assert pattern
- Skip decorators for conditional tests: `@pytest.mark.skipif(not ERROR_UTILS_AVAILABLE, reason="...")`

**JavaScript Suite Organization:**
```javascript
import { describe, expect, it } from 'vitest'
import { getEffectiveReferenceStatus } from './referenceStatus'

describe('referenceStatus', () => {
  it('treats LLM-found matching metadata as verified, not hallucinated', () => {
    const reference = {
      status: 'hallucination',
      title: 'Pytag: Tabletop games for multi-agent reinforcement learning',
      authors: ['Martin Balla', 'M. Long', 'George E. James Goodman'],
      year: 2024,
      hallucination_assessment: {
        verdict: 'LIKELY',
        found_title: 'Pytag: Tabletop games for multi-agent reinforcement learning',
      },
    }

    expect(llmFoundMetadataMatchesCitation(reference)).toBe(true)
    expect(getEffectiveReferenceStatus(reference, true)).toBe('verified')
  })

  it('prioritizes hallucination over errors and warnings', () => {
    const reference = {
      status: 'hallucination',
      errors: [{ error_type: 'author', error_details: 'Author mismatch' }],
      warnings: [{ error_type: 'year', error_details: 'Year mismatch' }],
    }

    expect(getEffectiveReferenceStatus(reference, true)).toBe('hallucination')
  })
})
```

**JavaScript Patterns:**
- `describe()` blocks group related tests
- `it()` describes specific behavior
- Assertion style: `expect(value).toBe(expected)`, `expect(value).toEqual(object)`
- Setup/teardown: Use `beforeEach`, `afterEach` when needed (not shown in examples but available)

## Mocking

**Python Framework:**
- `unittest.mock` (Mock, MagicMock, patch)
- Fixtures for complex mock objects

**Python Patterns:**
```python
@pytest.fixture
def mock_requests_session():
    """Mock requests session for API calls."""
    session = Mock()
    response = Mock()
    response.status_code = 200
    response.json.return_value = {}
    response.text = ""
    session.get.return_value = response
    return session

@pytest.fixture
def disable_network_calls(monkeypatch):
    """Disable all network calls during testing."""
    def mock_get(*args, **kwargs):
        raise RuntimeError("Network calls disabled in tests")
    
    monkeypatch.setattr("requests.get", mock_get)
    monkeypatch.setattr("requests.post", mock_post)
```

**JavaScript Framework:**
- Vitest built-in mocking (`vi.fn()`, `vi.mock()`)
- Global mocks in `web-ui/src/test/setup.js`

**JavaScript Patterns:**
```javascript
// Global setup.js mocks
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  })),
})

// localStorage mock
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// WebSocket mock
class MockWebSocket {
  constructor(url) {
    this.url = url
    this.readyState = WebSocket.CONNECTING
    setTimeout(() => {
      this.readyState = WebSocket.OPEN
      this.onopen?.()
    }, 0)
  }
  send = vi.fn()
  close = vi.fn(() => {
    this.readyState = WebSocket.CLOSED
    this.onclose?.({ code: 1000 })
  })
}
global.WebSocket = MockWebSocket
```

**What to Mock:**
- Python: External HTTP requests, file I/O, database connections, LLM API calls, environment variables
- JavaScript: `window.matchMedia`, `localStorage`, `WebSocket`, browser APIs

**What NOT to Mock:**
- Pure utility functions (test them directly)
- Internal business logic (integration tests should exercise real code paths)
- Trivial getters/setters

## Fixtures and Factories

**Python Fixtures (tests/conftest.py):**
```python
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_bibliography():
    """Sample bibliography text for testing."""
    return """
References

[1] Attention Is All You Need. Ashish Vaswani, Noam Shazeer...
[2] BERT: Pre-training of Deep Bidirectional Transformers...
"""

@pytest.fixture
def sample_references():
    """Sample parsed reference data for testing."""
    return [
        {
            'title': 'Attention Is All You Need',
            'authors': ['Ashish Vaswani', 'Noam Shazeer', ...],
            'year': 2017,
            'url': 'https://arxiv.org/abs/1706.03762',
            'type': 'arxiv'
        },
    ]

@pytest.fixture
def clean_environment(monkeypatch):
    """Clean environment variables for testing."""
    env_vars_to_clean = [
        'SEMANTIC_SCHOLAR_API_KEY',
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
    ]
    for var in env_vars_to_clean:
        monkeypatch.delenv(var, raising=False)
```

**Location:**
- Python: `tests/conftest.py` for shared fixtures
- JavaScript: `web-ui/src/test/setup.js` for global setup

**Fixture Scope:**
- Python: Function-scoped by default (created/destroyed per test)
- Use `@pytest.fixture(scope="module")` or `scope="session"` for expensive setup

## Coverage

**Requirements:**
- No enforced minimum coverage threshold
- Coverage reporting available but not mandatory

**Python Coverage:**
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
# Generates htmlcov/ directory with detailed coverage report
```

**Python Coverage Config (pytest.ini, commented out):**
```ini
# addopts = --cov=src --cov-report=html --cov-report=term-missing
```

**JavaScript Coverage:**
- Vitest provides built-in coverage via `v8` or `istanbul`
- Not currently configured in `vite.config.js`
- Can be enabled with `vitest --coverage`

**View Coverage:**
```bash
# Python
pytest --cov=src --cov-report=html
open htmlcov/index.html

# JavaScript
npm test -- --coverage
```

## Test Types

**Unit Tests (Python):**
- Scope: Individual functions, classes, utilities
- Location: `tests/unit/`
- Isolation: Mock external dependencies (network, database, LLM)
- Example: `test_error_utils.py` tests error creation functions in isolation
- Markers: `@pytest.mark.unit`

**Unit Tests (JavaScript):**
- Scope: Individual functions, React components
- Co-located with source
- Example: `referenceStatus.test.js` tests status computation logic

**Integration Tests (Python):**
- Scope: API interactions, service layer, database operations
- Location: `tests/integration/`
- May use test database or mock external APIs
- Markers: `@pytest.mark.integration`

**E2E Tests (JavaScript):**
- Framework: Playwright
- Location: `web-ui/e2e/`
- Scope: Full user workflows (login, check references, view history)
- Markers: `@pytest.mark.e2e` (Python equivalent)

**Live Network Tests (Python):**
- Marker: `@pytest.mark.network`
- Opt-in via `--run-network` flag
- Skip by default to keep tests deterministic
- Example: Tests that hit Semantic Scholar API, arXiv API

**Live LLM Tests (Python):**
- Marker: `@pytest.mark.llm` (opt-in via `--run-llm`)
- Auto-keyed marker: `@pytest.mark.llm_auto_keyed` (runs automatically when API keys are present)
- Requires API keys in environment (e.g., `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`)
- Skip when API keys not configured

**Test Selection (pytest.ini):**
```ini
markers =
    unit: Unit tests for individual components
    integration: Integration tests for API and service interactions
    e2e: End-to-end tests for complete workflows
    slow: Tests that take a long time to run
    network: Tests that require network access
    llm: Tests that require LLM API access
    llm_auto_keyed: Live LLM tests that run in the normal suite when provider keys are configured
    github: Tests that interact with GitHub API
```

## Common Patterns

**Python Async Testing:**
- pytest-asyncio used for async test functions
- Not heavily used (most tests are synchronous)

**Python Error Testing:**
```python
def test_invalid_doi_comparisons(self):
    """Test that invalid or empty DOIs are handled correctly"""
    from refchecker.utils.doi_utils import compare_dois
    
    test_cases = [
        ('', '10.1016/j.pmcj.2020.101221'),
        ('10.1016/j.pmcj.2020.101221', ''),
        (None, '10.1016/j.pmcj.2020.101221'),
    ]
    
    for cited, actual in test_cases:
        result = compare_dois(cited, actual)
        assert not result, f"Invalid DOI comparison should return False: {cited} vs {actual}"
```

**Python Parametric Testing:**
```python
def test_case_insensitive_comparison(self):
    """Test that DOI comparison is case-insensitive"""
    test_cases = [
        ('10.1016/j.isprsjprs.2007.01.001', '10.1016/J.ISPRSJPRS.2007.01.001'),
        ('10.1016/J.PMCj.2022.101687', '10.1016/j.pmcj.2022.101687'),
    ]
    
    for cited, actual in test_cases:
        assert compare_dois(cited, actual), f"DOIs should match despite case differences"
```

**JavaScript Component Testing:**
```javascript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import ReferenceCard from './ReferenceCard'

it('renders reference title', () => {
  render(<ReferenceCard reference={{ title: 'Test Paper' }} />)
  expect(screen.getByText('Test Paper')).toBeInTheDocument()
})
```

**JavaScript Store Testing (Zustand):**
```javascript
import { renderHook, act } from '@testing-library/react'
import { useCheckStore } from './useCheckStore'

it('updates check status', () => {
  const { result } = renderHook(() => useCheckStore())
  
  act(() => {
    result.current.setStatus('running')
  })
  
  expect(result.current.status).toBe('running')
})
```

## Test Configuration

**Python (pytest.ini):**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes

minversion = 6.0
log_cli = true
log_cli_level = INFO
```

**JavaScript (vite.config.js):**
```javascript
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    css: true,
    exclude: ['**/node_modules/**', '**/e2e/**'],
  },
})
```

**Custom Test Flags:**
- `--run-network`: Enable live network tests (Python)
- `--run-llm`: Enable live LLM tests (Python)
- Tests marked with `@pytest.mark.network` or `@pytest.mark.llm` are skipped by default

---

*Testing analysis: 2026-05-27*
