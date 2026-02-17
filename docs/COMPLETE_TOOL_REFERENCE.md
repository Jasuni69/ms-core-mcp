# Microsoft Fabric MCP Server - Complete Tool Reference

**83 tools** across 15 categories. All tools support natural language interaction through Claude Desktop and Claude Code.

---

## Quick Reference

| Category | Tools | Description |
|----------|-------|-------------|
| [Workspace](#1-workspace-management) | 3 | List, create, set active workspace |
| [Lakehouse](#2-lakehouse-management) | 3 | List, create, set active lakehouse |
| [Warehouse](#3-warehouse-management) | 3 | List, create, set active warehouse |
| [Tables & Delta](#4-table--delta-operations) | 9 | Schema, preview, history, optimize, vacuum |
| [SQL](#5-sql-operations) | 4 | Query, explain, export, endpoint resolution |
| [Semantic Models & DAX](#6-semantic-models--dax) | 9 | Models, measures CRUD, DAX analysis |
| [Power BI](#7-power-bi) | 4 | DAX queries, model refresh, report export |
| [Reports](#8-reports) | 2 | List and get report details |
| [Notebooks](#9-notebooks) | 17 | Create, execute, code generation, validation |
| [Pipelines & Scheduling](#10-pipelines--scheduling) | 8 | Run, monitor, create pipelines; manage schedules |
| [OneLake](#11-onelake-storage) | 7 | File I/O, directory listing, shortcuts |
| [Data Loading](#12-data-loading) | 1 | Load CSV/Parquet from URL into delta tables |
| [Items & Permissions](#13-items--permissions) | 4 | Resolve items, workspace role assignments |
| [Microsoft Graph](#14-microsoft-graph) | 8 | Users, mail, Teams messaging, OneDrive |
| [Context](#15-context-management) | 1 | Clear session context |

---

## Context Flow

Most tools inherit context from previously set values. Typical setup:

```
set_workspace("my-workspace")   # Required first
set_lakehouse("my-lakehouse")   # Before table/SQL ops
set_warehouse("my-warehouse")   # Alternative to lakehouse
set_table("my_table")           # Optional, for repeated table ops
```

Once set, all subsequent tool calls use these values unless overridden by explicit parameters.

---

## 1. Workspace Management

### `list_workspaces`
List all Fabric workspaces accessible to the authenticated user.
```python
list_workspaces()
```

### `create_workspace`
Create a new Fabric workspace.
```python
create_workspace(
    display_name="Analytics-Prod",
    capacity_id="00000000-...",   # Optional: Fabric capacity ID
    description="Production analytics",  # Optional
    domain_id="domain-uuid"      # Optional
)
```

### `set_workspace`
Set the active workspace for the session. Required before most other operations.
```python
set_workspace(workspace="Analytics-Prod")
```

---

## 2. Lakehouse Management

### `list_lakehouses`
List all lakehouses in a workspace.
```python
list_lakehouses(workspace="Analytics-Prod")  # Or uses active workspace
```

### `create_lakehouse`
Create a new lakehouse.
```python
create_lakehouse(
    name="sales_lakehouse",
    workspace="Analytics-Prod",    # Optional if set
    description="Sales data lake", # Optional
    folder_id="folder-uuid"        # Optional
)
```

### `set_lakehouse`
Set the active lakehouse for table and SQL operations.
```python
set_lakehouse(lakehouse="sales_lakehouse")
```

---

## 3. Warehouse Management

### `list_warehouses`
List all warehouses in a workspace.
```python
list_warehouses(workspace="Analytics-Prod")
```

### `create_warehouse`
Create a new warehouse.
```python
create_warehouse(
    name="sales_dw",
    workspace="Analytics-Prod",
    description="Sales data warehouse",
    folder_id="folder-uuid"
)
```

### `set_warehouse`
Set the active warehouse for SQL operations.
```python
set_warehouse(warehouse="sales_dw")
```

---

## 4. Table & Delta Operations

### `list_tables`
List all delta tables in a lakehouse.
```python
list_tables(
    workspace="Analytics-Prod",   # Optional if set
    lakehouse="sales_lakehouse"   # Optional if set
)
```

### `set_table`
Set the active table for repeated operations.
```python
set_table(table_name="fact_sales")
```

### `table_preview`
Preview rows from a table via SQL endpoint.
```python
table_preview(
    table="fact_sales",           # Optional if set
    lakehouse="sales_lakehouse",  # Optional if set
    workspace="Analytics-Prod",   # Optional if set
    limit=50                      # Default: 50
)
```

### `table_schema`
Get table schema with column types and metadata.
```python
table_schema(
    table="fact_sales",
    lakehouse="sales_lakehouse",
    workspace="Analytics-Prod"
)
```

### `get_lakehouse_table_schema`
Get complete table schema from SQL endpoint (same as `table_schema`).
```python
get_lakehouse_table_schema(
    table_name="fact_sales",
    workspace="Analytics-Prod",
    lakehouse="sales_lakehouse"
)
```

### `get_all_lakehouse_schemas`
Get schemas for every table in a lakehouse in one call.
```python
get_all_lakehouse_schemas(
    lakehouse="sales_lakehouse",
    workspace="Analytics-Prod"
)
```

### `describe_history`
Get Delta Lake transaction log history. Uses delta-rs directly against OneLake.
```python
describe_history(
    table="fact_sales",
    lakehouse="sales_lakehouse",
    workspace="Analytics-Prod",
    limit=20   # Default: 20 most recent versions
)
```
Returns: version, timestamp, operation type, metrics (rows written, files added/removed).

### `optimize_delta`
Compact small files in a Delta table. Optionally apply Z-order clustering. Uses delta-rs directly.
```python
optimize_delta(
    table="fact_sales",
    lakehouse="sales_lakehouse",
    workspace="Analytics-Prod",
    zorder_by=["customer_id", "order_date"]  # Optional
)
```
Returns: files compacted, size before/after.

### `vacuum_delta`
Remove old files no longer referenced by the Delta log. Uses delta-rs directly.
```python
vacuum_delta(
    table="fact_sales",
    lakehouse="sales_lakehouse",
    workspace="Analytics-Prod",
    retain_hours=168  # Default: 7 days
)
```

---

## 5. SQL Operations

### `sql_query`
Execute T-SQL against a lakehouse or warehouse SQL endpoint.
```python
sql_query(
    query="SELECT TOP 25 * FROM dbo.fact_sales",
    workspace="Analytics-Prod",
    lakehouse="sales_lakehouse",
    type="lakehouse",   # "lakehouse" or "warehouse" - required
    max_rows=100        # Default: 100
)
```
**Note:** Lakehouse SQL endpoints are read-only (no INSERT/UPDATE/DELETE/DDL). Warehouse endpoints support full DDL/DML.

### `sql_explain`
Get estimated XML execution plan (SHOWPLAN) for a query.
```python
sql_explain(
    query="SELECT customer_id, SUM(amount) FROM dbo.fact_sales GROUP BY customer_id",
    type="lakehouse",
    workspace="Analytics-Prod",
    lakehouse="sales_lakehouse"
)
```

### `sql_export`
Export query results to OneLake as CSV or Parquet.
```python
sql_export(
    query="SELECT * FROM dbo.fact_sales WHERE year = 2024",
    target_path="Files/exports/sales_2024.csv",
    type="lakehouse",
    workspace="Analytics-Prod",
    lakehouse="sales_lakehouse",
    export_lakehouse="sales_lakehouse",  # Target lakehouse for output
    file_format="csv",     # "csv" or "parquet"
    overwrite=True
)
```

### `get_sql_endpoint`
Resolve connection details (server, database, connection string) for a lakehouse or warehouse.
```python
get_sql_endpoint(
    workspace="Analytics-Prod",
    lakehouse="sales_lakehouse",
    type="lakehouse"   # "lakehouse" or "warehouse"
)
```
Returns: `server`, `database`, `connectionString`.

---

## 6. Semantic Models & DAX

### `list_semantic_models`
List all semantic models in a workspace.
```python
list_semantic_models(workspace="Analytics-Prod")
```

### `get_semantic_model`
Get details for a specific semantic model.
```python
get_semantic_model(workspace="Analytics-Prod", model_id="model-uuid")
```

### `get_model_schema`
Get complete TMSL model schema (tables, columns, measures, relationships).
```python
get_model_schema(
    workspace="Analytics-Prod",
    model="Sales-Model"
)
```
**Note:** Only works with user-created semantic models. Auto-generated lakehouse default models return empty definitions.

### `list_measures`
List all DAX measures in a semantic model.
```python
list_measures(workspace="Analytics-Prod", model="Sales-Model")
```

### `get_measure`
Get a specific DAX measure definition by name.
```python
get_measure(
    measure_name="Total Revenue",
    workspace="Analytics-Prod",
    model="Sales-Model"
)
```

### `create_measure`
Create a new DAX measure in a semantic model.
```python
create_measure(
    measure_name="Total Revenue",
    dax_expression="SUM(Sales[Amount])",
    table_name="Sales",
    workspace="Analytics-Prod",
    model="Sales-Model",
    format_string="$#,0.00",          # Optional
    description="Total sales revenue", # Optional
    is_hidden=False                    # Optional, default False
)
```
**Note:** Requires user-created semantic model. Auto-generated lakehouse models don't support `getDefinition` API.

### `update_measure`
Update an existing DAX measure (expression, format, name, visibility).
```python
update_measure(
    measure_name="Total Revenue",
    workspace="Analytics-Prod",
    model="Sales-Model",
    dax_expression="SUM(Sales[Amount]) * 1.1",  # Optional
    format_string="$#,0.00",                     # Optional
    description="Updated calculation",            # Optional
    is_hidden=False,                              # Optional
    new_name="Gross Revenue"                      # Optional rename
)
```

### `delete_measure`
Delete a DAX measure from a semantic model.
```python
delete_measure(
    measure_name="Total Revenue",
    workspace="Analytics-Prod",
    model="Sales-Model"
)
```

### `analyze_dax_query`
Analyze a DAX query for performance (execution time, row count, metrics).
```python
analyze_dax_query(
    dax_query="EVALUATE TOPN(10, Sales)",
    workspace="Analytics-Prod",
    model="Sales-Model",
    include_execution_plan=True  # Default: True
)
```

---

## 7. Power BI

### `dax_query`
Execute DAX query against a Power BI dataset/semantic model via the Power BI REST API.
```python
dax_query(
    dataset="Sales-Model",
    query="EVALUATE TOPN(10, 'DimCustomer')",
    workspace="Analytics-Prod"
)
```

### `semantic_model_refresh`
Trigger a semantic model refresh via Power BI REST API.
```python
semantic_model_refresh(
    workspace="Analytics-Prod",
    model="Sales-Model",
    refresh_type="Full"  # Full | Automatic | DataOnly | Calculate | ClearValues
)
```

### `report_export`
Export a Power BI report to PDF or other formats.
```python
report_export(
    workspace="Analytics-Prod",
    report="Executive-Summary",
    format="pdf"  # pdf, pptx, png
)
```

### `report_params_list`
List parameter definitions for a report.
```python
report_params_list(
    workspace="Analytics-Prod",
    report="Executive-Summary"
)
```

---

## 8. Reports

### `list_reports`
List all reports in a workspace.
```python
list_reports(workspace="Analytics-Prod")
```

### `get_report`
Get specific report details by ID.
```python
get_report(workspace="Analytics-Prod", report_id="report-uuid")
```

---

## 9. Notebooks

### Basic Operations

#### `list_notebooks`
List all notebooks in a workspace.
```python
list_notebooks(workspace="Analytics-Prod")
```

#### `create_notebook`
Create a new notebook with optional content.
```python
create_notebook(
    workspace="Analytics-Prod",
    notebook_name="my_notebook",  # Default: "new_notebook"
    content="print('Hello')"     # Optional
)
```

#### `get_notebook_content`
Get full notebook content (cells, metadata, outputs) as JSON.
```python
get_notebook_content(
    workspace="Analytics-Prod",
    notebook_id="notebook-uuid"
)
```

#### `update_notebook_cell`
Update a specific cell in a notebook (0-based index).
```python
update_notebook_cell(
    workspace="Analytics-Prod",
    notebook_id="notebook-uuid",
    cell_index=0,
    cell_content="print('Updated!')",
    cell_type="code"  # "code" or "markdown"
)
```

### Template-Based Creation

#### `create_pyspark_notebook`
Create a PySpark notebook from a template.
```python
create_pyspark_notebook(
    workspace="Analytics-Prod",
    notebook_name="ETL-Pipeline",
    template_type="etl"  # basic | etl | analytics | ml
)
```

Templates:
- **basic**: SparkSession setup, sample read/transform/write
- **etl**: Bronze/silver/gold medallion pattern with Delta Lake
- **analytics**: Aggregations, window functions, visualization prep
- **ml**: Feature engineering, model training, evaluation

#### `create_fabric_notebook`
Create a Fabric-optimized notebook with Delta Lake and notebookutils integration.
```python
create_fabric_notebook(
    workspace="Analytics-Prod",
    notebook_name="Fabric-ETL",
    template_type="fabric_integration"  # fabric_integration | streaming
)
```

### Code Generation

#### `generate_pyspark_code`
Generate PySpark code for common operations.
```python
generate_pyspark_code(
    operation="aggregate",
    source_table="sales.transactions",
    columns="customer_id,amount",
    filter_condition="amount > 100"
)
```

Operations: `read_table`, `write_table`, `transform`, `join`, `aggregate`, `schema_inference`, `data_quality`, `performance_optimization`

#### `generate_fabric_code`
Generate Fabric-specific PySpark code.
```python
generate_fabric_code(
    operation="read_lakehouse",
    lakehouse_name="sales_lakehouse",
    table_name="fact_sales",
    target_table="fact_sales_clean"  # For write operations
)
```

Operations: `read_lakehouse`, `write_lakehouse`, `merge_delta`, `performance_monitor`

### Code Validation

#### `validate_pyspark_code`
Check PySpark code for syntax errors and best practice violations.
```python
validate_pyspark_code(code="df = spark.table('sales')\ndf.collect()")
```

#### `validate_fabric_code`
Validate PySpark code for Fabric compatibility and performance recommendations.
```python
validate_fabric_code(code="df = spark.table('lakehouse.sales')\ndf.write.format('delta').save()")
```

#### `analyze_notebook_performance`
Analyze an existing notebook for performance issues. Returns a score (0-100) with specific recommendations.
```python
analyze_notebook_performance(
    workspace="Analytics-Prod",
    notebook_id="notebook-uuid"
)
```
Detects: `.collect()` on large data, missing partitioning, UDF anti-patterns, etc.

### Execution

#### `run_notebook_job`
Submit a notebook for execution via the Fabric Job Scheduler.
```python
run_notebook_job(
    workspace="Analytics-Prod",
    notebook="ETL-Pipeline",
    parameters={"date": "2024-01-01"},         # Optional
    configuration={"defaultLakehouse": {...}}   # Optional
)
```
Returns: `job_id` for tracking.

#### `get_run_status`
Poll a notebook job until completion.
```python
get_run_status(
    workspace="Analytics-Prod",
    notebook="ETL-Pipeline",
    job_id="job-uuid"
)
```
Returns: status (Submitted/Running/Completed/Failed), timing details.

#### `cancel_notebook_job`
Cancel a running notebook job.
```python
cancel_notebook_job(
    workspace="Analytics-Prod",
    notebook="ETL-Pipeline",
    job_id="job-uuid"
)
```

### Spark Environment

#### `cluster_info`
Get Spark pool configuration, runtime version, and session timeout.
```python
cluster_info(workspace="Analytics-Prod")
```

#### `install_requirements`
Install Python packages in workspace Spark environment.
```python
install_requirements(
    workspace="Analytics-Prod",
    requirements_txt="pandas==2.0.0\nscikit-learn==1.3.0"
)
```
**Known bug:** Uses non-existent Spark endpoint. Fabric manages libraries through Environments - needs rewrite.

#### `install_wheel`
Install a wheel package in workspace Spark environment.
```python
install_wheel(
    workspace="Analytics-Prod",
    wheel_url="https://example.com/package.whl"
)
```
**Known bug:** Same issue as `install_requirements`.

---

## 10. Pipelines & Scheduling

### Pipeline Operations

#### `create_data_pipeline`
Create a Data Factory pipeline with activities and dependencies.
```python
create_data_pipeline(
    pipeline_name="daily_etl",
    pipeline_definition={
        "activities": [
            {
                "name": "RunNotebook",
                "type": "TridentNotebook",
                "typeProperties": {
                    "notebookId": "notebook-uuid"
                }
            }
        ]
    },
    workspace="Analytics-Prod",
    description="Daily ETL pipeline"  # Optional
)
```

#### `get_pipeline_definition`
Get an existing pipeline definition with decoded activities. Uses POST /getDefinition (LRO).
```python
get_pipeline_definition(
    pipeline="daily_etl",
    workspace="Analytics-Prod"
)
```

#### `pipeline_run`
Trigger a pipeline execution via the Fabric Job Scheduler API.
```python
pipeline_run(
    workspace="Analytics-Prod",
    pipeline="daily_etl",
    parameters={"RunDate": "2024-01-01"}  # Optional
)
```

#### `pipeline_status`
Get status of a pipeline run (uses Job Scheduler `/jobs/instances/{id}`).
```python
pipeline_status(
    workspace="Analytics-Prod",
    pipeline="daily_etl",
    run_id="job-instance-uuid"
)
```
Returns: status, start/end time, failure reason if applicable.

#### `pipeline_logs`
List job execution history for a pipeline. Without `run_id`, lists all recent instances.
```python
pipeline_logs(
    workspace="Analytics-Prod",
    pipeline="daily_etl",
    run_id="job-instance-uuid"  # Optional - omit for all runs
)
```

#### `dataflow_refresh`
Trigger a Dataflow Gen2 refresh.
```python
dataflow_refresh(
    workspace="Analytics-Prod",
    dataflow="customer_dim_refresh"
)
```

### Scheduling

#### `schedule_list`
List refresh schedules for an item. Auto-detects job type per item type.
```python
schedule_list(
    workspace="Analytics-Prod",
    item="daily_etl",
    job_type="DefaultJob"  # Auto-detected: Pipeline, RunNotebook, TableMaintenance, etc.
)
```

#### `schedule_set`
Create or update a refresh schedule. Uses Cron format.
```python
schedule_set(
    workspace="Analytics-Prod",
    item="daily_etl",
    job_type="Pipeline",
    schedule={
        "enabled": False,
        "configuration": {
            "type": "Cron",
            "interval": 1440,
            "localTimeZoneId": "UTC",
            "startDateTime": "2024-01-01T06:00:00"
        }
    }
)
```

---

## 11. OneLake Storage

### File Operations

#### `onelake_ls`
List files and folders in a OneLake path. Defaults to `Files/` directory.
```python
onelake_ls(
    lakehouse="sales_lakehouse",
    path="Files/raw/customers",  # Default: "Files"
    workspace="Analytics-Prod"
)
```
Use `path="Tables"` to list delta tables (uses Fabric API fallback since Tables/ is virtual).

#### `onelake_read`
Read file contents from OneLake.
```python
onelake_read(
    lakehouse="sales_lakehouse",
    path="Files/raw/data.csv",
    workspace="Analytics-Prod"
)
```

#### `onelake_write`
Write text or base64 content to OneLake.
```python
onelake_write(
    lakehouse="sales_lakehouse",
    path="Files/exports/output.csv",
    content="id,name,value\n1,Test,100",
    workspace="Analytics-Prod",
    overwrite=True,       # Default: True
    encoding="utf-8",     # Default: utf-8
    is_base64=False       # Default: False (set True for binary)
)
```

#### `onelake_rm`
Delete a file or directory from OneLake.
```python
onelake_rm(
    lakehouse="sales_lakehouse",
    path="Files/temp/old_file.csv",
    workspace="Analytics-Prod",
    recursive=False  # Default: False
)
```

### Shortcuts

Shortcuts reference data in another location without copying. Ideal for cross-lakehouse access.

#### `onelake_create_shortcut`
Create a shortcut from one lakehouse path to another.
```python
onelake_create_shortcut(
    lakehouse="target_lakehouse",
    shortcut_name="sales_data",
    shortcut_path="Files",
    target_workspace="source-workspace",
    target_lakehouse="source_lakehouse",
    target_path="Files/sales",
    workspace="Analytics-Prod",
    conflict_policy="CreateOrOverwrite"  # Default
)
```

#### `onelake_list_shortcuts`
List all shortcuts in a lakehouse.
```python
onelake_list_shortcuts(
    lakehouse="target_lakehouse",
    workspace="Analytics-Prod"
)
```

#### `onelake_delete_shortcut`
Delete a shortcut from a lakehouse.
```python
onelake_delete_shortcut(
    lakehouse="target_lakehouse",
    shortcut_path="Files",
    shortcut_name="sales_data",
    workspace="Analytics-Prod"
)
```

---

## 12. Data Loading

### `load_data_from_url`
Download CSV or Parquet from a URL and load into a delta table. Uses delta-rs for lakehouses (writes directly to OneLake), SQL DDL for warehouses.
```python
load_data_from_url(
    url="https://example.com/data.csv",
    destination_table="raw_customers",
    workspace="Analytics-Prod",   # Optional if set
    lakehouse="sales_lakehouse",  # Optional if set (falls back to context)
    warehouse="sales_dw"          # Alternative to lakehouse
)
```

**Note:** New delta tables take 5-10 minutes to appear in the lakehouse SQL endpoint. Use `onelake_ls(path="Tables")` to verify immediately.

---

## 13. Items & Permissions

### `resolve_item`
Resolve an item name or ID to its canonical UUID and metadata.
```python
resolve_item(
    workspace="Analytics-Prod",
    name_or_id="Sales-Model",
    type="SemanticModel"  # Optional filter
)
```

### `list_items`
List all workspace items with optional type filter and search.
```python
list_items(
    workspace="Analytics-Prod",
    type="Notebook",      # Optional: Notebook, Lakehouse, Warehouse, SemanticModel, etc.
    search="sales",       # Optional search term
    top=100,              # Default: 100 (max 500)
    skip=0                # Default: 0
)
```

### `get_permissions`
Get workspace role assignments (Admin, Member, Contributor, Viewer).
```python
get_permissions(
    workspace="Analytics-Prod",
    item_id="any-item-id"  # Parameter exists but workspace-level roles are returned
)
```
**Note:** Fabric REST API does not support item-level permissions. Returns workspace-level role assignments.

### `set_permissions`
Add a workspace role assignment.
```python
set_permissions(
    workspace="Analytics-Prod",
    principal_id="user-or-group-uuid",
    principal_type="User",     # User | Group | ServicePrincipal
    role="Contributor"         # Admin | Member | Contributor | Viewer
)
```

---

## 14. Microsoft Graph

### User & Directory

#### `graph_user`
Look up Azure AD user profile. Use `"me"` for the authenticated user.
```python
graph_user(email="me")
graph_user(email="someone@contoso.com")
```

### Communication

#### `graph_mail`
Send email from the authenticated user's mailbox.
```python
graph_mail(
    to="owner@contoso.com",
    subject="Pipeline complete",
    body="<p>The nightly run succeeded.</p>"
)
```

### Teams Integration

#### `graph_teams_message`
Post a message to a Teams channel.
```python
graph_teams_message(
    team_id="team-uuid",
    channel_id="19:channel-id@thread.tacv2",
    text="Pipeline finished successfully.",
    content_type="html"  # html | text | markdown
)
```

#### `graph_teams_message_alias`
Post a message using a saved channel alias (no need to remember IDs).
```python
graph_teams_message_alias(
    alias="data-team",
    text="Daily ETL complete.",
    content_type="html"
)
```

#### `save_teams_channel_alias`
Save a team/channel ID pair under a friendly name.
```python
save_teams_channel_alias(
    alias="data-team",
    team_id="team-uuid",
    channel_id="19:channel-id@thread.tacv2"
)
```

#### `list_teams_channel_aliases`
List all saved aliases.
```python
list_teams_channel_aliases()
```

#### `delete_teams_channel_alias`
Delete a saved alias.
```python
delete_teams_channel_alias(alias="data-team")
```

### File Operations

#### `graph_drive`
List files in a OneDrive or SharePoint drive. Use `"me"` for the current user's OneDrive.
```python
graph_drive(drive_id="me", path="Documents/Reports")
graph_drive(drive_id="drive-uuid", path="Shared Documents")
```

---

## 15. Context Management

### `clear_context`
Clear all session context (workspace, lakehouse, warehouse, table).
```python
clear_context()
```

---

## Fabric REST API Capabilities

The MCP server communicates with Microsoft Fabric through several APIs:

### Fabric REST API (`https://api.fabric.microsoft.com/v1`)
- **Workspaces**: List, create, manage role assignments
- **Items**: List, resolve, get/set permissions (workspace-level)
- **Lakehouses**: List, create, get tables, get SQL endpoints
- **Warehouses**: List, create, get SQL endpoints
- **Notebooks**: List, create (POST /getDefinition LRO), get content, update cells
- **Pipelines**: Create, get definition (POST /getDefinition LRO), run/monitor via Job Scheduler
- **Semantic Models**: List, get, get/update definitions (POST with LRO)
- **Reports**: List, get details
- **Schedules**: List and set schedules per item with auto-detected job types
- **Spark**: Get cluster/pool settings
- **OneLake Shortcuts**: Create, list, delete (via Fabric Items API)
- **Long-Running Operations**: Automatic polling with retry-after headers

### Power BI REST API (`https://api.powerbi.com/v1.0/myorg`)
- **DAX Queries**: Execute via `/datasets/{id}/executeQueries`
- **Semantic Model Refresh**: Trigger via `/datasets/{id}/refreshes`
- **Report Export**: Export to PDF/PPTX/PNG
- **Report Parameters**: List parameter definitions

### Microsoft Graph API (`https://graph.microsoft.com/v1.0`)
- **Users**: Profile lookup (`/users/{email}`, `/me`)
- **Mail**: Send email (`/me/sendMail`)
- **Teams**: Post channel messages, manage channel aliases
- **OneDrive**: Browse files (`/me/drive/root/children`, `/drives/{id}/root/children`)

### OneLake ADLS Gen2 (`https://onelake.dfs.fabric.microsoft.com`)
- **File I/O**: Read, write, delete files via Azure Data Lake Storage Gen2 API
- **Directory Listing**: List files and folders
- **Delta Table Operations**: Direct delta-rs access for optimize, vacuum, history, and data loading

### SQL Endpoints (TDS/ODBC)
- **Lakehouse SQL**: Read-only T-SQL against lakehouse tables (auto-provisioned)
- **Warehouse SQL**: Full T-SQL with DDL/DML support
- **Execution Plans**: SHOWPLAN XML via SET SHOWPLAN_XML

---

## Known Limitations

| Tool | Issue |
|------|-------|
| `install_requirements` | Uses non-existent Spark endpoint. Fabric manages libraries through Environments API. |
| `install_wheel` | Same as above. |
| `create_measure` / `update_measure` / `delete_measure` | Only works with user-created semantic models. Auto-generated lakehouse default models don't support `getDefinition`. |
| `get_model_schema` | Same limitation as measure tools. |
| `set_permissions` | Workspace-level only. Fabric REST API doesn't support item-level permissions. |
| Lakehouse SQL | Read-only. No INSERT/UPDATE/DELETE/DDL. New delta tables take 5-10 min to appear. |

---

## Authentication

All tools authenticate via Azure CLI (`az login`). The server uses `DefaultAzureCredential` with different token scopes per API:

| API | Token Scope |
|-----|------------|
| Fabric REST API | `https://api.fabric.microsoft.com/.default` |
| Power BI API | `https://analysis.windows.net/powerbi/api/.default` |
| Microsoft Graph | `https://graph.microsoft.com/.default` |
| OneLake Storage | `https://storage.azure.com/.default` |
| SQL Endpoints | `https://database.windows.net/.default` |
