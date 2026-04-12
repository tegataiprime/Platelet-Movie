# Platelet-Movie

Discover Movies on Netflix that are long enough for a **Platelet Donation** (≥ 135 minutes).

Platelet donation typically takes 2–3 hours, so this CLI tool helps you find Netflix films that will keep you entertained throughout the entire process.

---

## How it works

Platelet-Movie uses the **TMDB (The Movie Database) API** to:

1. Query movies available on Netflix in your region
2. Filter by runtime (≥ a configurable minimum, default **135 minutes**)
3. Return sorted results by runtime, then title

TMDB provides reliable watch provider data (including Netflix availability) that is updated regularly. This approach is faster and more reliable than web scraping.

---

## Features

- 🎬 Uses the free TMDB API – no web scraping required
- 🔐 Only requires a free TMDB API key (no Netflix credentials needed)
- ⏱️ Filters movies by runtime range (min/max configurable, default: **135-145 minutes**)
- 🌐 Filter by original language (ISO 639-1 codes, default: **English**)
- ⭐ Shows **TMDB score**, **MPAA rating** (R, PG-13, etc.), and **genres** for each movie
- 📋 Returns results **sorted ascending** by runtime, then by title
- 🌍 Supports different Netflix regions (US, GB, CA, etc.)
- 🐍 Written in Python 3.11+, managed with [Poetry](https://python-poetry.org/) and task-automated with [Poe the Poet](https://poethepoet.natn.io/)

---

## Requirements

| Tool | Version |
|------|---------|
| Python | ≥ 3.11 |
| Poetry | ≥ 2.0 |
| Poe the Poet | ≥ 0.32 |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/tegataiprime/Platelet-Movie.git
cd Platelet-Movie
```

### 2. Install dependencies with Poetry

```bash
poetry install
```

### 3. Get a free TMDB API key

1. Create a free account at [themoviedb.org](https://www.themoviedb.org/signup)
2. Go to [Settings → API](https://www.themoviedb.org/settings/api)
3. Request an API key (it's free for personal use)

### 4. Activate the virtual environment (optional)

```bash
poetry shell
```

---

## Configuration (Environment Variables)

Platelet-Movie follows the [12-Factor App](https://12factor.net/config) methodology – all settings are read from **environment variables**.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TMDB_API_KEY` | ✅ | – | Your TMDB API key (v3 auth) |
| `TMDB_REGION` | ❌ | `US` | Netflix region code (ISO 3166-1 alpha-2, e.g., US, GB, CA) |
| `TMDB_MAX_PAGES` | ❌ | `10` | Maximum number of TMDB result pages to fetch (20 movies per page) |

### Setting environment variables

**Linux / macOS:**

```bash
export TMDB_API_KEY="your_api_key_here"
export TMDB_REGION="US"
```

**Windows (PowerShell):**

```powershell
$env:TMDB_API_KEY = "your_api_key_here"
$env:TMDB_REGION = "US"
```

You can also use a `.env` file with a tool like [direnv](https://direnv.net/).

> **Note:** The `.env` file is listed in `.gitignore` and should **never** be committed to source control.

---

## Usage

### Running via Poetry

```bash
poetry run platelet-movie
```

### Running directly (with the virtual environment active)

```bash
platelet-movie
```

### Options

```
Usage: platelet-movie [OPTIONS]

  Discover Netflix movies long enough for a Platelet Donation.

Options:
  --min-minutes INTEGER RANGE  Minimum movie runtime in minutes.  [default: 135; x>=0]
  --max-minutes INTEGER RANGE  Maximum movie runtime in minutes.  [default: 145; x>=1]
  --language TEXT              Original language filter (ISO 639-1 code).  [default: en]
  --max-pages INTEGER          Max result pages to fetch (20 movies/page). [default: 10]
  --api-key TEXT               TMDB API key (overrides TMDB_API_KEY env var).
  --region TEXT                Netflix region code (e.g., US, GB). Default: US.
  -v, --verbose                Enable verbose debug logging to stderr.
  --version                    Show the version and exit.
  --help                       Show this message and exit.
```

### Example

```bash
# Use the default runtime range (135-145 minutes) for US Netflix
platelet-movie

# Lower the threshold
platelet-movie --min-minutes 120

# Set a runtime range (e.g., 135-180 minutes)
platelet-movie --min-minutes 135 --max-minutes 180

# Search for Spanish-language movies
platelet-movie --language es

# Combine filters: French movies between 140-200 minutes
platelet-movie --language fr --min-minutes 140 --max-minutes 200

# Enable verbose debug logging to see API calls
platelet-movie --verbose

# Search Netflix UK catalog
platelet-movie --region GB

# Fetch more results (default: 10 pages = 200 movies)
platelet-movie --max-pages 20

# Pass API key directly (not recommended for production)
platelet-movie --api-key your_key_here
```

#### Sample Output

```
Netflix movies with a runtime 135-145 minutes:

   Runtime   Score  Rated    Genres               Title
-------------------------------------------------------------------------------------
    135 m     8.1  R        Crime, Drama         The Irishman
    138 m     7.9  PG-13    Thriller, Drama      Prisoners
    140 m     8.0  R        Drama, Crime         Heat
    142 m     8.5  PG-13    Drama, Mystery       Interstellar
    145 m     7.8  R        Action, Thriller     John Wick: Chapter 4
```

---

## API Rate Limits

TMDB has generous rate limits for their free API tier:

- **40 requests per 10 seconds**
- No daily limit for reasonable usage

For typical usage (discovering movies), you won't hit these limits. If you do, the tool will display a clear error message.

---

## Troubleshooting

### "Missing required environment variable: TMDB_API_KEY"

You need to set your TMDB API key. Get a free one at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api).

### "Invalid API key"

Double-check that your API key is correct and is a v3 auth key (not v4).

### "No movies found"

- Netflix catalog varies by region. Try a different `--region`.
- The TMDB watch providers data may have a 24-48 hour lag.
- Try lowering `--min-minutes` to see if shorter movies are available.

---

## Automated Weekly Email Report

A GitHub Actions workflow automatically runs `platelet-movie` weekly and emails the results to subscribers with a witty Lady Whistledown-style introduction.

### Setup

1. **Configure repository secrets** (Settings → Secrets and variables → Actions):

   | Secret | Required | Description |
   |--------|----------|-------------|
   | `TMDB_API_KEY` | ✅ | Your TMDB API key |
   | `PLATELET_MOVIE_SUBSCRIBERS` | ✅ | Comma-separated email addresses |
   | `MAIL_SERVER` | ✅ | SMTP server (e.g., `smtp.gmail.com`) |
   | `MAIL_PORT` | ❌ | SMTP port (default: `587`) |
   | `MAIL_USERNAME` | ✅ | SMTP username/email |
   | `MAIL_PASSWORD` | ✅ | SMTP password or app password |
   | `MAIL_FROM` | ❌ | From address (default: `MAIL_USERNAME`) |
   | `OPENAI_API_KEY` | ❌ | OpenAI API key for Lady Whistledown commentary (optional) |

2. **Configure repository variables** (optional):

   | Variable | Default | Description |
   |----------|---------|-------------|
   | `TMDB_REGION` | `US` | Netflix region code |

### Schedule

The workflow runs every **Friday at 8:00 PM US Eastern Time** (midnight UTC Saturday). You can also trigger it manually from the Actions tab.

### Lady Whistledown Commentary

The weekly email includes an AI-generated introduction written in the style of Lady Whistledown from Bridgerton. This feature requires an OpenAI API key (`OPENAI_API_KEY` secret). If the API key is not configured, the workflow will use a charming fallback message instead.

### Gmail Setup

For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833):
- `MAIL_SERVER`: `smtp.gmail.com`
- `MAIL_PORT`: `587`
- `MAIL_USERNAME`: your Gmail address
- `MAIL_PASSWORD`: your 16-character App Password

