# Platelet-Movie

Discover Movies on Netflix that are long enough for a **Platelet Donation** (≥ 135 minutes).

Platelet donation typically takes 2–3 hours, so this CLI tool helps you find Netflix films that will keep you entertained throughout the entire process.

---

## Features

- 🎬 Queries the Netflix catalog via the [uNoGS RapidAPI](https://rapidapi.com/unogs/api/unogs/) endpoint
- 🔐 Authenticates with your Netflix account credentials (stored as environment variables – [12-Factor App](https://12factor.net/config))
- ⏱️ Filters movies whose runtime is **≥ a configurable number of minutes** (default: **135**)
- 📋 Returns results **sorted ascending** by runtime, then by title
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

This installs all runtime **and** development dependencies (pytest, ruff, etc.) into an isolated virtual environment.

### 3. Activate the virtual environment (optional)

```bash
poetry shell
```

---

## Configuration (Environment Variables)

Platelet-Movie follows the [12-Factor App](https://12factor.net/config) methodology – all secrets and service URLs are read from **environment variables**.

| Variable | Required | Description |
|----------|----------|-------------|
| `NETFLIX_EMAIL` | ✅ | Your Netflix account e-mail address |
| `NETFLIX_PASSWORD` | ✅ | Your Netflix account password |
| `NETFLIX_API_KEY` | ✅ | Your [RapidAPI](https://rapidapi.com/) key for the uNoGS endpoint |
| `NETFLIX_API_HOST` | ❌ | uNoGS API host (default: `unogs-unogs-v1.p.rapidapi.com`) |

### Setting environment variables

**Linux / macOS:**

```bash
export NETFLIX_EMAIL="your@email.com"
export NETFLIX_PASSWORD="yourpassword"
export NETFLIX_API_KEY="your-rapidapi-key"
```

**Windows (PowerShell):**

```powershell
$env:NETFLIX_EMAIL = "your@email.com"
$env:NETFLIX_PASSWORD = "yourpassword"
$env:NETFLIX_API_KEY = "your-rapidapi-key"
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

  Queries Netflix for movies with a runtime >= MIN_MINUTES (default: 135)
  and prints the results sorted by runtime then title, ascending.

Options:
  --min-minutes INTEGER RANGE  Minimum movie runtime in minutes.  [default: 135; x>=0]
  --email TEXT                 Netflix account e-mail (overrides NETFLIX_EMAIL env var).
  --password TEXT              Netflix account password (overrides NETFLIX_PASSWORD env var).
  --api-key TEXT               Netflix search API key (overrides NETFLIX_API_KEY env var).
  --api-host TEXT              Netflix search API host (overrides NETFLIX_API_HOST env var).
  --version                    Show the version and exit.
  --help                       Show this message and exit.
```

### Example

```bash
# Use the default 135-minute minimum
platelet-movie

# Use a custom minimum runtime
platelet-movie --min-minutes 120

# Override credentials inline
platelet-movie --email user@example.com --password secret --api-key mykey
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

The project requires **≥ 80% code coverage**. The current coverage is **100%**.

### Project Structure

```
Platelet-Movie/
├── platelet_movie/
│   ├── __init__.py     # Package metadata
│   ├── cli.py          # Click-based CLI entry point
│   ├── auth.py         # Netflix credential management
│   ├── client.py       # Netflix API HTTP client
│   ├── config.py       # 12-Factor configuration (env vars)
│   └── models.py       # Movie data model
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_cli.py
│   ├── test_client.py
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
3. **Config** – stored in environment variables (`NETFLIX_EMAIL`, `NETFLIX_PASSWORD`, `NETFLIX_API_KEY`, `NETFLIX_API_HOST`)
4. **Processes** – stateless CLI process; no shared state

---

## Obtaining a RapidAPI Key

1. Create a free account at [RapidAPI](https://rapidapi.com/)
2. Subscribe to the [uNoGS – Unofficial Netflix Online Global Search](https://rapidapi.com/unogs/api/unogs/) API
3. Copy your **X-RapidAPI-Key** and export it as `NETFLIX_API_KEY`

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).
