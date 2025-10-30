# Setup Process Diagram

## Visual Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     SETUP PROCESS OVERVIEW                       │
└─────────────────────────────────────────────────────────────────┘

Step 1: Install Prerequisites
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Python 3.12 │  │Claude Desktop│  │  Azure CLI   │  │      uv      │
│      +       │  │              │  │              │  │  (optional)  │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
                           ↓
Step 2: Project Setup
┌─────────────────────────────────────────────────────────────────┐
│  Terminal:  cd ms-fabric-core-tools-mcp && uv sync              │
│  Result:    .venv/ directory created with dependencies          │
└─────────────────────────────────────────────────────────────────┘
                           ↓
Step 3: Azure Authentication
┌─────────────────────────────────────────────────────────────────┐
│  Terminal:  az login                                             │
│  Browser:   Login with your Azure account                       │
│  Verify:    az account get-access-token --resource https://...  │
└─────────────────────────────────────────────────────────────────┘
                           ↓
Step 4: Configure Claude Desktop
┌─────────────────────────────────────────────────────────────────┐
│  File:      %APPDATA%\Claude\claude_desktop_config.json         │
│  Edit:      Add ms-fabric-core-tools-mcp configuration          │
│  Paths:     Update with YOUR actual paths                       │
│  Validate:  Check JSON syntax                                   │
└─────────────────────────────────────────────────────────────────┘
                           ↓
Step 5: Restart & Test
┌─────────────────────────────────────────────────────────────────┐
│  Action:    Close Claude Desktop completely                     │
│  Action:    Restart Claude Desktop                              │
│  Test:      "List all my Microsoft Fabric workspaces"           │
│  Success:   ✅ See your workspaces!                             │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        YOUR MACHINE                               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │              Claude Desktop App                         │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │  User: "List my Fabric workspaces"              │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  │                        ↓                                │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │  Claude AI (LLM)                                 │  │     │
│  │  │  Interprets natural language                     │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  │                        ↓                                │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │  MCP Protocol                                    │  │     │
│  │  │  Calls: list_workspaces tool                    │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────────────┘     │
│                        ↓ STDIO                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  ms-fabric-core-tools-mcp MCP Server (Python)          │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │  • Receives tool calls via STDIO                │  │     │
│  │  │  • Authenticates with Azure CLI credentials     │  │     │
│  │  │  • Makes HTTP requests to Fabric API            │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────────────┘     │
│                        ↓ HTTPS                                   │
└──────────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│                   Microsoft Fabric (Cloud)                        │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Fabric API (api.fabric.microsoft.com)                 │     │
│  │  • Workspaces                                          │     │
│  │  • Lakehouses                                          │     │
│  │  • Warehouses                                          │     │
│  │  • Notebooks                                           │     │
│  │  • Tables                                              │     │
│  └────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
                         ↑
                         │
            Results flow back up the chain
```

## Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW                           │
└─────────────────────────────────────────────────────────────────┘

1. Initial Setup (One Time)
   ┌──────────────┐
   │  az login    │──→  Browser opens  ──→  Login to Azure
   └──────────────┘                          │
                                             ↓
                                    ┌─────────────────┐
                                    │ Token saved in  │
                                    │ ~/.azure/       │
                                    └─────────────────┘

2. Runtime Authentication (Every Request)
   ┌──────────────────────┐
   │  Claude Desktop      │
   │  starts MCP server   │
   └──────────────────────┘
             ↓
   ┌──────────────────────────────────────┐
   │  MCP Server (Python)                 │
   │  Uses DefaultAzureCredential()       │
   │  → Checks environment variables      │
   │  → Checks Azure CLI credentials ✓    │
   │  → Reads token from ~/.azure/        │
   └──────────────────────────────────────┘
             ↓
   ┌──────────────────────────────────────┐
   │  HTTP Request to Fabric API          │
   │  Headers: Authorization: Bearer XXX  │
   └──────────────────────────────────────┘
             ↓
   ┌──────────────────────────────────────┐
   │  Microsoft Fabric validates token    │
   │  Returns workspace/lakehouse data    │
   └──────────────────────────────────────┘
```

