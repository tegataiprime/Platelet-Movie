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

## Setup

MCP servers are automatically configured in [.vscode/mcp.json](.vscode/mcp.json) and will be available after:

1. **Rebuilding the devcontainer** - Node.js (LTS) is configured in the devcontainer
2. **Setting environment variables**:
   - `GITHUB_TOKEN` - GitHub personal access token
   - `DOPPLER_TOKEN` - Doppler API token
   - `TMDB_API_KEY` - The Movie Database API key

## Environment Variables

Set these in your environment or through Doppler:

```bash
export GITHUB_TOKEN="your_github_token"
export DOPPLER_TOKEN="your_doppler_token"
export TMDB_API_KEY="your_tmdb_api_key"
```

Or use Doppler to manage all secrets:

```bash
doppler run -- code .
```

## MCP Servers Run Via npx

The GitHub, Playwright, Doppler, and TMDB MCP servers are run via `npx` with the `-y` flag to auto-install packages on demand. This means:

- No manual npm installation required
- Packages are cached after first use
- Always uses the latest version

## Troubleshooting

If MCP servers fail to start:

1. **Check Node.js is installed**: `node --version && npm --version`
2. **Verify environment variables are set**: `echo $GITHUB_TOKEN $DOPPLER_TOKEN $TMDB_API_KEY`
3. **Check GitHub CLI extension**: `gh extension list` (should show `gh-aw`)
4. **Rebuild devcontainer** if Node.js is missing

## References

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [GitHub MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [Doppler MCP Server](https://github.com/dopplerhq/mcp-server-doppler)
- [Playwright MCP Server](https://github.com/executeautomation/playwright-mcp-server)
- [TMDB MCP Server](https://github.com/Laksh-star/mcp-server-tmdb)
