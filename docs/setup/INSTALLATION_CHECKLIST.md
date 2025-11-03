# Microsoft Fabric MCP Server - Installation Checklist

Use this checklist to set up the Microsoft Fabric MCP Server step-by-step. Print it out or keep it open while you work through the installation.

---

## Prerequisites Checklist

### Required Software

- [ ] **Python 3.12 or higher** installed
  - Test: `python --version` (should show 3.12.x or higher)
  - Download: https://www.python.org/downloads/

- [ ] **uv package manager** installed
  - Test: `uv --version`
  - Windows install: `irm https://astral.sh/uv/install.ps1 | iex`
  - macOS/Linux install: `curl -LsSf https://astral.sh/uv/install.sh | sh`

- [ ] **Azure CLI** installed
  - Test: `az --version`
  - Download: https://learn.microsoft.com/cli/azure/install-azure-cli

- [ ] **Claude Desktop** OR **VS Code with Claude Code** installed
  - Claude Desktop: https://claude.ai/download
  - Claude Code (VS Code extension): Install from VS Code marketplace

### Azure Access

- [ ] Access to a **Microsoft Fabric workspace**
  - Need: Contributor or Admin role
  - Verify: Log into https://app.fabric.microsoft.com/ and check workspace access

---

## Installation Steps

### Step 1: Clone/Download Project ✅

- [ ] Download or clone the `ms-fabric-core-tools-mcp` repository
- [ ] Navigate to the project directory
- [ ] Verify you see `fabric_mcp_stdio.py` and `pyproject.toml` files

### Step 2: Install Dependencies ✅

- [ ] Open terminal in project directory
- [ ] Run: `uv sync`
- [ ] Wait for completion (this creates `.venv` folder and installs packages)
- [ ] Verify `.venv` folder was created:
  - Windows: `dir .venv`
  - macOS/Linux: `ls .venv`

**Expected output:** "Resolved X packages in Y seconds"

### Step 3: Azure Authentication ✅

- [ ] Run: `az login`
- [ ] Browser opens for authentication
- [ ] Sign in with your Azure account
- [ ] Verify success: `az account get-access-token --resource https://api.fabric.microsoft.com/`
- [ ] You should see a JSON response with an access token

**Troubleshooting:** If token command fails, you may not have Fabric access. Contact your admin.

---

## Configuration: Choose Your Client

You need to configure EITHER Claude Desktop OR Claude Code (VS Code). Choose the one you want to use:

### Option A: Claude Desktop Configuration

#### Step 4A: Find Config File Path

- [ ] Locate your Claude Desktop config file:
  - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
  - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Quick find (Windows PowerShell):**
```powershell
echo $env:APPDATA\Claude\claude_desktop_config.json
```

