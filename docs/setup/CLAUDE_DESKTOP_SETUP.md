# Setting Up Microsoft Fabric MCP Tools in Claude Desktop

This guide shows you how to configure the Microsoft Fabric MCP server to work with Claude Desktop, enabling natural language management of your Fabric workspaces, lakehouses, and data.

## What You'll Be Able to Do

Once configured, you can ask Claude Desktop:
- "List all my Fabric workspaces"
- "Create a lakehouse called 'customer_data' in my workspace"
- "Show me all tables in my lakehouse"
- "Run a SQL query against my data"
- "Create a PySpark notebook for ETL processing"

And much more - 70+ tools for managing Microsoft Fabric!

---

## Prerequisites

Before you begin:

- ✅ **Python 3.12 or higher** installed
- ✅ **Claude Desktop** application installed
- ✅ **Azure CLI** installed and configured
- ✅ **uv** package manager installed
- ✅ Access to a **Microsoft Fabric workspace** (Contributor or Admin role)

---

## Quick Setup Guide

### Step 1: Install Dependencies

Open a terminal in the project directory and run:

```bash
uv sync
```

This creates a virtual environment (`.venv`) and installs all required packages.

### Step 2: Authenticate with Azure

```bash
az login
```

Verify authentication:
```bash
az account get-access-token --resource https://api.fabric.microsoft.com/
```

You should see a long access token. This confirms authentication is working.

### Step 3: Configure Claude Desktop

Find your Claude Desktop config file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Easy way to find it (Windows):**
```powershell
echo $env:APPDATA\Claude\claude_desktop_config.json
```