## Configuration File Structure

```
claude_desktop_config.json
├── mcpServers                    ← Top-level object
│   └── ms-fabric-core-tools-mcp ← Your server name
│       ├── command               ← Path to Python executable
│       ├── args                  ← Array with script path
│       └── env                   ← Environment variables
│           └── USERPROFILE       ← Needed for Azure CLI auth
```

## File Structure After Setup

```
ms-fabric-core-tools-mcp/
├── .venv/                              ← Virtual environment (created by uv sync)
│   ├── Scripts/python.exe              ← Python executable (Windows)
│   └── bin/python                      ← Python executable (macOS/Linux)
├── helpers/                            ← Helper modules
│   ├── clients/                        ← API clients
│   └── utils/                          ← Utilities
├── tools/                              ← MCP tool definitions
│   ├── workspace.py                    ← Workspace tools
│   ├── lakehouse.py                    ← Lakehouse tools
│   └── ...
├── fabric_mcp.py                       ← HTTP server (optional)
├── fabric_mcp_stdio.py                 ← STDIO server (recommended)
├── pyproject.toml                      ← Python dependencies
├── README.md                           ← Full documentation
├── SETUP.md                            ← Quick setup guide
├── INSTALLATION_CHECKLIST.md           ← Step-by-step checklist
├── CLAUDE_DESKTOP_CONFIG_EXAMPLE.json  ← Example config
└── SETUP_DIAGRAM.md                    ← This file!
```

## Troubleshooting Decision Tree

```
Is Claude Desktop showing the ms-fabric-core-tools-mcp server?
│
├─ NO
│  │
│  ├─ Check config file path is correct
│  ├─ Validate JSON syntax
│  ├─ Verify Python path is correct
│  ├─ Verify .venv exists
│  └─ Restart Claude Desktop
│
└─ YES
   │
   Can you list workspaces?
   │
   ├─ NO
   │  │
   │  ├─ Authentication issue
   │  │  └─ Run: az login
   │  │
   │  ├─ Path issue
   │  │  └─ Check USERPROFILE/HOME env var
   │  │
   │  └─ Permission issue
   │     └─ Verify Fabric workspace access
   │
   └─ YES
      │
      Can you create resources?
      │
      ├─ NO
      │  │
      │  └─ Permission issue
      │     └─ Need Contributor/Admin role
      │
      └─ YES → ✅ Everything works!
```

## Quick Command Reference

### Testing Connection
```bash
# Test Python
python --version

# Test Azure CLI
az --version

# Test Azure login
az login

# Test Fabric API access
az account get-access-token --resource https://api.fabric.microsoft.com/

# Test MCP server directly
.venv/Scripts/python fabric_mcp_stdio.py  # Windows
.venv/bin/python fabric_mcp_stdio.py      # macOS/Linux
```

### Common Paths

**Windows:**
- Config: `%APPDATA%\Claude\claude_desktop_config.json`
- Python: `C:\path\to\.venv\Scripts\python.exe`
- Script: `C:\path\to\fabric_mcp_stdio.py`
- Home: `C:\Users\YourUsername`

**macOS:**
- Config: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Python: `/path/to/.venv/bin/python`
- Script: `/path/to/fabric_mcp_stdio.py`
- Home: `/Users/yourusername`

**Linux:**
- Config: `~/.config/Claude/claude_desktop_config.json`
- Python: `/path/to/.venv/bin/python`
- Script: `/path/to/fabric_mcp_stdio.py`
- Home: `/home/yourusername`

---

**Visual learner?** Use this diagram to understand the setup process!
**Need step-by-step?** See [INSTALLATION_CHECKLIST.md](INSTALLATION_CHECKLIST.md)
**Want quick setup?** See [SETUP.md](SETUP.md)
