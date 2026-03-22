# Platelet-Movie

Discover Movies on Netflix that are long enough for a **Platelet Donation** (≥ 135 minutes).

Platelet donation typically takes 2–3 hours, so this CLI tool helps you find Netflix films that will keep you entertained throughout the entire process.

---

## How it works

Platelet-Movie uses a **real Chromium browser** (via [Playwright](https://playwright.dev/python/)) to:

1. Log in to Netflix with your own account credentials
2. Browse the Netflix movies catalog (`/browse/genre/34399`)
3. Visit individual title pages to read each film's runtime
4. Return all movies whose runtime is ≥ a configurable minimum (default **135 minutes**)

Because the scraper drives a genuine browser session, Netflix sees it as a normal user – not a bot.
Configurable rate-limiting (random delay between page loads, session size cap) keeps the account safe.

---

## Features

- 🎬 Scrapes the Netflix catalog directly – no third-party API required
- 🔐 Authenticates with your Netflix account credentials (stored as environment variables – [12-Factor App](https://12factor.net/config))
- ⏱️ Filters movies whose runtime is **≥ a configurable number of minutes** (default: **135**)
- 📋 Returns results **sorted ascending** by runtime, then by title
- 🛡️ Built-in rate-limiting and anti-lockout safeguards
- 🐍 Written in Python 3.11+, managed with [Poetry](https://python-poetry.org/) and task-automated with [Poe the Poet](https://poethepoet.natn.io/)

---

## Requirements

| Tool | Version |
|------|---------|
| Python | ≥ 3.11 |
| Poetry | ≥ 2.0 |
| Poe the Poet | ≥ 0.32 |
| Chromium | installed via `poe install-browsers` |

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

### 3. Install the Playwright browser

```bash
poe install-browsers
```

This downloads Chromium into the Playwright browser cache. It only needs to be run once.

### 4. Activate the virtual environment (optional)

```bash
poetry shell
```

---

## Configuration (Environment Variables)

Platelet-Movie follows the [12-Factor App](https://12factor.net/config) methodology – all secrets and tuning parameters are read from **environment variables**.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NETFLIX_EMAIL` | ✅ | – | Your Netflix account e-mail address |
| `NETFLIX_PASSWORD` | ✅ | – | Your Netflix account password |
| `NETFLIX_HEADLESS` | ❌ | `true` | Set to `false` to show the browser window |
| `NETFLIX_REQUEST_DELAY_S` | ❌ | `2.0` | Seconds between page loads (rate-limiting) |
| `NETFLIX_PAGE_TIMEOUT_MS` | ❌ | `30000` | Page load timeout in milliseconds |
| `NETFLIX_MAX_MOVIES` | ❌ | `100` | Maximum movie detail pages per session |

### Setting environment variables

**Linux / macOS:**

```bash
export NETFLIX_EMAIL="your@email.com"
export NETFLIX_PASSWORD="yourpassword"
```

**Windows (PowerShell):**

```powershell
$env:NETFLIX_EMAIL = "your@email.com"
$env:NETFLIX_PASSWORD = "yourpassword"
```

You can also use a `.env` file with a tool like [direnv](https://direnv.net/).

> **Note:** The `.env` file is listed in `.gitignore` and should **never** be committed to source control.

---

## Rate-Limiting & Anti-Lockout Safeguards

Platelet-Movie is designed to be a polite scraper:

| Safeguard | Detail |
|-----------|--------|
| **Random delay** | Each page load is followed by `NETFLIX_REQUEST_DELAY_S` seconds + up to 50 % random jitter |
| **Session cap** | No more than `NETFLIX_MAX_MOVIES` title pages are visited per run |
| **Realistic browser** | Full Chromium session with a standard desktop viewport and user-agent |
| **Graceful skip** | Pages that fail to load are silently skipped rather than retried aggressively |
| **Headless by default** | Runs invisibly; use `--no-headless` to watch the browser for debugging |

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
  --email TEXT                 Netflix account e-mail (overrides NETFLIX_EMAIL env var).
  --password TEXT              Netflix account password (overrides NETFLIX_PASSWORD env var).
  --no-headless                Show the browser window (useful for debugging login issues).
  --request-delay FLOAT        Seconds to wait between page loads (default: 2.0).
  --max-movies INTEGER         Maximum number of movies to inspect per session (default: 100).
  --version                    Show the version and exit.
  --help                       Show this message and exit.
```

### Example

```bash
# Use the default 135-minute minimum (headless by default)
platelet-movie

# Lower the threshold and watch the browser for debugging
platelet-movie --min-minutes 120 --no-headless

# Throttle more gently to reduce load on Netflix
platelet-movie --request-delay 4.0 --max-movies 50
```

#### Sample Output

```
Netflix movies with a runtime >= 135 minutes:

   Runtime  Title
------------------------------------------------------------
    135 m  The Irishman
    148 m  Inception
    169 m  The Dark Knight
    180 m  Avengers: Endgame
    195 m  Lawrence of Arabia
```

---

## Poe the Poet Tasks

All common developer tasks are available via [Poe the Poet](https://poethepoet.natn.io/):

| Command | Description |
|---------|-------------|
| `poe test` | Run the full test suite with coverage (≥ 80% required) |
| `poe lint` | Lint source code and tests with Ruff |
| `poe format` | Auto-format source code and tests with Ruff |
| `poe run` | Run the CLI (`platelet-movie`) |
| `poe install-browsers` | Download the Playwright Chromium browser |

### Examples

```bash
# Run tests with coverage
poe test

# Lint
poe lint

# Format code
poe format

# Install Playwright browser (first-time setup)
poe install-browsers
```

---

## Development

### Running Tests Manually

```bash
pytest tests/ -v --cov=platelet_movie --cov-report=term-missing
```

### Code Coverage

The project requires **≥ 80% code coverage**. The current coverage is **100%**.

All Playwright browser interactions are tested by mocking the `sync_playwright` context manager
and `Page` objects via `unittest.mock`.

### Project Structure

```
Platelet-Movie/
├── platelet_movie/
│   ├── __init__.py     # Package metadata
│   ├── cli.py          # Click-based CLI entry point
│   ├── auth.py         # Netflix login via Playwright
│   ├── scraper.py      # Playwright-based movie scraper
│   ├── config.py       # 12-Factor configuration (env vars)
│   └── models.py       # Movie data model
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_cli.py
│   ├── test_scraper.py
│   ├── test_config.py
│   └── test_models.py
├── pyproject.toml      # Poetry + Poe tasks + Ruff config
├── poetry.lock
└── README.md
```

### Architecture

Platelet-Movie is designed as a **12-Factor Application**:

1. **Codebase** – single repository, tracked in git
2. **Dependencies** – all declared in `pyproject.toml`, managed by Poetry
3. **Config** – stored in environment variables (`NETFLIX_EMAIL`, `NETFLIX_PASSWORD`, etc.)
4. **Processes** – stateless CLI process; no shared state

#### Data Flow

```
CLI (cli.py)
  │
  └─► Config (config.py)          ← environment variables
        │
        ├─► NetflixAuth (auth.py)     ← performs Playwright login
        │
        └─► NetflixScraper (scraper.py)
              │
              ├─► Playwright Chromium browser
              │      ├─► https://www.netflix.com/login
              │      ├─► https://www.netflix.com/browse/genre/34399
              │      └─► https://www.netflix.com/title/{id}  (per movie)
              │
              └─► [Movie]  →  sorted list  →  CLI output
```

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).