---

## Poe the Poet Tasks

All common developer tasks are available via [Poe the Poet](https://poethepoet.natn.io/):

| Command | Description |
|---------|-------------|
| `poe test` | Run the full test suite with coverage (≥ 80% required) |
| `poe lint` | Lint source code and tests with Ruff |
| `poe format` | Auto-format source code and tests with Ruff |
| `poe run` | Run the CLI (`platelet-movie`) |

### Examples

```bash
# Run tests with coverage
poe test

# Lint
poe lint

# Format code
poe format
```

---

## Development

### Running Tests Manually

```bash
pytest tests/ -v --cov=platelet_movie --cov-report=term-missing
```

### Code Coverage

The project requires **≥ 80% code coverage** (enforced by CI).

All TMDB API interactions are tested by mocking the `requests.get` calls via `pytest-mock`.

### Continuous Integration

All pull requests automatically trigger a GitHub Actions workflow that:
- Runs linting with Ruff (`poe lint`)
- Executes the full test suite with coverage (`poe test`)
- Enforces the 80% coverage threshold

The workflow runs on:
- New PR creation
- New commits pushed to the PR
- PR reopened
- Draft PR marked as ready for review

**Note:** To block PRs from being merged when tests fail, configure branch protection rules in repository settings to require the "Test Pull Request" workflow to pass before merging.

### Project Structure

```
Platelet-Movie/
├── platelet_movie/
│   ├── __init__.py       # Package metadata
│   ├── cli.py            # Click-based CLI entry point
│   ├── tmdb_client.py    # TMDB API client
│   ├── config.py         # 12-Factor configuration (env vars)
│   └── models.py         # Movie data model
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_tmdb_client.py
│   ├── test_config.py
│   └── test_models.py
├── scripts/
│   └── lady_whistledown.py  # OpenAI-powered commentary generator
├── pyproject.toml        # Poetry + Poe tasks + Ruff config
├── poetry.lock
└── README.md
```

### Architecture

Platelet-Movie is designed as a **12-Factor Application**:

1. **Codebase** – single repository, tracked in git
2. **Dependencies** – all declared in `pyproject.toml`, managed by Poetry
3. **Config** – stored in environment variables (`TMDB_API_KEY`, `TMDB_REGION`)
4. **Processes** – stateless CLI process; no shared state

#### Data Flow

```
CLI (cli.py)
  │
  └─► Config (config.py)          ← environment variables
        │
        └─► TMDBClient (tmdb_client.py)
              │
              ├─► TMDB /discover/movie API
              │      └─► Filter by Netflix provider
              │
              ├─► TMDB /movie/{id} API
              │      └─► Get runtime
              │
              ├─► TMDB /movie/{id}/watch/providers API
              │      └─► Verify Netflix availability in region
              │
              └─► [Movie]  →  sorted list  →  CLI output
```

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).
