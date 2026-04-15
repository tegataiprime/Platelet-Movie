---
name: Multi-Device Web Site Tester
description: Tests the generated static site functionality and responsive design across multiple device form factors
on:
  pull_request:
    paths:
      - 'site/**'
  workflow_dispatch:
    inputs:
      devices:
        description: 'Device types to test (comma-separated: mobile,tablet,desktop)'
        required: false
        default: 'mobile,tablet,desktop'
permissions:
  contents: read
  issues: read
  pull-requests: read
tracker-id: multi-device-docs-tester
engine:
  id: copilot
strict: true
timeout-minutes: 30
tools:
  playwright:
    version: "v1.56.1"
  bash:
    - "ls*"      # List files for directory navigation
    - "pwd*"     # Print working directory
    - "cd*"      # Change directory
    - "cat*"     # View file contents
safe-outputs:
  upload-asset:
  create-issue:
    expires: 2d
    labels: [multi-device-testing]
---

# Multi-Device Web Site Testing

You are a web user interface testing specialist. Your task is to comprehensively test the generated static site across multiple devices and form factors.

## Context

- Repository: ${{ github.repository }}
- Triggered by: @${{ github.actor }}
- Devices to test: ${{ inputs.devices }}
- Working directory: ${{ github.workspace }}

**IMPORTANT SETUP NOTES:**
1. You're already in the repository root
2. The site folder is at: `${{ github.workspace }}/site`
3. **Use `file://` URLs with Playwright** - No HTTP server needed
4. Keep token usage low by being efficient with your code and minimizing iterations
5. **Playwright is available via MCP tools only** - do NOT try to `require('playwright')` or install it via npm

## Your Mission

Test the static generated web site across multiple devices and form factors using Playwright's `file://` protocol. Test layout responsiveness, accessibility, interactive elements, and visual rendering across all device types. Use a single Playwright browser instance for efficiency.

**Note**: The site is completely static (HTML/CSS/JS + data.json) and can be tested directly via `file://` URLs without needing an HTTP server.

## Step 1: Prepare File URL

Playwright can navigate directly to local files using the `file://` protocol:

```bash
# Get the absolute path to the site directory
cd ${{ github.workspace }}
SITE_PATH="$(pwd)/site"
echo "Site path: $SITE_PATH"
echo "File URL: file://$SITE_PATH/index.html"
```

The site will be tested at: `file://${{ github.workspace }}/site/index.html`

## Step 2: Device Configuration

Test these device types based on input `${{ inputs.devices }}`:

**Mobile:** iPhone 12 (390x844), iPhone 12 Pro Max (428x926), Pixel 5 (393x851), Galaxy S21 (360x800)
**Tablet:** iPad (768x1024), iPad Pro 11 (834x1194), iPad Pro 12.9 (1024x1366)
**Desktop:** HD (1366x768), FHD (1920x1080), 4K (2560x1440)

## Step 3: Run Playwright Tests

**IMPORTANT: Using Playwright in gh-aw Workflows**

Playwright is provided through an MCP server interface, **NOT** as an npm package. You must use the MCP Playwright tools:

- ✅ **Correct**: Use MCP tools like `mcp__playwright__browser_navigate`, `mcp__playwright__browser_run_code`, etc.
- ❌ **Incorrect**: Do NOT try to `require('playwright')` or create standalone Node.js scripts
- ❌ **Incorrect**: Do NOT install playwright via npm - it's already available through MCP

**Example Usage:**

```javascript
// Use Playwright MCP tools to navigate and test
// Example: Navigate to the local file
mcp__playwright__navigate({
  url: 'file:///home/runner/work/Platelet-Movie/Platelet-Movie/site/index.html'
})

// Example: Run code to test functionality
mcp__playwright__browser_run_code({
  code: `async (page) => {
    await page.setViewportSize({ width: 390, height: 844 });
    const title = await page.title();
    return { url: page.url(), title };
  }`
})
```

**Important**: Use the full absolute path in `file://` URLs:
- Format: `file://${{ github.workspace }}/site/index.html`
- Example: `file:///home/runner/work/Platelet-Movie/Platelet-Movie/site/index.html`

For each device viewport, use Playwright MCP tools to:
- Navigate to `file://${{ github.workspace }}/site/index.html`
- Set viewport size for the device being tested
- Take screenshots and run accessibility audits
- Test interactions (theme toggle, table sorting)
- Check for layout issues (overflow, truncation, broken layouts)

