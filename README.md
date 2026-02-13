# Microsoft Fabric MCP Server

A Python MCP server that lets you manage Microsoft Fabric through natural language in Claude Code or Claude Desktop. 77+ tools covering workspaces, lakehouses, warehouses, SQL, DAX, semantic models, notebooks, pipelines, OneLake, and Microsoft Graph.

Inspired by: https://github.com/Augustab/microsoft_fabric_mcp/tree/main

## Quick Start

```bash
git clone https://github.com/Jasuni69/ms-core-mcp.git
cd ms-core-mcp
az login
python setup.py
```

The setup script checks prerequisites, installs dependencies, and configures your Claude client. It safely merges into existing config files without affecting other MCP servers.

Then restart VS Code or Claude Desktop and ask: **"List my Fabric workspaces"**

## Prerequisites

- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **uv** package manager - [Install](https://docs.astral.sh/uv/getting-started/installation/)
- **Azure CLI** - [Install](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- **ODBC Driver 18** (optional, for SQL tools) - [Download](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- Access to a **Microsoft Fabric workspace** with Contributor or Admin role

## How It Works

```
You (natural language) --> Claude --> MCP Server --> Fabric REST API --> Your Fabric Resources
```

Two transport modes:
- **STDIO** (default) - `fabric_mcp_stdio.py` - used by Claude Code and Claude Desktop
- **HTTP** - `fabric_mcp.py --port 8081` - for custom integrations

## Tools (77+)

### Workspace & Resource Management (9 tools)
`list_workspaces`, `create_workspace`, `set_workspace`, `list_lakehouses`, `create_lakehouse`, `set_lakehouse`, `list_warehouses`, `create_warehouse`, `set_warehouse`

### Delta Table Operations (10 tools)
`list_tables`, `set_table`, `get_lakehouse_table_schema`, `get_all_lakehouse_schemas`, `table_preview`, `table_schema`, `describe_history`, `optimize_delta`, `vacuum_delta`, `load_data_from_url`

### SQL (4 tools)
`sql_query`, `sql_explain`, `sql_export`, `get_sql_endpoint`

- Always pass `type` ("lakehouse" or "warehouse")
- SQL endpoints are **read-only** - no DDL/DML
- New delta tables take 5-10 min to appear in SQL endpoint
- Requires ODBC Driver 18

### Semantic Models & DAX (9 tools)
`list_semantic_models`, `get_semantic_model`, `get_model_schema`, `list_measures`, `get_measure`, `create_measure`, `update_measure`, `delete_measure`, `analyze_dax_query`

### Reports (4 tools)
`list_reports`, `get_report`, `report_export`, `report_params_list`

### Power BI (2 tools)
`semantic_model_refresh`, `dax_query`

### Notebooks (16 tools)
`list_notebooks`, `create_notebook`, `get_notebook_content`, `update_notebook_cell`, `create_pyspark_notebook`, `create_fabric_notebook`, `generate_pyspark_code`, `generate_fabric_code`, `validate_pyspark_code`, `validate_fabric_code`, `analyze_notebook_performance`, `run_notebook_job`, `get_run_status`, `cancel_notebook_job`, `install_requirements`, `install_wheel`, `cluster_info`

### Pipelines & Scheduling (8 tools)
`pipeline_run`, `pipeline_status`, `pipeline_logs`, `create_data_pipeline`, `get_pipeline_definition`, `dataflow_refresh`, `schedule_list`, `schedule_set`

### OneLake File Operations (7 tools)
`onelake_ls`, `onelake_read`, `onelake_write`, `onelake_rm`, `onelake_create_shortcut`, `onelake_list_shortcuts`, `onelake_delete_shortcut`

### Items & Permissions (4 tools)
`resolve_item`, `list_items`, `get_permissions`, `set_permissions`

### Microsoft Graph (8 tools)
`graph_user`, `graph_mail`, `graph_teams_message`, `graph_teams_message_alias`, `graph_drive`, `save_teams_channel_alias`, `list_teams_channel_aliases`, `delete_teams_channel_alias`

### Session (1 tool)
`clear_context`

## Example Usage

```
"List all my Fabric workspaces"
"Set workspace to Analytics-Prod"
"Show me all tables in the sales lakehouse"
"What are the top 10 customers by revenue?"
"Create a DAX measure for total sales"
"Generate a PySpark ETL notebook"
"Run the daily pipeline and check status"
```

## Manual Setup (without setup.py)

### Claude Code (VS Code)

Create `.mcp.json` in the project root:
```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "uv",
      "args": ["--directory", "/full/path/to/ms-core-mcp", "run", "fabric_mcp_stdio.py"]
    }
  }
}
```

Add to `~/.claude/settings.json`:
```json
{
  "enableAllProjectMcpServers": true
}
```

### Claude Desktop

Add to your `claude_desktop_config.json`:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ms-fabric-core-tools-mcp": {
      "command": "/full/path/to/uv",
      "args": ["--directory", "/full/path/to/ms-core-mcp", "run", "fabric_mcp_stdio.py"]
    }
  }
}
```

Note: Claude Desktop needs the **full path** to `uv` since it may not inherit your shell PATH.

## Project Structure

```
ms-core-mcp/
  fabric_mcp.py          # HTTP server entry point
  fabric_mcp_stdio.py    # STDIO entry point (Claude Code / Desktop)
  setup.py               # Automated setup script
  pyproject.toml          # Dependencies
  CLAUDE.md              # AI assistant instructions
  tools/                 # MCP tool definitions
  helpers/
    clients/             # Fabric API, SQL, OneLake clients
    formatters/          # Output formatters
    utils/               # Auth, context, validators
  tests/                 # Tests
  docs/                  # Documentation
```

## Known Limitations

- **SQL endpoints are read-only** - use PySpark notebooks for writes
- **SQL sync delay** - new tables take 5-10 min to appear
- **API rate limits** - 50 requests/min/user (Fabric), 120 queries/min/user (Power BI)
- **Notebook lakehouse attachment** - must be done manually in Fabric UI
- **ODBC Driver 18 required** for sql_query, table_preview, sql_explain tools
- **Report creation not supported** - can list, export, view params only

## Troubleshooting

**"Command not found: uv"** - Install uv, then restart terminal

**"Not authenticated"** - Run `az login`, then verify with:
```bash
az account get-access-token --resource https://api.fabric.microsoft.com/
```

**"Database not found" on SQL queries** - SQL endpoint may not be provisioned yet. Wait a few minutes or check the lakehouse has tables in the Fabric portal.

**MCP tools not appearing in Claude Desktop** - Use full path to `uv` in config. Check Task Manager to fully close and restart Claude Desktop.

**Only some tools showing** - Check for import errors by running:
```bash
uv run python -c "from tools import *; from helpers.utils.context import mcp; print(f'Tools: {len(mcp._tool_manager._tools)}')"
```

## Testing

```bash
uv run pytest tests/
```

## License

MIT
