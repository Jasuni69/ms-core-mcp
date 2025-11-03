# Quick Setup Guide for Colleagues

## What is this?

This MCP server lets you use **natural language in Claude Desktop** to manage Microsoft Fabric workspaces, lakehouses, warehouses, and more!

Instead of clicking through the Fabric portal, just ask Claude:
- "List all my Fabric workspaces"
- "Create a lakehouse called 'data-lake' in my workspace"
- "Show me all tables in my lakehouse"

## Prerequisites

- Python 3.12+ installed
- Claude Desktop installed
- Azure CLI installed
- Access to a Microsoft Fabric workspace

## Setup Steps

### 1. Install Dependencies

Open a terminal in this directory and run:

```bash
uv sync
```

This creates a virtual environment and installs all Python packages.

### 2. Authenticate with Azure

```bash
az login
```

Make sure your account has **Contributor** or **Admin** role in your Fabric workspace.

### 3. Configure Claude Desktop

**Find your Claude Desktop config file:**
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

**Add this configuration:**

**Windows Example:**
```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "C:\\Users\\YourName\\path\\to\\ms-fabric-core-tools-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\YourName\\path\\to\\ms-fabric-core-tools-mcp\\fabric_mcp_stdio.py"
      ],
      "env": {
        "USERPROFILE": "C:\\Users\\YourName"
      }
    }
  }
}
```

**macOS/Linux Example:**
```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "/Users/yourname/path/to/ms-fabric-core-tools-mcp/.venv/bin/python",
      "args": [
        "/Users/yourname/path/to/ms-fabric-core-tools-mcp/fabric_mcp_stdio.py"
      ],
      "env": {
        "HOME": "/Users/yourname"
      }
    }
  }
}
```

**IMPORTANT:** Replace the paths with the actual full paths on your system!

### 4. Restart Claude Desktop

Close Claude Desktop completely and restart it.

### 5. Test It!

Open Claude Desktop and try:

```
List all my Microsoft Fabric workspaces
```

If you see your workspaces, you're all set! 🎉

## Common Commands

Once connected, you can ask Claude:

**Workspace Management:**
- "List all my Fabric workspaces"
- "Set my workspace to 'my-workspace-name'"

**Lakehouse Operations:**
- "Show me all lakehouses in my workspace"
- "Create a lakehouse called 'test-lake'"
- "List all tables in the 'test-lake' lakehouse"
- "Show me the schema for the 'customers' table"

**PySpark Notebooks:**
- "Create a PySpark notebook for ETL processing"
- "Generate a notebook with analytics template"

**Code Generation:**
- "Generate PySpark code to read from a lakehouse table"
- "Show me code to merge Delta tables"

## Troubleshooting

### MCP Server Not Showing Up

1. Check that the paths in `claude_desktop_config.json` are correct
2. Verify `.venv` folder exists in the project directory
3. Restart Claude Desktop completely
4. Check Task Manager (Windows) to ensure Claude Desktop isn't running in background

### Authentication Errors

1. Run `az login` again
2. Verify access: `az account get-access-token --resource https://api.fabric.microsoft.com/`
3. Check you have permissions in the Fabric workspace

### Can't Create Resources

- Make sure your account has **Contributor** or **Admin** role
- Check workspace permissions in the Fabric portal
- Try read-only commands first (list workspaces, list lakehouses)

### Python or Module Errors

```bash
# Reinstall dependencies
uv sync --reinstall

# Check Python version (should be 3.12+)
python --version
```

## Need More Help?

See the full [README.md](README.md) for detailed documentation and troubleshooting.

## Quick Reference Card

| What You Want | What To Ask Claude |
|--------------|-------------------|
| See all workspaces | "List all my Fabric workspaces" |
| Set active workspace | "Set my workspace to 'workspace-name'" |
| List lakehouses | "Show me all lakehouses" |
| Create lakehouse | "Create a lakehouse called 'data-lake'" |
| List tables | "List all tables in my lakehouse" |
| Get table schema | "Show me the schema for the 'sales' table" |
| Create notebook | "Create a PySpark notebook for analytics" |
| Generate code | "Generate PySpark code to read from lakehouse" |

---

**Questions?** Check the main [README.md](README.md) or ask your colleague who set this up!
