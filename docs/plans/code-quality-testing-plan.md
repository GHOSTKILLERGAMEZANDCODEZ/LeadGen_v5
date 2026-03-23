# LeadGen v5 - Code Quality & Testing Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task with review checkpoints.

**Goal:** Comprehensive code optimization, refactoring, and testing for LeadGen v5 PySide6 application.

**Architecture:**

- Business logic layer (modules/) - optimize and test
- GUI layer (gui/) - refactor to PySide6 best practices
- Database layer (database/) - optimize queries
- Utilities (utils/) - clean up and document

**Tech Stack:** PySide6 >= 6.5.0, pandas >= 2.0.0, pytest, mypy, black, requests, beautifulsoup4

---

## Phase 1: Code Review & Analysis (Tasks 1-10)

### Task 1: Run python-ds-reviewer on data_processor.py

**Files:**

- Review: `modules/data_processor.py`
- Review: `modules/phone_validator.py`
- Review: `modules/bitrix_mapper.py`

**Agent:** `python-ds-reviewer`

**Steps:**

**Step 1: Launch python-ds-reviewer agent**

```bash
# Agent will analyze:
# - Data processing efficiency
# - Pandas operations optimization
# - Type annotations completeness
# - Error handling patterns
```

**Step 2: Review report**
Expected output:

- Performance bottlenecks identified
- Type annotation gaps
- Error handling improvements
- Code style recommendations

**Step 3: Create issues list**

```markdown
## Data Processor Issues
- [ ] Issue 1: Description
- [ ] Issue 2: Description
```

**Step 4: Commit review results**

```bash
git add docs/reviews/data_processor_review.md
git commit -m "docs: add data processor code review"
```

---

### Task 2: Run python-ds-reviewer on lpr_parser.py

**Files:**

- Review: `modules/lpr_parser.py`

**Agent:** `python-ds-reviewer`

**Steps:**

**Step 1: Launch agent**

```bash
# Agent will analyze:
# - Web scraping patterns
# - HTML parsing efficiency
# - Error handling for network requests
# - Data extraction patterns
```

**Step 2: Review report**
Expected: Recommendations for parser optimization

**Step 3: Commit**

```bash
git add docs/reviews/lpr_parser_review.md
git commit -m "docs: add LPR parser code review"
```

---

### Task 3: Run python-web-architect on GUI modules

**Files:**

- Review: `gui/pages/processing_page.py`
- Review: `gui/pages/analytics_page.py`
- Review: `gui/pages/manager_monitor_page.py`
- Review: `gui/pages/settings_page.py`
- Review: `gui/pages/link_generator_page.py`
- Review: `gui/pages/lpr_finder_page.py`

**Agent:** `python-web-architect`

**Steps:**

**Step 1: Launch agent**

```bash
# Agent will analyze:
# - PySide6 best practices
# - Signal/slot patterns
# - Memory management
# - UI responsiveness
# - Thread safety
```

**Step 2: Review report**
Expected:

- GUI architecture improvements
- Signal/slot optimization
- Memory leak prevention
- Thread safety recommendations

**Step 3: Commit**

```bash
git add docs/reviews/gui_review.md
git commit -m "docs: add GUI code review"
```

---

### Task 4: Run mypy strict type checking

**Files:**

- All Python files in `gui/`, `modules/`, `utils/`, `database/`

**Steps:**

**Step 1: Install mypy**

```bash
pip install mypy
```

**Step 2: Run mypy strict**

```bash
mypy --strict --ignore-missing-imports gui/ modules/ utils/ database/ > docs/reports/mypy_report.txt
```

**Step 3: Review report**
Expected: List of type annotation errors

**Step 4: Create fix list**

```markdown
## Type Annotation Issues
- gui/main_window.py: Line 45 - Missing return type
- modules/data_processor.py: Line 123 - Missing parameter types
```

**Step 5: Commit report**

```bash
git add docs/reports/mypy_report.txt
git commit -m "docs: add mypy strict report"
```

