---
name: Multi-Device Site Tester

description: Tests a static web site site for responsive layout issues, accessibility problems, and broken interactions across mobile, tablet, and desktop device form factors

on:
  schedule: daily
  pull_request:
    paths:
      - 'site/**'
  workflow_dispatch:
    inputs:
      devices:
        description: 'Device types to test (comma-separated: mobile,tablet,desktop)'
        required: false
        default: 'mobile,tablet,desktop'
      docs_dir:
        description: 'Directory containing the static site (relative to repository root)'
        required: false
        default: 'site'
      build_command:
        description: 'Command to build the static site (empty if pre-generated)'
        required: false
        default: ''
      serve_command:
        description: 'Command to serve the static site'
        required: false
        default: 'npx serve -l'
      server_port:
        description: 'Port the static site server listens on'
        required: false
        default: '4321'

permissions:
  contents: read
  issues: read
  pull-requests: read

tracker-id: daily-multi-device-site-tester

engine:
  id: copilot

timeout-minutes: 30

network:
  allowed:
    - defaults
    - node

tools:
  playwright:
    version: "v1.56.1"
  bash:
    - "npx serve*"  # Serve static files
    - "npx http-server*"  # Alternative static server
    - "curl*"       # Health checks
    - "kill*"       # Cleanup
    - "lsof*"       # Find server process
    - "ls*"         # List files
    - "pwd*"        # Print working directory
    - "cat*"        # View file contents
    - "echo*"       # Debug output
    - "sleep*"      # Wait for server
safe-outputs:
  upload-asset:
  create-issue:
    expires: 2d
    labels: [documentation, testing]
---

# Multi-Device Site Testing

You are a site testing specialist. Your task is to build the project's static site and test it across multiple device form factors to catch responsive design issues, accessibility problems, and broken interactions before they reach users.

## Context

- **Repository**: ${{ github.repository }}
- **Run ID**: ${{ github.run_id }}
- **Triggered by**: @${{ github.actor }}
- **Devices to test** (DEVICES): ${{ inputs.devices }} (default: 'mobile,tablet,desktop')
- **Site directory** (SITE_DIR): ${{ inputs.docs_dir }} (default: 'site' )
- **Build command** (BUILD_COMMAND): ${{ inputs.build_command }} (default '' )
- **Serve command** (SERVE_COMMAND): ${{ inputs.serve_command }} (default 'npx serve -l')
- **Server port** (SERVER_PORT): ${{ inputs.server_port }} (default '4321')
- **Working directory**: ${{ github.workspace }}

## Step 1: Verify the Static Site Exists

Check that the site directory exists and contains an index.html file. This indicates that there is a static site to test:

```bash
ls -la ${{ github.workspace }}/SITE_DIR/
cat ${{ github.workspace }}/SITE_DIR/index.html 2>/dev/null | head -20 || echo "No index.html found"
```

If the site directory doesn't exist or has no index.html, call the `noop` safe output explaining that this repository doesn't have a buildable static site and stop.

## Step 2: Start the Preview Server

Start the preview server in the background and wait for it to be ready:

```bash
cd ${{ github.workspace }}/SITE_DIR
# Default command: npx serve -l SERVER_PORT SITE_DIR
SERVE_COMMAND SERVER_PORT > /tmp/docs-preview.log 2>&1 &
echo $! > /tmp/docs-server.pid
echo "Server started with PID: $(cat /tmp/docs-server.pid)"
```

Wait for the server to be ready:

```bash
PORT=SERVER_PORT
for i in {1..30}; do
  curl -s http://localhost:$PORT > /dev/null && echo "Server ready on port $PORT!" && break
  echo "Waiting for server... ($i/30)" && sleep 2
done
curl -s http://localhost:$PORT > /dev/null || echo "WARNING: Server may not have started properly"
```

## Step 3: Device Configuration

Use these viewport sizes based on the `DEVICES` input:

**Mobile devices** (test if "mobile" in input):
- iPhone 12: 390×844
- Pixel 5: 393×851
- Galaxy S21: 360×800

**Tablet devices** (test if "tablet" in input):
- iPad: 768×1024
- iPad Pro 11": 834×1194

**Desktop devices** (test if "desktop" in input):
- HD: 1366×768
- FHD: 1920×1080

## Step 4: Run Playwright Tests

**IMPORTANT: Use Playwright via MCP tools only — do NOT install or require Playwright as an npm package.**

Use Playwright MCP tools (e.g., `mcp__playwright__browser_navigate`, `mcp__playwright__browser_run_code`, `mcp__playwright__browser_snapshot`) to test the documentation site.

For **each device viewport** in the requested device types, perform the following checks:

```javascript
// Example: set viewport, navigate, snapshot
mcp__playwright__browser_run_code({
  code: `async (page) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('http://localhost:SERVER_PORT/');
    return { url: page.url(), title: await page.title() };
  }`
})
```

For each device, check:
1. **Page loads** successfully (no 404, 500 errors)
2. **Navigation** is usable (menu accessible, links work)
3. **Content** is readable without horizontal scrolling
4. **Images** are properly sized and not overflowing
5. **Interactive elements** (search, buttons, tabs) are reachable and tappable
6. **Text** is not truncated or overlapping
7. **Accessibility** basics: headings present, alt text on images, sufficient contrast

Take screenshots on failure for evidence. Use `upload-asset` safe output to store screenshots.

## Step 5: Analyze Results

Categorize findings by severity:
- 🔴 **Critical**: Blocks navigation or makes content unreadable
- 🟡 **Warning**: Layout issues that degrade experience but don't block content
- 🟢 **Passed**: Device renders correctly

## Step 6: Stop the Preview Server

Always clean up when done:

```bash
kill $(cat /tmp/docs-server.pid) 2>/dev/null || true
rm -f /tmp/docs-server.pid /tmp/docs-preview.log
echo "Server stopped"
```

## Step 8: Report Results

### If NO Issues Found

Call the `noop` safe output to log completion:

```json
{
  "noop": {
    "message": "Multi-device documentation testing complete. All devices tested successfully with no issues found."
  }
}
```

**You MUST invoke the noop tool — do not just write this message as text.**

### If Issues ARE Found

Create a GitHub issue titled "📱 Multi-Device Docs Testing Report - [Date]" with:

```markdown
### Test Summary
- Triggered by: @${{ github.actor }}
- Workflow run: [§${{ github.run_id }}](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})
- Devices tested: {count}
- Test date: {date}

### Results Overview
- 🟢 Passed: {count}
- 🟡 Warnings: {count}
- 🔴 Critical: {count}

### Critical Issues
[List issues that block functionality or readability — keep visible]

<details>
<summary><b>View All Warnings</b></summary>

[Minor layout and UX issues with device names and details]

</details>

<details>
<summary><b>View Detailed Test Results by Device</b></summary>

#### Mobile Devices
[Test results per device]

#### Tablet Devices
[Test results per device]

#### Desktop Devices
[Test results per device]

</details>

### Accessibility Findings
[Key accessibility issues — keep visible as they are important]

### Recommendations
[Actionable steps to fix the issues found]
```

**Important**: If no action is needed after completing your analysis, you **MUST** call the `noop` safe-output tool with a brief explanation. Failing to call any safe-output tool is the most common cause of workflow failures.

```json
{"noop": {"message": "No action needed: [brief explanation of what was analyzed and why no action was required]"}}
```