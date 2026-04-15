# Contributing to Platelet-Movie

Thank you for your interest in contributing to Platelet-Movie! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

This project adheres to a simple code of conduct:

- **Be respectful and inclusive**: Treat everyone with respect. We welcome contributors of all backgrounds and experience levels.
- **Be collaborative**: Work together constructively and assume good intentions.
- **Be professional**: Keep discussions focused on the project and technical matters.

Unacceptable behavior will not be tolerated. If you experience or witness unacceptable behavior, please report it by opening an issue or contacting the maintainers.

---

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs. **actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Relevant logs or error messages**

**Example:**
```markdown
**Title:** Score column shows "N/A" for all movies

**Description:**
The Score column in the static site displays "N/A" for all movie titles instead of showing the TMDB rating.

**Steps to Reproduce:**
1. Navigate to the GitHub Pages site
2. Observe the Score column in the movies table

**Expected:** Should show ratings like "8.1", "7.5", etc.
**Actual:** Shows "N/A" for all entries

**Environment:** Viewing on Chrome 120, macOS
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Clear description** of the enhancement
- **Use case**: Why would this be useful?
- **Proposed implementation** (if you have ideas)
- **Alternatives considered**

### Submitting Pull Requests

We actively welcome pull requests! See the [Pull Request Process](#pull-request-process) section below.

---

## Development Setup

### Prerequisites

- **Python** ≥ 3.11
- **Poetry** ≥ 2.0
- **Git**

### Installation

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Platelet-Movie.git
   cd Platelet-Movie
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/tegataiprime/Platelet-Movie.git
   ```

4. **Install dependencies**:
   ```bash
   poetry install
   ```

5. **Activate the virtual environment**:
   ```bash
   poetry shell
   ```

6. **Set up environment variables**:
   ```bash
   export TMDB_API_KEY="your_tmdb_api_key"
   ```
   
   Get a free TMDB API key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)

7. **Verify the setup**:
   ```bash
   poe test
   ```

### Using Doppler for Secrets (Recommended)