---

### Task 5: Run black formatting check

**Steps:**

**Step 1: Install black**

```bash
pip install black
```

**Step 2: Check formatting**

```bash
black --check --diff gui/ modules/ utils/ database/ > docs/reports/black_report.txt
```

**Step 3: Apply formatting**

```bash
black gui/ modules/ utils/ database/
```

---

### Task 6: Analyze import structure

**Files:**

- All `__init__.py` files
- All page files

**Steps:**

**Step 1: Check for circular imports**

```bash
python -c "import gui; import modules; import utils; print('No circular imports')"
```

**Step 2: Verify import order**

```bash
# Standard lib → Third-party → Local
# Use isort if needed
pip install isort
isort --check-only gui/ modules/ utils/ database/
```

**Step 3: Fix if needed**

```bash
isort gui/ modules/ utils/ database/
git commit -am "style: fix import order with isort"
```

---

### Task 7: Document public API

**Files:**

- `modules/__init__.py`
- `gui/__init__.py`
- `utils/__init__.py`
- `database/__init__.py`

**Steps:**

**Step 1: Review current exports**

```python
# modules/__init__.py
__all__ = ['data_processor', 'bitrix_mapper', 'phone_validator', ...]
```

**Step 2: Add missing exports**

```python
# Ensure all public functions are exported
__all__ = [
    'merge_files',
    'export_to_bitrix_csv',
    'clean_phone',
    ...
]
```

**Step 3: Commit**

```bash
git add modules/__init__.py gui/__init__.py utils/__init__.py database/__init__.py
git commit -m "refactor: document public API exports"
```

---

### Task 8: Analyze database queries

**Files:**

- `database/models.py`
- `database/db_manager.py`

**Steps:**

**Step 1: Review SQL queries**

```python
# Check for:
# - Missing indexes
# - N+1 query problems
# - Transaction usage
# - Connection pooling
```

**Step 2: Add indexes if missing**

```python
# Already present in models.py:
# - idx_statistics_filename
# - idx_statistics_load_date
# - idx_managers_name
# - idx_processing_history_date
```

**Step 3: Document findings**

```markdown
## Database Optimization
- [x] Indexes present
- [x] No N+1 queries
- [ ] Add connection pooling (optional)
```

**Step 4: Commit documentation**

```bash
git add docs/reviews/database_review.md
git commit -m "docs: add database review"
```

---

### Task 9: Performance profiling

**Files:**

- `modules/data_processor.py`
- `modules/bitrix_mapper.py`

**Steps:**

**Step 1: Install profiler**

```bash
pip install cProfile
```

**Step 2: Profile data processing**

```bash
python -m cProfile -o profile.stats main.py
# Process sample data
```

**Step 3: Analyze results**

```bash
python -m pstats profile.stats
# Sort by time
# Identify bottlenecks
```

**Step 4: Document findings**

```markdown
## Performance Bottlenecks
1. merge_files() - 45% of total time
2. clean_phone() - 25% of total time
3. map_to_bitrix() - 20% of total time
```

**Step 5: Commit**

```bash
git add docs/reports/performance_profile.md
git commit -m "docs: add performance profiling report"
```

---

### Task 10: Create optimization backlog

**Files:**

- `docs/plans/optimization_backlog.md`

**Steps:**

**Step 1: Consolidate all findings**

```markdown
# Optimization Backlog

## Critical
- [ ] Issue 1 from code review
- [ ] Issue 2 from mypy

## High Priority
- [ ] Performance bottleneck 1
- [ ] Type annotation gap 1

## Medium Priority
- [ ] Code style issue 1
- [ ] Documentation gap 1

## Low Priority
- [ ] Nice-to-have improvement 1
```

**Step 2: Prioritize**

```markdown
Priority matrix:
- Critical + Easy → Do first
- Critical + Hard → Plan carefully
- Low + Easy → Do when bored
- Low + Hard → Maybe never
```

**Step 3: Commit**

