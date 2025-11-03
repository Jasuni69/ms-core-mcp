# Microsoft Fabric MCP Tools - Documentation

This folder contains comprehensive documentation for the Microsoft Fabric MCP Server, organized by purpose.

## 📁 Documentation Structure

```
docs/
├── README.md                    # This file - Documentation index
├── setup/                       # Installation and configuration
├── guides/                      # Usage guides and tutorials
├── testing/                     # Testing documentation
├── bugfixes/                    # Bug fixes and test results
└── images/                      # Screenshots and diagrams
```

---

## 🚀 Setup & Installation

**Directory:** [setup/](setup/)

### [CLAUDE_DESKTOP_SETUP.md](setup/CLAUDE_DESKTOP_SETUP.md)
Set up MCP server with Claude Desktop (standalone app)

**What's inside:**
- Installing dependencies with uv
- Azure authentication
- Claude Desktop configuration
- Troubleshooting common issues
- Quick reference commands

**Use this if:** You want to use Claude Desktop app to manage Fabric resources

---

### [CLAUDE_CODE_VSCODE_SETUP.md](setup/CLAUDE_CODE_VSCODE_SETUP.md)
Set up MCP server with Claude Code in VS Code

**What's inside:**
- Creating `.mcp.json` in project root
- Configuring `~/.claude/settings.json`
- Understanding Claude Code vs VS Code MCP systems
- Verifying MCP tool availability
- Path configuration for all platforms

**Use this if:** You're using Claude Code extension in VS Code and want MCP tools available

---

### [ARCHITECTURE_DIAGRAM.md](setup/ARCHITECTURE_DIAGRAM.md)
Visual diagrams showing how the MCP server works

**What's inside:**
- Complete setup process flow
- Component architecture (Claude ↔ MCP Server ↔ Fabric API)
- Authentication flow with Azure CLI
- Configuration file structure
- Troubleshooting decision trees
- Common file paths for all platforms

**Use this if:** You want to understand how all the pieces fit together

---

### [INSTALLATION_CHECKLIST.md](setup/INSTALLATION_CHECKLIST.md)
Step-by-step installation checklist

**What's inside:**
- Prerequisites verification
- Project setup steps
- Azure authentication
- Path collection worksheet
- Configuration template
- Testing procedures
- Troubleshooting quick fixes

**Use this if:** You prefer a structured, checkbox approach to installation

---

## 📖 Usage Guides

**Directory:** [guides/](guides/)

### [pyspark_guide.md](guides/pyspark_guide.md)
Guide to using PySpark functionality with Fabric MCP tools

### [architecture.md](guides/architecture.md)
Detailed architecture and design documentation

---

## 🧪 Testing & Development

**Directory:** [testing/](testing/)

### [TESTING_AND_DEBUG_PLAN.md](testing/TESTING_AND_DEBUG_PLAN.md)
Comprehensive testing strategy and bug tracking

**What's inside:**
- Executive summary of test coverage
- Priority 1: Critical bugs to fix
- Priority 2: Core untested features
- Priority 3: Advanced features
- Testing matrix (76 tools across 14 categories)
- 4-week testing roadmap
- Test documentation templates

**Use this if:** You're contributing to the project and need to understand testing status

---

### [QUICK_TESTING_GUIDE.md](testing/QUICK_TESTING_GUIDE.md)
Fast-track testing guide

**What's inside:**
- 30-minute quick test sets
- One-day testing sprint plan
- Priority testing matrix
- Common troubleshooting checks
- Quick test documentation template

**Use this if:** You want to quickly verify functionality or run focused tests

---

## 🐛 Bug Fixes & Test Results

**Directory:** [bugfixes/](bugfixes/)

Contains detailed bug fix summaries, test results, and debugging notes.

### Latest: [SQL_MCP_BUGFIX_SUMMARY.md](bugfixes/SQL_MCP_BUGFIX_SUMMARY.md)
SQL MCP tools bug fixes (November 3, 2025)
- ✅ Bug #1: Workspace name resolution
- ✅ Bug #2: SQL error messages
- ✅ Bug #3: Connection string parsing

