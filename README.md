# Platelet-Movie

Discover Movies on Netflix that are long enough for a **Platelet Donation** (≥ 135 minutes).

Platelet donation typically takes 2–3 hours, so this CLI tool helps you find Netflix films that will keep you entertained throughout the entire process.

**🌐 [View the live GitHub Pages site](https://tegataiprime.github.io/Platelet-Movie/)** – Updated weekly with Lady Whistledown's commentary!

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
- 📄 **Multiple output formats**: Markdown (default), HTML, CSV, and JSON
- 🌍 Supports different Netflix regions (US, GB, CA, etc.)
- 🌙 **GitHub Pages site** with light/dark mode, runtime filter, sortable columns, and Lady Whistledown commentary
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
  --format [markdown|html|csv|json]
                               Output format for the movie list.  [default: markdown]
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

# Output as HTML table (useful for email reports)
platelet-movie --format html

# Output as CSV (useful for spreadsheets)
platelet-movie --format csv

# Output as JSON (useful for programmatic consumption)
platelet-movie --format json
```

#### Sample Output

Default (Markdown) format:
```
Netflix movies with a runtime 135-145 minutes:

   Runtime    Year   Score  Rated    Genres               Title
-----------------------------------------------------------------------------------------------
    135 m    2019     8.1  R        Crime, Drama         The Irishman
    138 m    2013     7.9  PG-13    Thriller, Drama      Prisoners
    140 m    1995     8.0  R        Drama, Crime         Heat
    142 m    2014     8.5  PG-13    Drama, Mystery       Interstellar
    145 m    2023     7.8  R        Action, Thriller     John Wick: Chapter 4
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

## GitHub Pages Site

The project includes a static website hosted on GitHub Pages that displays the weekly movie selections with Lady Whistledown's commentary.

**🌐 [Visit the live site](https://tegataiprime.github.io/Platelet-Movie/)**

### Features

- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Light/Dark Mode**: Toggle between themes with persistent preference storage
- **American Red Cross Branding**: Color scheme follows American Red Cross brand guidelines (#E42424 red)
- **Runtime Filter**: Filter movies by minimum (default: 90 min) and maximum (default: 160 min) runtime
- **Sortable Columns**: Click any column header to sort (all columns sortable, including genres); visual indicators show sort state (⇅ / ▲ / ▼)
- **Lady Whistledown Commentary**: AI-generated introduction in the style of Bridgerton
- **Acknowledgements**: Proper attribution for TMDB data, accuracy disclaimers, and Bridgerton credits

### Deployment

The site is automatically updated every **Friday at 8:00 PM UTC** (same schedule as the weekly email report) via GitHub Actions.

The workflow:
1. Generates fresh movie data using the `platelet-movie` CLI
2. Creates Lady Whistledown commentary using OpenAI
3. Builds a `data.json` file with all content
4. Deploys the static site to GitHub Pages

### Manual Deployment

You can manually trigger a deployment from the Actions tab:
1. Go to **Actions** → **Deploy GitHub Pages**
2. Click **Run workflow**

### Enabling GitHub Pages

**Note:** GitHub Pages is automatically configured when the repository becomes public. For private repositories, you may need to enable it manually:

1. Go to **Settings** → **Pages**
2. Under **Source**, select **GitHub Actions**
3. The site will be available at `https://tegataiprime.github.io/Platelet-Movie/`

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

The workflow runs every **Friday at 8:00 PM UTC** (4:00 PM EDT / 3:00 PM EST). You can also trigger it manually from the Actions tab.

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
| `poe generate` | Regenerate `site/data.json` with fresh movie data and Lady Whistledown commentary (fetches 50 pages by default) |
| `poe site` | Serve the static website locally for preview (port 8000) |

### Examples

```bash
# Run tests with coverage
poe test

# Lint
poe lint

# Format code
poe format

# Regenerate the website data (fetches fresh movies & generates commentary)
poe generate

# Regenerate with custom max-pages for faster testing (default: 50)
python scripts/generate_site_data.py --max-pages 5

# Preview the static site locally
poe site
# Then open http://localhost:8000 in your browser
# Works in GitHub Codespaces (port is auto-forwarded)
```

---

## Development

### Generating Site Data

The `scripts/generate_site_data.py` script fetches movie data from TMDB and generates Lady Whistledown commentary for the static website.

**Usage:**
```bash
# Generate with default settings (50 pages = ~1000 movies)
python scripts/generate_site_data.py

# Generate with custom max-pages for faster testing
python scripts/generate_site_data.py --max-pages 5

# Or use the Poe task (uses default 50 pages)
poe generate
```

**Options:**
- `--max-pages INTEGER`: Maximum number of TMDB result pages to fetch (default: 50, each page contains ~20 movies)

**Note:** Using a lower `--max-pages` value is recommended for faster end-to-end testing during development.

### Running Tests Manually

```bash
pytest tests/ -v --cov=platelet_movie --cov-report=term-missing
```

### Code Coverage

The project requires **≥ 80% code coverage** (enforced by CI) for both the `platelet_movie` package and the `scripts` directory.

All TMDB API interactions are tested by mocking the `requests.get` calls via `pytest-mock`. The Lady Whistledown commentary generator (`scripts/lady_whistledown.py`) is also tested with mocked OpenAI API calls and is included in coverage requirements.

### Continuous Integration

The project uses GitHub Actions to ensure code quality:

**Pull Request Testing** (`test-pr.yml`):
- Runs linting with Ruff (`poe lint`)
- Executes the full test suite with coverage (`poe test`)
- Enforces the 80% coverage threshold
- Triggers on: PR opened, synchronized, reopened, or marked ready for review

**Main Branch Testing** (`test-main.yml`):
- Runs linting and full test suite on every push to `main`
- Validates that merged code maintains quality standards
- Provides immediate feedback if issues slip through

**PR Movie Report Test** (`pr-movie-report-test.yml`):
- End-to-end functional test of the weekly movie report workflow
- Runs the full `platelet-movie` CLI with the same configuration as the weekly report
- Generates Lady Whistledown commentary using the OpenAI API
- Posts the complete report as a PR comment (instead of sending email)
- Validates that the entire movie discovery and reporting pipeline works correctly
- Triggers on: PR opened, synchronized, reopened

**GitHub Pages Deployment** (`deploy-github-pages.yml`):
- Automatically generates and deploys the static website
- Runs every Friday at 8:00 PM UTC (same schedule as the weekly email)
- Generates movie data, Lady Whistledown commentary, and builds `data.json`
- Deploys to GitHub Pages for public viewing
- Can be triggered manually from the Actions tab

**Multi-Device Docs Tester** (`.github/aw/multi-device-docs-tester.md`):
- GitHub Agentic Workflow for automated UI testing across devices
- Tests the static site on mobile, tablet, and desktop viewports
- Validates responsive design, accessibility, and interactive elements
- Runs daily on schedule or can be triggered manually
- Creates GitHub issues when problems are found

**Note:** To block PRs from being merged when tests fail, configure branch protection rules in repository settings to require the "Test Pull Request" workflow to pass before merging.

### Project Structure

```
Platelet-Movie/
├── .github/
│   └── workflows/
│       ├── weekly-movie-report.yml       # Weekly email report automation
│       ├── deploy-github-pages.yml       # GitHub Pages deployment
│       ├── pr-movie-report-test.yml      # E2E functional test for PRs
│       ├── test-pr.yml                   # PR testing (lint + coverage)
│       └── test-main.yml                 # Main branch testing
├── site/                                 # GitHub Pages static site
│   ├── index.html                        # Main HTML page
│   ├── styles.css                        # Styles with light/dark mode
│   ├── app.js                            # JavaScript for sorting & theme
│   └── data.json                         # Generated movie data
├── platelet_movie/
│   ├── __init__.py       # Package metadata
│   ├── cli.py            # Click-based CLI entry point
│   ├── tmdb_client.py    # TMDB API client
│   ├── config.py         # 12-Factor configuration (env vars)
│   ├── models.py         # Movie data model
│   └── formatters.py     # Output formatters (markdown, HTML, CSV, JSON)
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_tmdb_client.py
│   ├── test_config.py
│   ├── test_models.py
│   └── test_lady_whistledown.py
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

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Code of conduct
- Development setup
- Testing requirements
- Code style guidelines
- Pull request process

---

## Acknowledgements & Disclaimers

### 📊 Data Source

This product uses the [TMDB API](https://www.themoviedb.org/) but is not endorsed or certified by TMDB. Movie data, ratings, and Netflix availability information are provided by [The Movie Database (TMDB)](https://www.themoviedb.org/).

### ⚠️ Accuracy Disclaimer

Netflix availability and movie data may have a 24-48 hour lag from TMDB's updates. Regional availability varies, and content may be removed or added without notice. Always verify movie availability on Netflix before your donation appointment.

### ✍️ Commentary Attribution

"Lady Whistledown" commentary is AI-generated in the style of the character from *Bridgerton*, a Netflix series created by Chris Van Dusen and produced by Shondaland. *Bridgerton* is based on the novels by Julia Quinn. This is a parody/homage and is not affiliated with Netflix, Shondaland, or Julia Quinn.

### 🩸 About Platelet Donation

Platelet donation typically takes 2-3 hours and helps cancer patients, trauma victims, and surgical patients. Learn more about platelet donation at the [American Red Cross](https://www.redcross.org/give-blood/how-to-donate/types-of-blood-donations/platelet-donation.html).

### ⚠️ Red Cross Disclaimer

This project is not affiliated with, endorsed by, or connected to the American Red Cross or any other Red Cross organization. The use of the American Red Cross brand colors and references to platelet donation are for informational purposes only. All trademarks and brand elements belong to their respective owners.

---

## License

This project is licensed under the terms of the [MIT License](LICENSE).