```bash
git add docs/plans/optimization_backlog.md
git commit -m "docs: create optimization backlog"
```

---

## Phase 2: Testing Infrastructure (Tasks 11-20)

### Task 11: Setup pytest infrastructure

**Files:**

- Create: `tests/conftest.py`
- Create: `tests/__init__.py`
- Modify: `requirements.txt`

**Steps:**

**Step 1: Add test dependencies**

```txt
# requirements.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
```

**Step 2: Install**

```bash
pip install -r requirements.txt
```

**Step 3: Create conftest.py**

```python
"""
Pytest configuration and fixtures.
"""
import pytest
from pathlib import Path


@pytest.fixture
def sample_data_dir() -> Path:
    """Path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_output_dir(tmp_path) -> Path:
    """Temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
```

**Step 4: Create pytest.ini**

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=gui --cov=modules --cov=utils --cov=database
```

**Step 5: Commit**

```bash
git add tests/conftest.py pytest.ini requirements.txt
git commit -m "test: setup pytest infrastructure"
```

---

### Task 12: Write tests for phone_validator.py

**Files:**

- Modify: `tests/test_phone_validator.py`

**Agent:** `python-ds-reviewer` (for test quality review)

**Steps:**

**Step 1: Review existing tests**

```bash
# Current tests cover:
# - clean_phone() with valid numbers
# - clean_phone() with invalid numbers
# - format_phone() with different formats
# - validate_phone()
```

**Step 2: Add missing tests**

```python
def test_clean_phone_with_whitespace():
    """Test phone cleaning with whitespace."""
    assert clean_phone("+7 (999) 123-45-67") == "79991234567"


def test_clean_phone_with_extension():
    """Test phone cleaning with extension."""
    assert clean_phone("79991234567 доб. 123") == "79991234567"


def test_clean_phone_international_format():
    """Test international format."""
    assert clean_phone("+7 999 123 45 67", phone_format="+7") == "+79991234567"
```

**Step 3: Run tests**

```bash
pytest tests/test_phone_validator.py -v
# Expected: All PASS
```

**Step 4: Check coverage**

```bash
pytest tests/test_phone_validator.py --cov=modules.phone_validator
# Expected: >90% coverage
```

**Step 5: Commit**

```bash
git add tests/test_phone_validator.py
git commit -m "test: add phone validator tests"
```

---

### Task 13: Write tests for data_processor.py

**Files:**

- Create: `tests/test_data_processor.py`

**Steps:**

**Step 1: Create test file**

```python
"""
Tests for data processing module.
"""
import pytest
import pandas as pd
from modules.data_processor import (
    load_file,
    clean_phone_column,
    remove_duplicates,
    assign_managers,
    merge_files,
)
```

**Step 2: Write load_file tests**

```python
def test_load_json_file(sample_data_dir):
    """Test loading JSON file."""
    filepath = sample_data_dir / "test.json"
    df = load_file(filepath)
    assert df is not None
    assert len(df) > 0


def test_load_csv_file(sample_data_dir):
    """Test loading CSV file."""
    filepath = sample_data_dir / "test.csv"
    df = load_file(filepath)
    assert df is not None


def test_load_invalid_file():
    """Test loading invalid file."""
    df = load_file("nonexistent.json")
    assert df is None
```

**Step 3: Write clean_phone tests**

```python
def test_clean_phone_column():
    """Test phone column cleaning."""
    series = pd.Series(["79991234567", "89991234567", None, "nan"])
    cleaned = clean_phone_column(series)
    assert cleaned.iloc[0] == "79991234567"
    assert cleaned.iloc[1] == "79991234567"
    assert pd.isna(cleaned.iloc[2])
```

**Step 4: Write duplicate removal tests**

```python
def test_remove_duplicates():
    """Test duplicate removal."""
    df = pd.DataFrame({
        'phone_1': ['79991234567', '79991234567', '79991234568']
    })
    df_cleaned, duplicates = remove_duplicates(df)
    assert len(df_cleaned) == 2
    assert duplicates == 1
