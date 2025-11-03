# Setting Up MCP Tools in Claude Code (VS Code)

This guide explains how to configure and use MCP (Model Context Protocol) servers with Claude Code inside Visual Studio Code.

## Overview

Claude Code has its own MCP configuration system that is separate from VS Code's workspace settings. This means you need to configure MCP servers specifically for Claude Code, even if they're already configured in your VS Code workspace.

## Configuration Steps

### 1. Create `.mcp.json` in Your Project Root

Create a `.mcp.json` file in your project's root directory with the following structure:

```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "uv",
      "args": ["run", "fabric_mcp_stdio.py"],
      "cwd": "c:\\Users\\YourUsername\\Documents\\Projects\\ms-fabric-core-tools-mcp",
      "env": {}
    }
  }
}
```

**Key parameters:**
- `command`: The executable to run (e.g., `uv`, `node`, `python`)
- `args`: Command-line arguments to pass
- `cwd`: Working directory for the MCP server (absolute path)
- `env`: Environment variables (optional)

### 2. Enable MCP Servers in Claude Code Settings

Create or edit the Claude Code settings file at:
- **Windows**: `C:\Users\YourUsername\.claude\settings.json`
- **macOS/Linux**: `~/.claude/settings.json`

Add one of the following configurations:

#### Option 1: Enable All Project MCP Servers (Recommended)

```json
{
  "enableAllProjectMcpServers": true
}
```

This automatically enables any MCP server found in `.mcp.json` files in your projects.

#### Option 2: Enable Specific Servers Only

```json
{
  "enabledMcpjsonServers": ["ms-fabric-core-tools-mcp"]
}
```

This gives you more granular control over which servers are enabled.

### 3. Restart VS Code

After creating the configuration files, you need to **reload the entire VS Code window**:

1. Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Type "Reload Window" and select "Developer: Reload Window"

Alternatively, close and reopen VS Code.

### 4. Approve the MCP Server (if prompted)

When Claude Code detects a new MCP server, it may prompt you to approve it. This is a security feature to ensure you trust the code being executed.

## Verifying the Setup

Once configured, Claude Code can access MCP tools. The tools will be available with a prefix format:

```
mcp__<server-name>__<tool-name>
```

For example, with the `ms-fabric-core-tools-mcp` server:
- `mcp__ms-fabric-core-tools-mcp__list_workspaces`
- `mcp__ms-fabric-core-tools-mcp__create_lakehouse`
- `mcp__ms-fabric-core-tools-mcp__sql_query`

## Key Differences: VS Code vs Claude Code

| Aspect | VS Code Workspace | Claude Code |
|--------|------------------|-------------|
| Config Location | `.vscode/settings.json` or `workspace.json` | `.mcp.json` in project root |
| Global Settings | VS Code settings | `~/.claude/settings.json` |
| MCP Integration | VS Code's MCP client | Claude Code's MCP client |
| Configuration Sharing | ❌ These are separate systems | ❌ These are separate systems |

**Important**: Even if you have MCP servers configured in VS Code workspace settings, Claude Code will not detect them. You must create a separate `.mcp.json` file.

## Troubleshooting

### MCP Tools Not Appearing

1. **Check the `.mcp.json` file exists** in your project root
2. **Verify the `cwd` path** is correct and uses the proper path format for your OS
3. **Ensure Claude Code settings** are properly configured in `~/.claude/settings.json`
4. **Reload the VS Code window** completely
5. **Check for approval prompts** in the Claude Code interface

### Server Connection Issues

1. **Verify the command exists**: Make sure `uv`, `node`, `python`, or whatever command you're using is in your PATH
2. **Test the server manually**: Try running the command directly from your terminal
3. **Check environment variables**: Ensure any required env vars are set in the `env` object

### Path Format Issues

- **Windows**: Use double backslashes `\\` or forward slashes `/`
  - ✅ `"c:\\Users\\Name\\Project"`
  - ✅ `"c:/Users/Name/Project"`
  - ❌ `"c:\Users\Name\Project"` (single backslash won't work in JSON)

## Example: This Project (ms-fabric-core-tools-mcp)

This project provides MCP tools for Microsoft Fabric. After setup, Claude Code can:

- List and create workspaces, lakehouses, and warehouses
- Run SQL queries against Fabric data sources
- Manage notebooks and run notebook jobs
- Interact with semantic models and reports
- Perform OneLake file operations
- Query via Microsoft Graph API
- And much more (70+ tools available)

## Additional Resources

- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Microsoft Fabric MCP Server Repository](https://github.com/your-repo-here)

## Summary

To use MCP servers with Claude Code in VS Code:

1. ✅ Create `.mcp.json` in your project root with server configuration
2. ✅ Create/edit `~/.claude/settings.json` to enable MCP servers
3. ✅ Reload VS Code window
4. ✅ Start using MCP tools in Claude Code!
