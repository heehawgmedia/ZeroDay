# ZeroDay

## Hostinger integration for Claude Code

This repo is configured (via [`.mcp.json`](.mcp.json)) to load the official
[Hostinger API MCP server](https://github.com/hostinger/api-mcp-server), which
gives Claude Code direct access to your Hostinger account: hosting, domains,
DNS, VPS, WordPress, billing, and more (155 tools).

### One-time setup

1. **Create a Hostinger API token**
   Log in to hPanel and go to **Account → API** (https://hpanel.hostinger.com/profile/api),
   then generate a new token.

2. **Provide the token to Claude Code as `HOSTINGER_API_TOKEN`**
   - **Claude Code on the web:** open your session's environment settings and add an
     environment variable named `HOSTINGER_API_TOKEN` with your token as the value.
   - **Claude Code CLI (local):** export it in your shell before starting Claude Code:
     ```bash
     export HOSTINGER_API_TOKEN="your-token-here"
     ```

   Never commit the token itself to the repo — `.mcp.json` only references the
   environment variable.

3. **Start a new Claude Code session** in this repo. Claude will ask you to approve
   the `hostinger` MCP server the first time; approve it and the Hostinger tools
   become available.

### Verify it works

In a new session, ask Claude something like *"list my Hostinger domains"* — if the
token is set correctly, it will answer using the live API.