```

**Step 5: Run tests**

```bash
pytest tests/test_data_processor.py -v
# Expected: All PASS
```

**Step 6: Commit**

```bash
git add tests/test_data_processor.py
git commit -m "test: add data processor tests"
```

---

### Task 14: Write tests for bitrix_mapper.py

**Files:**

- Modify: `tests/test_bitrix_mapper.py`

**Steps:**

**Step 1: Add mapping tests**

```python
def test_map_to_bitrix_columns():
    """Test Bitrix column mapping."""
    df = pd.DataFrame({'Название лида': ['Test'], 'Рабочий телефон': ['79991234567']})
    mapped = map_to_bitrix(df)
    assert 'Название лида' in mapped.columns
    assert 'Рабочий телефон' in mapped.columns
    assert len(mapped.columns) == 64


def test_export_to_bitrix_csv(temp_output_dir):
    """Test CSV export."""
    df = pd.DataFrame({'Название лида': ['Test']})
    filepath = temp_output_dir / "test.csv"
    success = export_to_bitrix_csv(df, filepath)
    assert success
    assert filepath.exists()
```

**Step 2: Run tests**

```bash
pytest tests/test_bitrix_mapper.py -v
```

**Step 3: Commit**

```bash
git add tests/test_bitrix_mapper.py
git commit -m "test: add bitrix mapper tests"
```

---

### Task 15: Write tests for GUI components

**Files:**

- Create: `tests/gui/test_main_window.py`
- Create: `tests/gui/test_sidebar.py`

**Steps:**

**Step 1: Setup GUI testing**

```python
"""
GUI component tests.
"""
import pytest
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


@pytest.fixture
def app():
    """Create QApplication for tests."""
    app = QApplication.instance() or QApplication([])
    yield app
    app.quit()


@pytest.fixture
def main_window(app):
    """Create main window for tests."""
    window = MainWindow()
    window.show()
    yield window
    window.close()
```

**Step 2: Write window tests**

```python
def test_main_window_creates(main_window):
    """Test main window creation."""
    assert main_window is not None
    assert main_window.isVisible()


def test_sidebar_exists(main_window):
    """Test sidebar exists."""
    assert main_window._sidebar is not None
```

**Step 3: Run tests**

```bash
pytest tests/gui/test_main_window.py -v
# Note: Requires display (Xvfb on CI)
```

**Step 4: Commit**

```bash
git add tests/gui/
git commit -m "test: add GUI component tests"
```

---

### Task 16: Write integration tests

**Files:**

- Create: `tests/integration/test_full_workflow.py`

**Steps:**

**Step 1: Create integration test**

```python
"""
Integration tests for full workflow.
"""
import pytest
from pathlib import Path
from modules.data_processor import merge_files
from modules.bitrix_mapper import export_to_bitrix_csv


def test_full_workflow(sample_data_dir, temp_output_dir):
    """Test complete lead processing workflow."""
    # Load test data
    test_file = sample_data_dir / "test_leads.json"
    
    # Process files
    managers = ["Manager 1", "Manager 2"]
    df, stats = merge_files([str(test_file)], managers)
    
    # Verify processing
    assert df is not None
    assert len(df) > 0
    assert 'Ответственный' in df.columns
    
    # Export to Bitrix
    output_file = temp_output_dir / "output.csv"
    success = export_to_bitrix_csv(df, str(output_file))
    
    # Verify export
    assert success
    assert output_file.exists()