**Quick find (macOS/Linux):**
```bash
echo ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

#### Step 5A: Get Project Path

- [ ] Get the **absolute path** to this project directory

**Windows (PowerShell):**
```powershell
cd path\to\ms-fabric-core-tools-mcp
(Get-Location).Path -replace '\\', '\\\\'
```

**macOS/Linux:**
```bash
cd path/to/ms-fabric-core-tools-mcp
pwd
```

**Write your path here:**
```
Project path: _______________________________________
```

#### Step 6A: Edit Configuration File

- [ ] Open `claude_desktop_config.json` in a text editor (Notepad, VS Code, etc.)
- [ ] Add or merge this configuration:

**Windows:**
```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "PASTE_YOUR_PATH_HERE",
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
        "PASTE_YOUR_PATH_HERE",
        "run",
        "fabric_mcp_stdio.py"
      ]
    }
  }
}
```

- [ ] Replace `PASTE_YOUR_PATH_HERE` with your actual project path
- [ ] Save the file
- [ ] **Optional**: Validate JSON at https://jsonlint.com/

#### Step 7A: Restart Claude Desktop

- [ ] **Completely close** Claude Desktop
  - Windows: Check Task Manager (Ctrl+Shift+Esc) - ensure no Claude process running
  - macOS: Check Activity Monitor - ensure Claude not running
  - Linux: `ps aux | grep claude`
- [ ] Reopen Claude Desktop

#### Step 8A: Test Connection

- [ ] Open Claude Desktop
- [ ] Type: "List all my Microsoft Fabric workspaces"
- [ ] You should see your workspaces listed ✅

**If it works:** You're done! Skip to "Next Steps" section.

---

### Option B: Claude Code (VS Code) Configuration

#### Step 4B: Create `.mcp.json`

- [ ] Navigate to the project root directory
- [ ] Create a new file named `.mcp.json`
- [ ] Get the absolute path to this project:

**Windows (PowerShell):**
```powershell
(Get-Location).Path
```

**macOS/Linux:**
```bash
pwd
```

**Write your path here:**
```
Project path: _______________________________________
```

- [ ] Add this content to `.mcp.json`:

**Windows:**
```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "uv",
      "args": ["run", "fabric_mcp_stdio.py"],
      "cwd": "PASTE_YOUR_PATH_HERE",
      "env": {}
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
      "args": ["run", "fabric_mcp_stdio.py"],
      "cwd": "PASTE_YOUR_PATH_HERE",
      "env": {}
    }
  }
}
```

- [ ] Replace `PASTE_YOUR_PATH_HERE` with your actual path
- [ ] Save `.mcp.json`
- [ ] **Important**: Verify `.mcp.json` is in `.gitignore` (it is by default)

#### Step 5B: Configure Claude Code Settings

- [ ] Find/create Claude Code settings file:
  - **Windows**: `C:\Users\YourUsername\.claude\settings.json`
  - **macOS**: `~/Library/Application Support/Claude/settings.json`
  - **Linux**: `~/.config/Claude/settings.json`

- [ ] Create or edit the file with this content:

```json
{
  "enableAllProjectMcpServers": true
}
```

- [ ] Save the file

#### Step 6B: Reload VS Code

- [ ] Open Command Palette: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
- [ ] Type: "Reload Window"
- [ ] Select: "Developer: Reload Window"
- [ ] VS Code will reload

#### Step 7B: Approve MCP Server

- [ ] When prompted, click "Approve" to allow Claude Code to use the MCP server

#### Step 8B: Test Connection

- [ ] Open Claude Code in VS Code
- [ ] Ask: "List all my Microsoft Fabric workspaces"
- [ ] You should see your workspaces listed ✅

**If it works:** You're done! Continue to "Next Steps" section.

---

## Verification Checklist

### Basic Functionality Tests

Test these commands in Claude Desktop or Claude Code:

- [ ] **List workspaces**: "List all my Fabric workspaces"
  - Expected: Table with workspace names and IDs

- [ ] **Set workspace**: "Set my workspace to 'workspace-name'"
  - Expected: Confirmation message

- [ ] **List lakehouses**: "Show me all lakehouses in my workspace"
  - Expected: List of lakehouses (or message if none exist)

- [ ] **List tables**: "List all tables in lakehouse 'lakehouse-name'"
  - Expected: List of tables (or message if none exist)

### Advanced Tests (Optional)

- [ ] **Create lakehouse**: "Create a test lakehouse called 'test_lake'"
- [ ] **Create notebook**: "Create a PySpark notebook for testing"
- [ ] **SQL query** (if ODBC installed): "Run SELECT * FROM dbo.table_name LIMIT 5"

---

## Optional: Install ODBC Driver

For SQL query capabilities, install Microsoft ODBC Driver for SQL Server:

- [ ] Download: https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server
- [ ] Install: ODBC Driver 18 for SQL Server
- [ ] Restart Claude Desktop or VS Code
- [ ] Test: "Run a SQL query: SELECT @@VERSION"

**What works without ODBC:**
- ✅ Workspace, lakehouse, notebook management
- ✅ OneLake file operations
- ✅ Schema inspection

**What requires ODBC:**
- ⚠️ `sql_query` - Run T-SQL queries
- ⚠️ `table_preview` - View table data

---

## Troubleshooting Guide

### Issue: MCP server not detected

**Checklist:**
- [ ] Verify config file exists and has correct path
- [ ] Check JSON syntax is valid (use https://jsonlint.com/)
- [ ] Ensure `.venv` folder exists in project directory
- [ ] Completely restart Claude Desktop/VS Code
- [ ] Check no typos in configuration

**Test manually:**
```bash
cd path/to/ms-fabric-core-tools-mcp
uv run fabric_mcp_stdio.py
```
Expected output: "Starting MCP server in STDIO mode..."

### Issue: Authentication errors

**Checklist:**
- [ ] Run `az login` again
- [ ] Verify token: `az account get-access-token --resource https://api.fabric.microsoft.com/`
- [ ] Check workspace permissions in Fabric portal
- [ ] Ensure you have Contributor or Admin role

### Issue: Python/module errors

**Checklist:**
- [ ] Verify Python version: `python --version` (must be 3.12+)
- [ ] Reinstall dependencies: `uv sync --reinstall`
- [ ] Check `.venv` exists: `ls .venv` or `dir .venv`
- [ ] Try creating fresh venv: `rm -rf .venv` then `uv sync`

### Issue: Can't create resources

**Checklist:**
- [ ] Verify workspace permissions (need Contributor or Admin)
- [ ] Try read-only commands first ("list workspaces")
- [ ] Check workspace isn't read-only
- [ ] Ask admin to grant proper access

---

## Success Criteria

You're successfully installed when:

✅ **Authentication works**: `az login` completes successfully
✅ **MCP server connects**: Claude can see and use Fabric tools
✅ **Basic commands work**: Can list workspaces and lakehouses
✅ **No errors**: Commands execute without authentication/connection errors

---

## Next Steps

Now that you're set up, explore what you can do:

1. **Read the docs**: Check [README.md](../../README.md) for full tool list
2. **See examples**: Review [Testing Guide](../testing/medallion_architecture_test.md)
3. **Try medallion pipeline**: Follow the [Medallion Notebooks Guide](../medallion_notebooks.md)
4. **Experiment**: Ask Claude to help you build data pipelines!

---

## Quick Reference

| Task | Command |
|------|---------|
| List workspaces | "List all my Fabric workspaces" |
| Set workspace | "Set workspace to 'name'" |
| List lakehouses | "Show me all lakehouses" |
| Create lakehouse | "Create lakehouse called 'name'" |
| List tables | "List tables in lakehouse 'name'" |
| Table schema | "Show schema for table 'name'" |
| SQL query | "Run query: SELECT * FROM table" |

---

**Questions?**
- See [Claude Desktop Setup](./CLAUDE_DESKTOP_SETUP.md) for detailed Claude Desktop guide
- See [Claude Code Setup](./CLAUDE_CODE_VSCODE_SETUP.md) for detailed VS Code guide
- Check [README](../../README.md) for complete documentation

**Pro Tip:** Keep this checklist handy for setting up on new machines or for colleagues!

---

**Installation Complete!** 🎉

You can now manage Microsoft Fabric through natural language!
