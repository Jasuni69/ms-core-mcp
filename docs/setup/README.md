# Setup Documentation

Welcome! This folder contains all the guides you need to set up the Microsoft Fabric MCP Server with either Claude Desktop or Claude Code (VS Code).

---

## 📚 Available Guides

### 🚀 [Installation Checklist](./INSTALLATION_CHECKLIST.md)
**Start here!** Step-by-step checklist format for setting up the MCP server.

**Best for:**
- First-time setup
- Following a structured process
- Ensuring nothing is missed

**Covers:**
- Prerequisites verification
- Installation steps for both Claude Desktop and Claude Code
- Testing and troubleshooting
- Printable checklist format

---

### 💻 [Claude Desktop Setup](./CLAUDE_DESKTOP_SETUP.md)
Complete guide for configuring the MCP server with **Claude Desktop**.

**Best for:**
- Using the standalone Claude Desktop application
- Quick setup with simple configuration
- Non-developers or those who prefer GUI interfaces

**Includes:**
- Quick setup guide
- Configuration templates
- Troubleshooting common issues
- Example commands and queries

---

### 🔧 [Claude Code Setup (VS Code)](./CLAUDE_CODE_VSCODE_SETUP.md)
Complete guide for configuring the MCP server with **Claude Code** in Visual Studio Code.

**Best for:**
- Developers using VS Code
- Project-based MCP configuration
- Integration with existing VS Code workflows

**Includes:**
- `.mcp.json` configuration
- Claude Code settings
- VS Code-specific troubleshooting
- Advanced configuration options

---

### 📐 [Architecture Diagram](./ARCHITECTURE_DIAGRAM.md)
Technical overview of how the MCP server works with Microsoft Fabric.

**Best for:**
- Understanding the system architecture
- Learning how components interact
- Technical documentation reference

---

## 🎯 Which Guide Should I Use?

### I'm new to this → Start with [Installation Checklist](./INSTALLATION_CHECKLIST.md)
The checklist walks you through everything step-by-step.

### I want to use Claude Desktop → See [Claude Desktop Setup](./CLAUDE_DESKTOP_SETUP.md)
Perfect for the standalone app.

### I want to use VS Code → See [Claude Code Setup](./CLAUDE_CODE_VSCODE_SETUP.md)
For developers who live in VS Code.

### I want to understand how it works → Read [Architecture Diagram](./ARCHITECTURE_DIAGRAM.md)
Technical overview and architecture.

---

## 🔑 Prerequisites (All Guides)

Before using any guide, ensure you have:

- ✅ **Python 3.12+** installed
- ✅ **uv** package manager installed
- ✅ **Azure CLI** installed and configured
- ✅ **Claude Desktop** OR **VS Code with Claude Code**
- ✅ Access to a Microsoft Fabric workspace (Contributor/Admin role)

---

## ⚡ Quick Start

**Don't want to read docs?** Here's the 2-minute version:

### For Claude Desktop:

```bash
# 1. Install dependencies
uv sync

# 2. Authenticate
az login

# 3. Edit config file (path depends on OS)
# Windows: %APPDATA%\Claude\claude_desktop_config.json
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json

# 4. Add this (replace path!):
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "uv",
      "args": ["--directory", "/full/path/to/project", "run", "fabric_mcp_stdio.py"]
    }
  }
}

# 5. Restart Claude Desktop
# 6. Test: "List all my Fabric workspaces"
```

### For Claude Code (VS Code):

```bash
# 1. Install dependencies
uv sync

# 2. Authenticate
az login

# 3. Create .mcp.json in project root:
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "uv",
      "args": ["run", "fabric_mcp_stdio.py"],
      "cwd": "/full/path/to/project",
      "env": {}
    }
  }
}

# 4. Edit ~/.claude/settings.json:
{
  "enableAllProjectMcpServers": true
}

# 5. Reload VS Code
# 6. Test: "List all my Fabric workspaces"
```

---

## 🆘 Troubleshooting

### Common Issues:

**MCP server not detected:**
- Check config file paths are absolute
- Verify `.venv` folder exists
- Restart Claude Desktop/VS Code completely
- Validate JSON syntax

**Authentication errors:**
- Run `az login` again
- Verify token: `az account get-access-token --resource https://api.fabric.microsoft.com/`
- Check Fabric workspace permissions

**"Command not found: uv":**
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Module/Python errors:**
```bash
# Reinstall dependencies
uv sync --reinstall

# Check Python version (must be 3.12+)
python --version
```

---

## 📖 Additional Resources

- **[Main README](../../README.md)** - Complete project documentation
- **[Testing Guide](../testing/README.md)** - See what works and examples
- **[Medallion Architecture Test](../testing/medallion_architecture_test.md)** - End-to-end example
- **[Notebook Examples](../medallion_notebooks.md)** - Ready-to-use PySpark code

---

## 🎓 What You Can Do After Setup

Once installed, you can ask Claude to:

**Manage Workspaces:**
- List all workspaces
- Create new workspaces with trial capacity
- Set active workspace

**Work with Lakehouses:**
- Create lakehouses (bronze, silver, gold layers)
- List all tables
- Get table schemas
- Query data with SQL

**Manage Notebooks:**
- Create PySpark notebooks from templates
- Generate Fabric-specific code
- Run notebook jobs
- Check execution status

**OneLake File Operations:**
- Read/write files
- List directories
- Manage data files

**And 70+ more tools!**

---

## 💡 Pro Tips

1. **Use `uv run`** instead of specifying Python paths - it's simpler and more portable
2. **Add `.mcp.json` to `.gitignore`** - it contains user-specific paths
3. **Test with read-only commands first** - "list workspaces" before "create workspace"
4. **Install ODBC driver** - Enables SQL query tools (optional but recommended)
5. **Keep docs handy** - Bookmark this folder for reference

---

## 📝 Feedback & Issues

Found a problem with the setup docs?
- Check existing issues: https://github.com/your-repo/issues
- Create a new issue with details about what went wrong
- Include your OS, Python version, and error messages

---

**Ready to get started?** Pick a guide above and begin your setup! 🚀