```

**Step 2: Run integration tests**

```bash
pytest tests/integration/ -v
```

**Step 3: Commit**

```bash
git add tests/integration/
git commit -m "test: add integration tests"
```

---

### Task 17: Setup CI/CD configuration

**Files:**

- Create: `.github/workflows/tests.yml`
- Create: `.gitlab-ci.yml` (if using GitLab)

**Steps:**

**Step 1: Create GitHub Actions workflow**

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=gui --cov=modules --cov=utils --cov=database
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

**Step 2: Commit**

```bash
git add .github/workflows/tests.yml
git commit -m "ci: add GitHub Actions workflow"
```

---

### Task 18: Add code coverage reporting

**Files:**

- Create: `.coveragerc`
- Modify: `pytest.ini`

**Steps:**

**Step 1: Create coverage config**

```ini
# .coveragerc
[run]
source = gui,modules,utils,database
omit = 
    */tests/*
    */__init__.py
    */conftest.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError

[html]
directory = htmlcov
```

**Step 2: Generate coverage report**

```bash
pytest --cov=gui --cov=modules --cov=utils --cov=database --cov-report=html
# Opens htmlcov/index.html in browser
```

**Step 3: Check coverage threshold**

```bash
pytest --cov=gui --cov=modules --cov-fail-under=80
# Fails if coverage < 80%
```

**Step 4: Commit**

```bash
git add .coveragerc
git commit -m "test: add coverage configuration"
```

---

### Task 19: Create test data fixtures

**Files:**

- Create: `tests/data/test_leads.json`
- Create: `tests/data/test_leads.csv`
- Create: `tests/data/test_companies.csv`

**Steps:**

**Step 1: Create test JSON**

```json
[
  {
    "Название": "Test Company 1",
    "Адрес": "Test Address 1",
    "phone_1": "79991234567",
    "phone_2": "79991234568",
    "Category 0": "Test Category",
    "companyUrl": "https://example.com"
  }
]
```

**Step 2: Create test CSV**

```csv
Название,Адрес,phone_1,phone_2,Category 0,companyUrl
Test Company 1,Test Address 1,79991234567,79991234568,Test Category,https://example.com
```

**Step 3: Commit**

```bash
git add tests/data/
git commit -m "test: add test data fixtures"
```

---

### Task 20: Document testing strategy

**Files:**

- Create: `docs/TESTING.md`

**Steps:**

**Step 1: Create testing documentation**

```markdown
# Testing Strategy

## Test Structure
```

tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── gui/           # GUI tests
└── data/          # Test fixtures

```

## Running Tests
```bash
# All tests
pytest

# Specific module
pytest tests/test_phone_validator.py

# With coverage
pytest --cov=gui --cov=modules

# Generate HTML report
pytest --cov-report=html
```

## Coverage Requirements

- Unit tests: >90%
- Integration tests: >80%
- GUI tests: >70%

## CI/CD

Tests run automatically on:

- Every push
- Every pull request
- Python 3.11 and 3.12

```

**Step 2: Commit**
```bash
git add docs/TESTING.md
git commit -m "docs: add testing strategy documentation"
```

---

## Phase 3: Optimization & Refactoring (Tasks 21-30)

### Task 21-30: Implement optimizations based on review findings

**Note:** These tasks will be defined after completing Phase 1 & 2 reviews.

**Expected areas:**

- Performance optimization (from Task 9 profiling)
- Type annotation completion (from Task 4 mypy)
- Code structure improvements (from Task 3 GUI review)
- Database query optimization (from Task 8)
- Memory management improvements
- Error handling standardization

---

## Execution Checklist

- [ ] Phase 1: Code Review & Analysis (Tasks 1-10)
- [ ] Phase 2: Testing Infrastructure (Tasks 11-20)
- [ ] Phase 3: Optimization & Refactoring (Tasks 21-30)
- [ ] Final: Documentation & Handoff

---

## Success Criteria

1. **Code Quality:**
   - mypy strict: 0 errors
   - black: 100% formatted
   - pylint: >9/10 score

2. **Test Coverage:**
   - Overall: >85%
   - Critical modules: >90%
   - GUI: >70%

3. **Performance:**
   - Data processing: <5 seconds for 1000 leads
   - GUI responsiveness: <100ms for UI operations
   - Memory usage: <500MB for typical workload

4. **Documentation:**
   - All public APIs documented
   - Testing strategy documented
   - Optimization decisions documented