**See:** [bugfixes/README.md](bugfixes/README.md) for complete index

---

## 🖼️ Images & Screenshots

**Directory:** [images/](images/)

Contains screenshots and visual documentation:
- MCP Inspector screenshots
- VS Code integration images
- Architecture diagrams

---

## 🗂️ Quick Start Guide

### I want to use Claude Desktop to manage my Fabric workspace
1. Read [setup/CLAUDE_DESKTOP_SETUP.md](setup/CLAUDE_DESKTOP_SETUP.md)
2. Follow [setup/INSTALLATION_CHECKLIST.md](setup/INSTALLATION_CHECKLIST.md)
3. Reference [setup/ARCHITECTURE_DIAGRAM.md](setup/ARCHITECTURE_DIAGRAM.md) if stuck

### I want to use Claude Code in VS Code as a developer
1. Read [setup/CLAUDE_CODE_VSCODE_SETUP.md](setup/CLAUDE_CODE_VSCODE_SETUP.md)
2. This explains the differences between VS Code and Claude Code MCP configurations

### I want to understand how everything works
1. Read [setup/ARCHITECTURE_DIAGRAM.md](setup/ARCHITECTURE_DIAGRAM.md)
2. Review [guides/architecture.md](guides/architecture.md)

### I'm developing/testing this MCP server
1. Review [testing/TESTING_AND_DEBUG_PLAN.md](testing/TESTING_AND_DEBUG_PLAN.md)
2. Use [testing/QUICK_TESTING_GUIDE.md](testing/QUICK_TESTING_GUIDE.md) for rapid testing
3. Check [bugfixes/](bugfixes/) for known issues

### I'm helping a colleague set this up
1. Give them [setup/INSTALLATION_CHECKLIST.md](setup/INSTALLATION_CHECKLIST.md)
2. They can check off each step as they complete it

---

## 📋 Quick Reference by Platform

### Windows Users
- Claude Desktop config: `%APPDATA%\Claude\claude_desktop_config.json`
- Claude Code config: `C:\Users\YourName\.claude\settings.json`
- Python path: `C:\path\to\.venv\Scripts\python.exe`
- **Note:** Use double backslashes in JSON: `"C:\\Users\\..."`

### macOS Users
- Claude Desktop config: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Claude Code config: `~/.claude/settings.json`
- Python path: `/path/to/.venv/bin/python`
- **Note:** Use forward slashes: `"/Users/..."`

### Linux Users
- Claude Desktop config: `~/.config/Claude/claude_desktop_config.json`
- Claude Code config: `~/.claude/settings.json`
- Python path: `/path/to/.venv/bin/python`
- **Note:** Use forward slashes: `"/home/..."`

---

## 🆘 Common Questions

### What's the difference between Claude Desktop and Claude Code?
- **Claude Desktop** = Standalone chat application
- **Claude Code** = VS Code extension for coding
- They have **separate MCP configuration systems**

### Can I use both with this MCP server?
Yes! Configure each separately:
- Claude Desktop: `claude_desktop_config.json`
- Claude Code: `.mcp.json` + `~/.claude/settings.json`

### Why do I need both `.mcp.json` and `~/.claude/settings.json`?
- `.mcp.json` = MCP server configuration (per-project)
- `~/.claude/settings.json` = Enable MCP server (global setting)

---

## 🚀 Getting Started Checklist

- [ ] Read the appropriate setup guide
- [ ] Install prerequisites (Python 3.12+, Azure CLI, uv)
- [ ] Run `uv sync` to create virtual environment
- [ ] Authenticate with `az login`
- [ ] Configure Claude Desktop or Claude Code
- [ ] Test with "List all my Microsoft Fabric workspaces"
- [ ] Celebrate! 🎉

---

**Last Updated:** November 3, 2025
