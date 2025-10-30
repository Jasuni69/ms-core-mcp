# Installation Checklist

Use this checklist to set up the Microsoft Fabric MCP Server for Claude Desktop.

## Prerequisites Checklist

- [ ] Python 3.12 or higher installed
  - Test: `python --version`
- [ ] Claude Desktop installed
  - Download: https://claude.ai/download
- [ ] Azure CLI installed
  - Test: `az --version`
  - Download: https://learn.microsoft.com/cli/azure/install-azure-cli
- [ ] uv package manager installed
  - Test: `uv --version`
  - Download: https://docs.astral.sh/uv/getting-started/installation/
- [ ] Access to a Microsoft Fabric workspace
  - Need: Contributor or Admin role

## Installation Steps

### Step 1: Project Setup
- [ ] Navigate to the `ms-fabric-core-tools-mcp` directory
- [ ] Run `uv sync` to create virtual environment
- [ ] Verify `.venv` folder was created

### Step 2: Azure Authentication
- [ ] Run `az login` in terminal
- [ ] Verify authentication: `az account get-access-token --resource https://api.fabric.microsoft.com/`
- [ ] Confirm you see a long access token (means you're authenticated)

### Step 3: Get Full Paths
You need the full paths to:

**Path 1: Python executable**
- Windows: `C:\path\to\ms-fabric-core-tools-mcp\.venv\Scripts\python.exe`
- macOS/Linux: `/path/to/ms-fabric-core-tools-mcp/.venv/bin/python`

**Path 2: MCP script**
- Windows: `C:\path\to\ms-fabric-core-tools-mcp\fabric_mcp_stdio.py`
- macOS/Linux: `/path/to/ms-fabric-core-tools-mcp/fabric_mcp_stdio.py`

**Path 3: Your home directory**
- Windows: `C:\Users\YourUsername`
- macOS/Linux: `/home/yourusername` or `/Users/yourusername`

Write them here:
```
Python path: ________________________________
Script path: ________________________________
Home path: __________________________________
```

### Step 4: Configure Claude Desktop
- [ ] Find Claude Desktop config file location:
  - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Linux: `~/.config/Claude/claude_desktop_config.json`

- [ ] Open the config file in a text editor

- [ ] Add the MCP server configuration (see below)

- [ ] Replace ALL placeholder paths with your actual paths from Step 3

- [ ] Validate JSON syntax (paste into https://jsonlint.com/ to check)

- [ ] Save the file

**Configuration Template:**

```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "PASTE_PYTHON_PATH_HERE",
      "args": [
        "PASTE_SCRIPT_PATH_HERE"
      ],
      "env": {
        "USERPROFILE": "PASTE_HOME_PATH_HERE"
      }
    }
  }
}
```

**Important Notes:**
- On Windows, use double backslashes: `C:\\Users\\...`
- Use forward slashes on macOS/Linux: `/Users/...`
- For macOS/Linux, use `"HOME"` instead of `"USERPROFILE"`

### Step 5: Test Connection
- [ ] Close Claude Desktop completely
  - Windows: Check Task Manager to ensure it's not running
  - macOS: Check Activity Monitor

- [ ] Restart Claude Desktop

- [ ] Open a new conversation in Claude Desktop

- [ ] Type: "List all my Microsoft Fabric workspaces"

- [ ] You should see a list of your Fabric workspaces

## Verification

If everything is working, you should see:
- ✅ Your Fabric workspaces listed
- ✅ Claude can execute commands like "Show me all lakehouses"
- ✅ No error messages about authentication or connection

## Troubleshooting Quick Fixes

### Issue: MCP server not showing up
- [ ] Verify all paths are correct and absolute (not relative)
- [ ] Check JSON syntax is valid
- [ ] Restart Claude Desktop again
- [ ] Check `.venv` folder exists in project directory

### Issue: Authentication errors
- [ ] Run `az login` again
- [ ] Verify token: `az account get-access-token --resource https://api.fabric.microsoft.com/`
- [ ] Check workspace permissions (need Contributor or Admin)

### Issue: Python or import errors
- [ ] Run `uv sync --reinstall`
- [ ] Verify Python 3.12+: `python --version`
- [ ] Check virtual environment exists: `ls .venv` or `dir .venv`

### Issue: Can't create resources
- [ ] Verify workspace permissions in Fabric portal
- [ ] Try read-only commands first (list workspaces, list lakehouses)
- [ ] Ask workspace admin to grant Contributor role

## Test Commands

Once installed, try these in Claude Desktop:

1. ✅ "List all my Fabric workspaces"
2. ✅ "Set my workspace to 'workspace-name'"
3. ✅ "Show me all lakehouses in my workspace"
4. ✅ "List all tables in lakehouse 'my-lakehouse'"

If all these work, you're successfully set up! 🎉

## Getting Help

- See [SETUP.md](SETUP.md) for quick setup guide
- See [README.md](README.md) for full documentation
- Check troubleshooting section in README for detailed solutions

---

**Pro Tip:** Keep this checklist handy when setting up the server on a new machine or for a colleague!
