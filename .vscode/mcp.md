# MCP Server Configuration

This project includes Model Context Protocol (MCP) servers for enhanced development capabilities.

## Configured Servers

### 1. GitHub Agentic Workflows
- **Command**: `gh aw mcp-server`
- **Purpose**: Provides agentic workflow capabilities for GitHub operations
- **Prerequisites**: GitHub CLI with `gh-aw` extension installed

### 2. GitHub
- **Package**: `@modelcontextprotocol/server-github`
- **Purpose**: General GitHub API access through MCP
- **Environment**: Requires `GITHUB_TOKEN` environment variable
- **Prerequisites**: Node.js/npm

### 3. Playwright
- **Package**: `@executeautomation/playwright-mcp-server`
- **Purpose**: Browser automation and testing through MCP
- **Prerequisites**: Node.js/npm

### 4. Doppler
- **Package**: `@dopplerhq/mcp-server-doppler`
- **Purpose**: Secrets management through Doppler
- **Environment**: Requires `DOPPLER_TOKEN` environment variable
- **Prerequisites**: Node.js/npm

### 5. TMDB (The Movie Database)
- **Package**: `mcp-server-tmdb`
- **Purpose**: Search movies, TV shows, get recommendations, streaming availability, cast/crew details
- **Environment**: Requires `TMDB_API_KEY` environment variable
- **Prerequisites**: Node.js/npm
- **Features**:
  - Search movies and TV shows
  - Get trending content (daily/weekly)
  - Search by genre or keyword
  - Advanced filtering (genre, year, rating, runtime)
  - Get movie details (cast, crew, reviews)
  - Find streaming providers by region
  - Get recommendations and similar movies

### 6. SonarQube (SonarCloud)
- **Docker Image**: `mcp/sonarqube`
- **Purpose**: Code quality and security analysis through SonarCloud
- **Environment**: Requires `SONAR_TOKEN` environment variable
- **Prerequisites**: Docker
- **Configuration**:
  - Organization: `tegataiprime`
  - Cloud URL: `https://sonarcloud.io`
  - IDE Port: `64120`
- **Features**:
  - Analyze files for code quality issues
  - List potential security vulnerabilities
  - Setup connected mode for IDE integration
  - Exclude files from analysis

## Setup

MCP servers are automatically configured in [.vscode/mcp.json](.vscode/mcp.json) and will be available after:

1. **Rebuilding the devcontainer** - Node.js (LTS) and Docker CLI are configured in the devcontainer
   - Docker socket is mounted from Codespaces host
   - Docker CLI is installed via post-create script
2. **Setting environment variables**:
   - `GITHUB_TOKEN` - GitHub personal access token
   - `DOPPLER_TOKEN` - Doppler API token
   - `TMDB_API_KEY` - The Movie Database API key
   - `SONAR_TOKEN` - SonarCloud authentication token

## Environment Variables

Set these in your environment or through Doppler:

```bash
export GITHUB_TOKEN="your_github_token"
export DOPPLER_TOKEN="your_doppler_token"
export TMDB_API_KEY="your_tmdb_api_key"
export SONAR_TOKEN="your_sonar_token"
```

Or use Doppler to manage all secrets:

```bash
doppler run -- code .
```

## MCP Servers Run Via npx and Docker

**npx-based servers** (GitHub, Playwright, Doppler, TMDB):
- Run via `npx` with the `-y` flag to auto-install packages on demand
- No manual npm installation required
- Packages are cached after first use
- Always uses the latest version

**Docker-based servers** (SonarQube):
- Run via Docker containers
- Uses host Docker socket mounted at `/var/run/docker.sock`
- Docker CLI installed during container creation
- Configured with environment variables passed to the container

## Troubleshooting

If MCP servers fail to start:

1. **Check Node.js is installed**: `node --version && npm --version`
2. **Check Docker is available**: `docker --version` (for SonarQube server)
3. **Check Docker daemon is running**: `docker ps` (should not error)
4. **Verify environment variables are set**: `echo $GITHUB_TOKEN $DOPPLER_TOKEN $TMDB_API_KEY $SONAR_TOKEN`
5. **Check GitHub CLI extension**: `gh extension list` (should show `gh-aw`)
6. **Verify Docker image is available**: `docker images | grep mcp/sonarqube`
7. **Rebuild devcontainer** to apply Docker socket mount and install Docker CLI if just added

## References

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [GitHub MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [Doppler MCP Server](https://github.com/dopplerhq/mcp-server-doppler)
- [Playwright MCP Server](https://github.com/executeautomation/playwright-mcp-server)
- [TMDB MCP Server](https://github.com/Laksh-star/mcp-server-tmdb)
- [SonarQube MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/sonarqube)