For local development, we recommend using [Doppler](https://www.doppler.com/) to manage secrets:

```bash
# Install Doppler CLI
brew install dopplerhq/cli/doppler  # macOS

# Login and setup
doppler login
doppler setup

# Run commands with secrets
doppler run -- poe run
doppler run -- poe test
```

---

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Use descriptive branch names:
- `feature/add-genre-filter` (for new features)
- `fix/score-column-regression` (for bug fixes)
- `docs/update-readme` (for documentation)
- `refactor/improve-sorting` (for refactoring)

### 2. Make Your Changes

Follow the [Test-Driven Development (TDD)](#test-driven-development-tdd) approach:

1. **Write a failing test** that defines the desired behavior
2. **Run the test** to confirm it fails: `poe test`
3. **Write minimal code** to make the test pass
4. **Run the test** to confirm it passes
5. **Refactor** if needed while keeping tests green

### 3. Test Your Changes

Run the full test suite:

```bash
# Run all tests with coverage
poe test

# Run specific test file
pytest tests/test_formatters.py -v

# Run tests with verbose output
pytest -vv
```

**All tests must pass before submitting a PR.**

### 4. Lint and Format

```bash
# Check code style
poe lint

# Auto-format code
poe format
```

### 5. Update Documentation

If your changes affect user-facing functionality:

- **Update README.md** with new features, options, or configuration
- **Update code comments** for complex logic
- **Add docstrings** for new functions/classes

### 6. Commit Your Changes

Follow the [Commit Message Guidelines](#commit-message-guidelines):

```bash
git add .
git commit -m "Fix: Resolve Score column showing N/A for all movies"
```

### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

---

## Coding Standards

### Python Style Guide

- **PEP 8** compliance (enforced by Ruff)
- **Maximum line length**: 100 characters
- **Type hints** for function signatures (encouraged)
- **Docstrings** for public functions and classes

### Code Formatting

We use **Ruff** for linting and formatting:

```bash
# Auto-format code
poe format

# Check for issues
poe lint
```

Ruff is configured in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]
```

### Test-Driven Development (TDD)

**Always write tests before implementation.**

Example workflow:

```python
# 1. Write a failing test (tests/test_formatters.py)
def test_json_includes_vote_average():
    movies = [Movie(title="Test", runtime_minutes=120, rating=8.5)]
    result = format_movies(movies, "json")
    parsed = json.loads(result)
    assert parsed[0]["vote_average"] == 8.5  # This will fail initially

# 2. Run test to confirm it fails
# $ poe test

# 3. Implement the feature (platelet_movie/formatters.py)
def _format_json(movies: list[Movie]) -> str:
    movie_dicts = [
        {
            "title": movie.title,
            "vote_average": movie.rating,  # Changed from "rating"
            # ... other fields
        }
        for movie in movies
    ]
    return json.dumps(movie_dicts, indent=2)

# 4. Run test to confirm it passes
# $ poe test

# 5. Refactor if needed (while keeping tests green)
```

### Configuration

- **Use environment variables** for all configuration (12-Factor App)
- **Never commit secrets** to version control
- **Document new environment variables** in README.md

---

## Testing Requirements

### Coverage Requirements

- **Minimum coverage**: 80% (enforced by CI)
- **Current coverage**: 98%

### Running Tests

```bash
# Full test suite with coverage
poe test

# Run specific test file
pytest tests/test_cli.py -v

# Run tests matching a pattern
pytest -k "test_format" -v

# Show coverage report
pytest --cov=platelet_movie --cov-report=term-missing
```

### Writing Tests

Use **pytest** with **pytest-mock** for mocking:

```python
def test_discover_movies_filters_by_runtime(mocker):
    """Test that movies are filtered by minimum runtime."""
    # Mock the API response
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "results": [
            {"id": 1, "title": "Short Movie", "runtime": 90},
            {"id": 2, "title": "Long Movie", "runtime": 150},
        ]
    }
    
    # Test the functionality
    client = TMDBClient(api_key="test_key")
    movies = client.discover_movies_on_netflix(min_runtime=120)
    
    # Assert expectations
    assert len(movies) == 1
    assert movies[0].title == "Long Movie"
```

### Test Organization

Tests are organized by module:

```
tests/
├── test_cli.py              # CLI interface tests
├── test_tmdb_client.py      # TMDB API client tests
├── test_config.py           # Configuration tests
├── test_models.py           # Data model tests
├── test_formatters.py       # Output formatter tests
├── test_generate_site_data.py  # Site generation tests
└── test_lady_whistledown.py    # Commentary generator tests
```

---

## Commit Message Guidelines

### Format

```
<type>: <subject>

[optional body]

[optional footer]
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring (no feature change or bug fix)
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (dependencies, build, etc.)

### Examples

**Good commit messages:**
```
feat: Add genre filter to CLI

Adds --genre option to filter movies by genre name.
Users can now search for specific genres like "Action" or "Drama".

Closes #42
```

```
fix: Resolve Score column showing N/A for all movies

Changed JSON output field from "rating" to "vote_average" to match
the JavaScript expectation in the static site.

Updated tests to reflect the field name change.
```

```
docs: Update README with Red Cross branding changes

- Document new color scheme (Red Cross Red #E42424)
- Add American Red Cross disclaimer
- Update GitHub Pages features section
```

**Bad commit messages:**
```
fixed bug          # Too vague, no context
Updated files      # Doesn't explain what changed
WIP                # Not descriptive
```

### Commit Best Practices

- **One logical change per commit**
- **Write in imperative mood**: "Add feature" not "Added feature"
- **Keep subject line under 72 characters**
- **Reference issues** when applicable: "Closes #123" or "Fixes #456"

---

## Pull Request Process

### Before Submitting

1. ✅ **All tests pass**: `poe test`
2. ✅ **Code is linted**: `poe lint`
3. ✅ **Code is formatted**: `poe format`
4. ✅ **Documentation is updated** (README.md if needed)
5. ✅ **Commit messages follow guidelines**
6. ✅ **Branch is up to date** with `main`:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### Creating the Pull Request

1. **Push your branch** to your fork
2. **Create a PR** on GitHub from your branch to `tegataiprime/Platelet-Movie:main`
3. **Fill out the PR template** with:
   - **Clear description** of changes
   - **Motivation**: Why is this change needed?
   - **Testing**: How was this tested?
   - **Screenshots** (if UI changes)
   - **Related issues**: "Closes #123"

### PR Review Process

- Maintainers will review your PR
- **Automated checks** will run (tests, linting, coverage)
- You may be asked to make changes
- Once approved, a maintainer will merge your PR

### After Merge

1. **Delete your feature branch** (optional but recommended):
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. **Update your local main**:
   ```bash
   git checkout main
   git pull upstream main
   ```

---

## Questions?

If you have questions about contributing:

1. **Check existing issues and discussions**
2. **Open a new issue** with the "question" label
3. **Tag maintainers** if you need specific guidance

---

## Recognition

Contributors are recognized in the project:

- Your commits will appear in the repository history
- Significant contributions may be mentioned in release notes
- All contributors are valued members of the community

Thank you for contributing to Platelet-Movie! 🎬🩸