### Key Elements to Test

The Platelet Movie generated static site includes:
- **Header** with title and dark mode toggle button
- **Lady Whistledown commentary section** with dynamic content
- **Movie table** with sortable columns (Runtime, Year, Score, Rated, Genres, Title)
- **Acknowledgements section** with TMDB attribution, disclaimer, and credits
- **Footer** with repository link
- **Responsive design** that adapts to different screen sizes

### Test Scenarios

1. **Theme Toggle**: Click the theme toggle button and verify light/dark mode switches
2. **Table Sorting**: Click column headers and verify sorting functionality
3. **Responsive Layout**: Verify layout adapts correctly at each viewport size
4. **Element Visibility**: Verify all sections are visible and properly rendered
5. **Links**: Verify external links are present and properly formatted

## Step 4: Analyze Results

Organize findings by severity:
- 🔴 **Critical**: Blocks functionality or major accessibility issues
- 🟡 **Warning**: Minor issues or potential problems
- 🟢 **Passed**: Everything working as expected

## Step 5: Report Results

### If NO Issues Found

**YOU MUST CALL** the `noop` tool to log completion:

```json
{
  "noop": {
    "message": "Multi-device documentation testing complete. All {device_count} devices tested successfully with no issues found."
  }
}
```

**DO NOT just write this message in your output text** - you MUST actually invoke the `noop` tool. The workflow will fail if you don't call it.

### If Issues ARE Found

## 📝 Report Formatting Guidelines

**CRITICAL**: Follow these formatting guidelines to create well-structured, readable reports:

### 1. Header Levels
**Use h3 (###) or lower for all headers in your report to maintain proper document hierarchy.**

The issue or discussion title serves as h1, so all content headers should start at h3:
- Use `###` for main sections (e.g., "### Executive Summary", "### Key Metrics")
- Use `####` for subsections (e.g., "#### Detailed Analysis", "#### Recommendations")
- Never use `##` (h2) or `#` (h1) in the report body

### 2. Progressive Disclosure
**Wrap long sections in `<details><summary><b>Section Name</b></summary>` tags to improve readability and reduce scrolling.**

Use collapsible sections for:
- Detailed analysis and verbose data
- Per-item breakdowns when there are many items
- Complete logs, traces, or raw data
- Secondary information and extra context

Example:
```markdown
<details>
<summary><b>View Detailed Analysis</b></summary>

[Long detailed content here...]

</details>
```

### 3. Report Structure Pattern

Your report should follow this structure for optimal readability:

1. **Brief Summary** (always visible): 1-2 paragraph overview of key findings
2. **Key Metrics/Highlights** (always visible): Critical information and important statistics
3. **Detailed Analysis** (in `<details>` tags): In-depth breakdowns, verbose data, complete lists
4. **Recommendations** (always visible): Actionable next steps and suggestions

### Design Principles

Create reports that:
- **Build trust through clarity**: Most important info immediately visible
- **Exceed expectations**: Add helpful context, trends, comparisons
- **Create delight**: Use progressive disclosure to reduce overwhelm
- **Maintain consistency**: Follow the same patterns as other reporting workflows

Create a GitHub issue titled "🔍 Multi-Device Docs Testing Report - [Date]" with:

```markdown
### Test Summary
- Triggered by: @${{ github.actor }}
- Workflow run: [§${{ github.run_id }}](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})
- Devices tested: {count}
- Test date: [Date]

### Results Overview
- 🟢 Passed: {count}
- 🟡 Warnings: {count}
- 🔴 Critical: {count}

### Critical Issues
[List critical issues that block functionality or major accessibility problems - keep visible]

<details>
<summary><b>View All Warnings</b></summary>

[Minor issues and potential problems with device names and details]

</details>

<details>
<summary><b>View Detailed Test Results by Device</b></summary>

#### Mobile Devices
[Test results, screenshots, findings]

#### Tablet Devices
[Test results, screenshots, findings]

#### Desktop Devices
[Test results, screenshots, findings]

</details>

### Accessibility Findings
[Key accessibility issues - keep visible as these are important]

### Recommendations
[Actionable recommendations for fixing issues - keep visible]
```

Label with: `documentation`, `testing`, `automated`

## Summary

**Always provide a safe output:**
- **If issues found**: Create GitHub issue with test results, findings, and recommendations
- **If no issues found**: Call `noop` tool with completion message including total devices tested and pass status

The workflow requires explicit safe output (either issue creation or noop) to confirm completion.
