# Setting Up Microsoft Fabric MCP Tools in Claude Code (VS Code)

This guide explains how to configure and use the Microsoft Fabric MCP server with Claude Code inside Visual Studio Code.

## Overview

Claude Code (the AI coding assistant in VS Code) has its own MCP configuration system that is separate from VS Code's workspace settings. This guide shows you how to set up the Fabric MCP tools so Claude Code can manage your Fabric workspaces, lakehouses, notebooks, and more through natural language.

---

## Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.12 or higher** installed
- ✅ **Visual Studio Code** with Claude Code extension
- ✅ **Azure CLI** installed and configured
- ✅ **uv** package manager installed
- ✅ Access to a **Microsoft Fabric workspace** (with Contributor or Admin role)

---

## Quick Setup

### 1. Install Project Dependencies

Open a terminal in the project root and run:

```bash
uv sync
```

This creates a virtual environment (`.venv`) and installs all required Python packages.

### 2. Authenticate with Azure

```bash
az login
```

Verify authentication:
```bash
az account get-access-token --resource https://api.fabric.microsoft.com/
```

You should see an access token, which confirms you're authenticated.

### 3. Create `.mcp.json` in Project Root

Create a file named `.mcp.json` in your project's root directory:

**Template:**
```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "uv",
      "args": ["run", "fabric_mcp_stdio.py"],
      "cwd": "C:\\Users\\YourUsername\\Documents\\Projects\\ms-fabric-core-tools-mcp",
      "env": {}
    }
  }
}
```

**Important:** Replace `cwd` with the **absolute path** to this project on your machine.

**Path Format Notes:**
- **Windows**: Use double backslashes `\\` or forward slashes `/`
  - ✅ `"C:\\Users\\Name\\Projects\\ms-fabric-core-tools-mcp"`
  - ✅ `"C:/Users/Name/Projects/ms-fabric-core-tools-mcp"`
  - ❌ `"C:\Users\Name..."` (single backslash won't work in JSON)
- **macOS/Linux**: Use forward slashes
  - ✅ `"/Users/name/projects/ms-fabric-core-tools-mcp"`

**Why use `uv run`?**
- `uv run` automatically activates the virtual environment and runs the script
- No need to specify full path to Python executable
- Works consistently across different operating systems

### 4. Configure Claude Code Settings

Create or edit the Claude Code settings file:

**Location:**
- **Windows**: `C:\Users\YourUsername\.claude\settings.json`
- **macOS**: `~/Library/Application Support/Claude/settings.json`
- **Linux**: `~/.config/Claude/settings.json`

**Add this configuration:**

```json
{
  "enableAllProjectMcpServers": true
}
```

This automatically enables any MCP server found in `.mcp.json` files in your projects.

**Alternative (more restrictive):**
```json
{
  "enabledMcpjsonServers": ["ms-fabric-core-tools-mcp"]
}
```

This only enables specific servers you list.

### 5. Add `.mcp.json` to `.gitignore`

**Important:** The `.mcp.json` file contains user-specific paths and should NOT be committed to git.

The project's `.gitignore` already includes:
```
# Local MCP configuration (contains user-specific paths)
.mcp.json
```

### 6. Restart VS Code

After creating the configuration files, **reload the VS Code window**:

1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Type "Reload Window" and select "Developer: Reload Window"

Or simply close and reopen VS Code.

### 7. Approve the MCP Server

When Claude Code detects a new MCP server, it may prompt you to approve it. Click "Approve" to allow Claude Code to use the Fabric MCP tools.

---

## Verifying the Setup

Once configured, test that Claude Code can access the MCP tools:

1. Open a new Claude Code session in VS Code
2. Ask: "List my Microsoft Fabric workspaces"
3. You should see your workspaces listed

The tools are available with this naming format:
```
mcp__ms-fabric-core-tools-mcp__<tool-name>
```

**Available Tools** (70+ tools total):
- Workspace management: `list_workspaces`, `create_workspace`, `set_workspace`
- Lakehouse operations: `list_lakehouses`, `create_lakehouse`, `list_tables`, `table_schema`
- Notebook management: `create_notebook`, `list_notebooks`, `run_notebook_job`
- SQL queries: `sql_query`, `sql_explain`, `sql_export`
- OneLake files: `onelake_read`, `onelake_write`, `onelake_ls`
- Semantic models: `list_semantic_models`, `create_measure`, `dax_query`
- And many more!

---

## Example Usage

Once configured, you can ask Claude Code:

**Workspace Management:**
```
"List all my Fabric workspaces"
"Create a new workspace called 'Analytics_Workspace' with trial capacity"
"Set my workspace to 'Analytics_Workspace'"
```

**Lakehouse Operations:**
```
"Create a lakehouse called 'bronze_customer_data'"
"Show me all tables in the bronze_customer_data lakehouse"
"Get the schema for the customers_raw table"
```

**SQL Queries:**
```
"Run a SQL query: SELECT * FROM dbo.customers WHERE country = 'USA'"
"Show me the top 10 customers by revenue"
```

**Notebook Management:**
```
"Create a PySpark notebook for ETL processing"
"List all notebooks in my workspace"
```

---

## Troubleshooting

### MCP Tools Not Appearing

1. **Check `.mcp.json` exists** in project root
2. **Verify the `cwd` path** is correct and absolute
3. **Check Claude Code settings** in `~/.claude/settings.json`
4. **Reload VS Code window** completely
5. **Look for approval prompts** in Claude Code interface

### "Command not found: uv"

Install uv:
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your terminal and VS Code.

### Azure Authentication Errors

1. Run `az login` again
2. Verify workspace access in Fabric portal
3. Test token: `az account get-access-token --resource https://api.fabric.microsoft.com/`

---

## ODBC Driver (Optional)

Some SQL tools require Microsoft ODBC Driver for SQL Server.

**Install:** [Download ODBC Driver 18](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

---

## Summary

1. ✅ Run `uv sync` to install dependencies
2. ✅ Run `az login` to authenticate
3. ✅ Create `.mcp.json` in project root
4. ✅ Configure `~/.claude/settings.json`
5. ✅ Reload VS Code
6. ✅ Start using: "List my Fabric workspaces"!

🎉 You're ready to manage Microsoft Fabric through Claude Code!
