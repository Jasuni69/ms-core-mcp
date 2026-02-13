# Microsoft Fabric MCP Tools

MCP server exposing 77+ Fabric tools via STDIO/HTTP. Covers workspaces, lakehouses, warehouses, SQL, DAX, semantic models, notebooks, pipelines, OneLake, and Microsoft Graph.

## First-Time Setup
If the user just cloned this repo and needs help setting up, guide them through these steps:

1. Check prerequisites: Python 3.12+, uv, Azure CLI must be installed
2. Run `az login` to authenticate (opens browser - user must complete this)
3. Run `python setup.py` in the project root - it checks everything, installs deps, and configures Claude Code / Claude Desktop
4. After setup.py completes, user must reload VS Code window or restart Claude Desktop
5. Test by asking "List my Fabric workspaces"

If setup.py reports failures, help the user fix each one before continuing.
IMPORTANT: setup.py safely merges into existing config files - it will NOT delete other MCP servers.

## Context Flow
- Always `set_workspace` before other operations
- Always `set_lakehouse` or `set_warehouse` before SQL/table operations
- Use `list_tables` or `SELECT TOP 1 *` to discover schema before writing queries

## SQL
- Always pass `type` ("lakehouse" or "warehouse") to sql_query, sql_explain, sql_export
- Fabric SQL endpoints are read-only - no INSERT/UPDATE/DELETE/DDL
- New delta tables take 5-10 min to appear in SQL endpoint
- Use T-SQL dialect with FORMAT() for readable numbers
- Column names vary per dataset - always check schema first

## Data Questions
- Translate natural language to SQL automatically - don't ask, just query
- Format results as markdown tables
- Default to TOP 20 for ranked queries
- Suggest follow-up analyses when relevant

## Semantic Models & DAX
- Add descriptions when creating measures
- Use format strings (e.g., "#,0.00", "0.0%") on measures
- When gold tables are created, suggest relevant DAX measures

## OneLake
- `onelake_ls` browses Files path by default - use `path: "Tables"` for delta tables
- Shortcuts reference data without copying - prefer over duplication

## Notebooks
- Use `create_pyspark_notebook` with templates (basic, etl, analytics, ml)
- `run_notebook_job` + `get_run_status` to execute and poll

## Naming Conventions
- Bronze: `{source}_{entity}_raw`
- Silver: `{entity}_clean`
- Gold: `fact_{entity}`, `dim_{entity}`
- Measures: `Total {Metric}`, `{Metric} YTD`, `{Metric} Growth %`

## Code Style
- Python: PEP 8, type hints, f-strings
- SQL: T-SQL, uppercase keywords
- Files under 300 lines