**Easy way to find it (macOS/Linux):**
```bash
echo ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Step 4: Add MCP Server Configuration

Edit `claude_desktop_config.json` and add this configuration:

**Recommended Method (using `uv run`):**

**Windows:**
```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\YourUsername\\path\\to\\ms-fabric-core-tools-mcp",
        "run",
        "fabric_mcp_stdio.py"
      ]
    }
  }
}
```

**macOS/Linux:**
```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yourname/path/to/ms-fabric-core-tools-mcp",
        "run",
        "fabric_mcp_stdio.py"
      ]
    }
  }
}
```

**Important:** Replace the path with the actual absolute path to this project on your computer!

**Why `uv run`?**
- Automatically uses the correct Python from `.venv`
- No need to find Python executable path
- Works across different operating systems
- Simpler configuration

**Alternative Method (direct Python path):**

If you prefer to use the Python executable directly:

**Windows:**
```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "C:\\Users\\YourName\\path\\to\\ms-fabric-core-tools-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\YourName\\path\\to\\ms-fabric-core-tools-mcp\\fabric_mcp_stdio.py"
      ]
    }
  }
}
```

**macOS/Linux:**
```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "/Users/yourname/path/to/ms-fabric-core-tools-mcp/.venv/bin/python",
      "args": [
        "/Users/yourname/path/to/ms-fabric-core-tools-mcp/fabric_mcp_stdio.py"
      ]
    }
  }
}
```

### Step 5: Restart Claude Desktop

**Important:** Completely close Claude Desktop and restart it.

- **Windows**: Check Task Manager to ensure it's fully closed
- **macOS**: Check Activity Monitor
- **Linux**: Check system processes

Then reopen Claude Desktop.

### Step 6: Test the Connection

Open Claude Desktop and ask:

```
List all my Microsoft Fabric workspaces
```

If you see your workspaces listed, congratulations! The setup is complete! 🎉

---

## Example Commands

Once connected, try these commands:

**Workspace Management:**
```
"Show me all my Fabric workspaces"
"Set my workspace to 'MyWorkspace'"
```

**Lakehouse Operations:**
```
"List all lakehouses in my workspace"
"Create a lakehouse called 'bronze_data'"
"Show me all tables in the 'bronze_data' lakehouse"
"Get the schema for the 'customers' table"
```

**SQL Queries:**
```
"Run this SQL query: SELECT * FROM dbo.customers WHERE country = 'USA'"
"Show me the top 10 rows from the sales table"
```

**Notebook Management:**
```
"Create a PySpark notebook for ETL"
"List all notebooks in my workspace"
```

**OneLake Files:**
```
"List files in Files/raw/customers/"
"Read the CSV file at Files/raw/data.csv"
```

---

## Troubleshooting

### MCP Server Not Showing Up

1. **Check paths are correct**: Make sure all paths in `claude_desktop_config.json` are absolute and correct
2. **Verify `.venv` exists**: Check that `uv sync` created the `.venv` folder
3. **Restart completely**: Fully close Claude Desktop (check Task Manager/Activity Monitor)
4. **Check config syntax**: Validate JSON at https://jsonlint.com/

### "Command not found: uv"

Install uv package manager:

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your terminal.

### Authentication Errors

1. **Re-login to Azure:**
   ```bash
   az login
   ```

2. **Verify token:**
   ```bash
   az account get-access-token --resource https://api.fabric.microsoft.com/
   ```

3. **Check workspace permissions**: Ensure you have Contributor or Admin role in the Fabric portal

### Python or Module Errors

1. **Reinstall dependencies:**
   ```bash
   uv sync --reinstall
   ```

2. **Check Python version:**
   ```bash
   python --version
   # Should be 3.12 or higher
   ```

3. **Verify virtual environment:**
   ```bash
   # Windows
   dir .venv

   # macOS/Linux
   ls .venv
   ```

### Can't Create Resources

- **Check permissions**: Verify you have Contributor or Admin role in Fabric workspace
- **Try read-only first**: Test with "list workspaces" or "list lakehouses" before creating resources
- **Ask admin for access**: Request proper role from workspace administrator

---

## Path Format Guide

Getting paths wrong is the #1 cause of setup issues. Here's how to format paths correctly:

### Windows Paths

**In JSON, you MUST escape backslashes:**
- ✅ `"C:\\Users\\Name\\Projects\\ms-fabric-core-tools-mcp"`
- ✅ `"C:/Users/Name/Projects/ms-fabric-core-tools-mcp"` (forward slashes work!)
- ❌ `"C:\Users\Name\Projects\ms-fabric-core-tools-mcp"` (single backslash FAILS)

**Quick way to get your path (Windows PowerShell):**
```powershell
cd path\to\ms-fabric-core-tools-mcp
(Get-Location).Path -replace '\\', '\\\\'
```

### macOS/Linux Paths

**Use forward slashes:**
- ✅ `/Users/name/projects/ms-fabric-core-tools-mcp`
- ✅ `/home/name/projects/ms-fabric-core-tools-mcp`

**Quick way to get your path (macOS/Linux):**
```bash
cd path/to/ms-fabric-core-tools-mcp
pwd
```

---

## ODBC Driver (Optional)

Some SQL query tools work better with Microsoft ODBC Driver for SQL Server installed.

**What works without ODBC:**
- ✅ All workspace, lakehouse, notebook operations
- ✅ OneLake file operations
- ✅ Schema inspection
- ✅ Code generation

**What requires ODBC:**
- ⚠️ `sql_query` - Run T-SQL queries (recommended to install)
- ⚠️ `table_preview` - Preview table data
- ❌ `describe_history`, `optimize_delta` - Use Spark SQL in notebooks instead

**Install ODBC Driver:**
[Download ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

After installing, restart Claude Desktop to enable SQL query features.

---

## Configuration Examples

### Multiple MCP Servers

You can have multiple MCP servers configured:

```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ms-fabric-core-tools-mcp",
        "run",
        "fabric_mcp_stdio.py"
      ]
    },
    "another-mcp-server": {
      "command": "node",
      "args": ["/path/to/server.js"]
    }
  }
}
```

### With Environment Variables

Pass custom environment variables to the MCP server:

```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ms-fabric-core-tools-mcp",
        "run",
        "fabric_mcp_stdio.py"
      ],
      "env": {
        "LOG_LEVEL": "DEBUG",
        "AZURE_TENANT_ID": "your-tenant-id"
      }
    }
  }
}
```

---

## Additional Resources

- **[Installation Checklist](./INSTALLATION_CHECKLIST.md)** - Step-by-step checklist
- **[Main README](../../README.md)** - Complete project documentation
- **[Testing Guide](../testing/README.md)** - See what works and examples
- **[Claude Desktop Documentation](https://claude.ai/help)** - Official Claude Desktop docs
- **[MCP Protocol](https://modelcontextprotocol.io/)** - Learn about MCP

---

## Quick Reference Card

| What You Want | What To Ask Claude |
|--------------|-------------------|
| See all workspaces | "List all my Fabric workspaces" |
| Set active workspace | "Set my workspace to 'workspace-name'" |
| List lakehouses | "Show me all lakehouses" |
| Create lakehouse | "Create a lakehouse called 'data-lake'" |
| List tables | "List all tables in my lakehouse" |
| Get table schema | "Show me the schema for the 'sales' table" |
| Run SQL query | "Run a SQL query: SELECT * FROM dbo.customers" |
| Create notebook | "Create a PySpark notebook for analytics" |

---

## Summary

To set up Microsoft Fabric MCP tools in Claude Desktop:

1. ✅ Install dependencies: `uv sync`
2. ✅ Authenticate: `az login`
3. ✅ Edit `claude_desktop_config.json` with server configuration
4. ✅ Use `uv run` for simplicity
5. ✅ Completely restart Claude Desktop
6. ✅ Test: "List all my Fabric workspaces"

🎉 You're ready to manage Microsoft Fabric through natural language in Claude Desktop!

---

**Questions?** Check the [Installation Checklist](./INSTALLATION_CHECKLIST.md) for a step-by-step walkthrough or see the main [README](../../README.md) for detailed documentation.
