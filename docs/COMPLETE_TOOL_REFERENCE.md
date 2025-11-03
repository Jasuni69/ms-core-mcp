# Complete MCP Tool Reference

This document provides a comprehensive reference for all 77 MCP tools available in the Microsoft Fabric MCP Server.

---

## 1. Workspace Management (3 tools)

### `list_workspaces`
List all available Fabric workspaces.
```python
list_workspaces()
# Usage: "List all my Fabric workspaces"
```

### `create_workspace`
Create a new Fabric workspace.
```python
create_workspace(
    display_name="Analytics-Workspace",
    capacity_id="00000000-0000-0000-0000-000000000000",  # Optional: trial capacity ID
    description="Analytics workspace for BI",  # Optional
    domain_id="domain-id"  # Optional
)
```

### `set_workspace`
Set the current workspace context for the session.
```python
set_workspace(workspace="Analytics-Workspace")
```

---

## 2. Warehouse Management (3 tools)

### `list_warehouses`
List all warehouses in a workspace.
```python
list_warehouses(workspace="Analytics-Workspace")
```

### `create_warehouse`
Create a new warehouse.
```python
create_warehouse(
    name="Sales-DW",
    workspace="Analytics-Workspace",
    description="Sales data warehouse",  # Optional
    folder_id="folder-id"  # Optional
)
```

### `set_warehouse`
Set current warehouse context.
```python
set_warehouse(warehouse="Sales-DW")
```

---

## 3. Lakehouse Management (3 tools)

### `list_lakehouses`
List all lakehouses in a workspace.
```python
list_lakehouses(workspace="Analytics-Workspace")
```

### `create_lakehouse`
Create a new lakehouse.
```python
create_lakehouse(
    name="Sales-Data-Lake",
    workspace="Analytics-Workspace",
    description="Sales data lakehouse",  # Optional
    folder_id="folder-id"  # Optional
)
```

### `set_lakehouse`
Set current lakehouse context.
```python
set_lakehouse(lakehouse="Sales-Data-Lake")
```

---

## 4. Table Operations (10 tools)

### `list_tables`
List all tables in a lakehouse.
```python
list_tables(workspace="Analytics-Workspace", lakehouse="Sales-Data-Lake")
```

### `set_table`
Set current table context.
```python
set_table(table_name="transactions")
```

### `get_lakehouse_table_schema`
Get schema for a specific table.
```python
get_lakehouse_table_schema(
    workspace="Analytics-Workspace",
    lakehouse="Sales-Data-Lake",
    table_name="transactions"
)
```

### `get_all_lakehouse_schemas`
Get schemas for all tables in a lakehouse.
```python
get_all_lakehouse_schemas(
    workspace="Analytics-Workspace",
    lakehouse="Sales-Data-Lake"
)
```

### `table_preview`
Preview rows from a Delta table through the SQL endpoint.
```python
table_preview(
    workspace="Analytics-Workspace",
    lakehouse="Sales-Data-Lake",
    table="transactions",
    limit=25
)
```

### `table_schema`
Retrieve detailed schema and metadata for a table.
```python
table_schema(
    workspace="Analytics-Workspace",
    lakehouse="Sales-Data-Lake",
    table="transactions"
)
```

### `describe_history`
Inspect the Delta transaction log history.
```python
describe_history(
    workspace="Analytics-Workspace",
    lakehouse="Sales-Data-Lake",
    table="transactions",
    limit=10
)
```

### `optimize_delta`
Compact files and optionally Z-Order a Delta table.
```python
optimize_delta(
    workspace="Analytics-Workspace",
    lakehouse="Sales-Data-Lake",
    table="transactions",
    zorder_by=["customer_id", "order_date"]
)
```

### `vacuum_delta`
Remove old files from Delta storage.
```python
vacuum_delta(
    workspace="Analytics-Workspace",
    lakehouse="Sales-Data-Lake",
    table="transactions",
    retain_hours=72
)
```

---

## 5. SQL Operations (4 tools)

### `sql_query`
Execute SQL against Fabric endpoints and receive structured rows.
```python
sql_query(
    workspace="Analytics-Workspace",
    lakehouse="Sales-Data-Lake",
    query="SELECT TOP 25 * FROM dbo.transactions",
    type="lakehouse",
    max_rows=100
)
```

### `sql_explain`
Retrieve estimated execution plans for SQL statements.
```python
sql_explain(
    workspace="Analytics-Workspace",
    lakehouse="Sales-Data-Lake",
    query="SELECT customer_id, SUM(amount) FROM dbo.transactions GROUP BY customer_id"
)
```

### `sql_export`
Export query results to OneLake as CSV or Parquet.
```python
sql_export(
    workspace="Analytics-Workspace",
    lakehouse="Sales-Data-Lake",
    query="SELECT * FROM dbo.transactions WHERE order_date >= '2024-01-01'",
    target_path="Files/exports/transactions_2024.csv",
    file_format="csv"
)
```

### `get_sql_endpoint`
Resolve connection details for a lakehouse or warehouse SQL endpoint.
```python
get_sql_endpoint(
    workspace="Analytics-Workspace",
    lakehouse="Sales-Data-Lake",
    type="lakehouse"
)
```

---

## 6. Notebook Management (19 tools)

### Basic Notebook Operations

#### `list_notebooks`
List all notebooks in a workspace.
```python
list_notebooks(workspace="Analytics-Workspace")
```

#### `create_notebook`
Create a new notebook.
```python
create_notebook(workspace="Analytics-Workspace")
```

#### `get_notebook_content`
Retrieve notebook content.
```python
get_notebook_content(
    workspace="Analytics-Workspace",
    notebook_id="notebook-id"
)
```

#### `update_notebook_cell`
Update specific notebook cells.
```python
update_notebook_cell(
    workspace="Analytics-Workspace",
    notebook_id="notebook-id",
    cell_index=0,
    cell_content="print('Hello, Fabric!')",
    cell_type="code"
)
```

### PySpark Notebook Creation

#### `create_pyspark_notebook`
Create notebooks from basic templates.
```python
create_pyspark_notebook(
    workspace="Analytics-Workspace",
    notebook_name="Data-Analysis",
    template_type="analytics"  # Options: basic, etl, analytics, ml
)
```

#### `create_fabric_notebook`
Create Fabric-optimized notebooks.
```python
create_fabric_notebook(
    workspace="Analytics-Workspace",
    notebook_name="Fabric-Pipeline",
    template_type="fabric_integration"  # Options: fabric_integration, streaming
)
```

### Code Generation

#### `generate_pyspark_code`
Generate code for common operations.
```python
generate_pyspark_code(
    operation="read_table",
    source_table="sales.transactions",
    columns="id,amount,date"
)
# Available operations: read_table, write_table, transform, join, aggregate
```

#### `generate_fabric_code`
Generate Fabric-specific code.
```python
generate_fabric_code(
    operation="read_lakehouse",
    lakehouse_name="Sales-Data-Lake",
    table_name="transactions"
)
# Available operations: read_lakehouse, write_lakehouse, merge_delta, performance_monitor
```

### Code Validation

#### `validate_pyspark_code`
Validate PySpark code syntax and best practices.
```python
validate_pyspark_code(code="""
df = spark.table('transactions')
df.show()
""")
```

#### `validate_fabric_code`
Validate Fabric compatibility.
```python
validate_fabric_code(code="""
df = spark.table('lakehouse.transactions')
df.write.format('delta').saveAsTable('summary')
""")
```

#### `analyze_notebook_performance`
Comprehensive performance analysis.
```python
analyze_notebook_performance(
    workspace="Analytics-Workspace",
    notebook_id="notebook-id"
)
```

### Notebook Execution

#### `run_notebook_job`
Submit a notebook job run with parameters.
```python
run_notebook_job(
    workspace="Analytics-Workspace",
    notebook="ETL-Pipeline",
    parameters={"date": "2024-01-01"},
    configuration={"defaultLakehouse": {"name": "Sales"}}
)
```

#### `get_run_status`
Check the status of a notebook run.
```python
get_run_status(
    workspace="Analytics-Workspace",
    notebook="ETL-Pipeline",
    job_id="job-id"
)
```

#### `cancel_notebook_job`
Cancel a running notebook job.
```python
cancel_notebook_job(
    workspace="Analytics-Workspace",
    notebook="ETL-Pipeline",
    job_id="job-id"
)
```

### Environment Management

#### `install_requirements`
Install Python requirements for workspace Spark environment.
```python
install_requirements(
    workspace="Analytics-Workspace",
    requirements_txt="pandas==2.0.0\\nscikit-learn==1.3.0"
)
```

#### `install_wheel`
Install a wheel package into workspace Spark environment.
```python
install_wheel(
    workspace="Analytics-Workspace",
    wheel_url="https://example.com/package.whl"
)
```

#### `cluster_info`
Retrieve Spark cluster information.
```python
cluster_info(workspace="Analytics-Workspace")
```

---

## 7. Semantic Model & DAX (9 tools)

### Model Operations

#### `list_semantic_models`
List semantic models in workspace.
```python
list_semantic_models(workspace="Analytics-Workspace")
```

#### `get_semantic_model`
Get specific semantic model.
```python
get_semantic_model(workspace="Analytics-Workspace", model_id="model-id")
```

#### `get_model_schema`
Get complete model schema with tables, columns, measures, and relationships.
```python
get_model_schema(
    workspace="Analytics-Workspace",
    model="Sales-Model"
)
```

### DAX Measure Management

#### `list_measures`
List all DAX measures in a semantic model.
```python
list_measures(
    workspace="Analytics-Workspace",
    model="Sales-Model"
)
```

#### `get_measure`
Get specific DAX measure definition by name.
```python
get_measure(
    measure_name="Total Revenue",
    workspace="Analytics-Workspace",
    model="Sales-Model"
)
```

#### `create_measure`
Create a new DAX measure.
```python
create_measure(
    measure_name="Total Revenue",
    dax_expression="SUM(Sales[Amount])",
    table_name="Sales",
    workspace="Analytics-Workspace",
    model="Sales-Model",
    format_string="$#,0.00",  # Optional
    description="Total sales revenue",  # Optional
    is_hidden=False  # Optional
)
```

#### `update_measure`
Update an existing DAX measure.
```python
update_measure(
    measure_name="Total Revenue",
    workspace="Analytics-Workspace",
    model="Sales-Model",
    dax_expression="SUM(Sales[Amount]) * 1.1",  # Optional
    format_string="$#,0.00",  # Optional
    description="Updated revenue calculation",  # Optional
    is_hidden=False,  # Optional
    new_name="Gross Revenue"  # Optional
)
```

#### `delete_measure`
Delete a DAX measure.
```python
delete_measure(
    measure_name="Total Revenue",
    workspace="Analytics-Workspace",
    model="Sales-Model"
)
```

### DAX Query & Analysis

#### `analyze_dax_query`
Analyze a DAX query for performance insights and execution plan.
```python
analyze_dax_query(
    dax_query="EVALUATE TOPN(10, Sales)",
    workspace="Analytics-Workspace",
    model="Sales-Model",
    include_execution_plan=True
)
```

---

## 8. Report Management (6 tools)

### Report Operations

#### `list_reports`
List all reports in a workspace.
```python
list_reports(workspace="Analytics-Workspace")
```

#### `get_report`
Get specific report details.
```python
get_report(workspace="Analytics-Workspace", report_id="report-id")
```

#### `report_export`
Export a report to PDF or PowerPoint.
```python
report_export(
    workspace="Analytics-Workspace",
    report="Executive-Summary",
    format="pdf"  # Options: pdf, pptx, png
)
```

#### `report_params_list`
List the parameter definitions for a report.
```python
report_params_list(
    workspace="Analytics-Workspace",
    report="Executive-Summary"
)
```

### Power BI Operations

#### `semantic_model_refresh`
Trigger a refresh for a semantic model.
```python
semantic_model_refresh(
    workspace="Analytics-Workspace",
    model="Sales-Model",
    refresh_type="Full"  # Options: Full, Automatic, DataOnly, Calculate, ClearValues
)
```

#### `dax_query`
Execute DAX against a semantic model.
```python
dax_query(
    workspace="Analytics-Workspace",
    dataset="Sales-Model",
    query="EVALUATE TOPN(10, 'DimCustomer')"
)
```

---

## 9. Pipeline & Dataflow (6 tools)

### Pipeline Operations

#### `pipeline_run`
Trigger a Fabric pipeline execution.
```python
pipeline_run(
    workspace="Analytics-Workspace",
    pipeline="Daily-Ingest",
    parameters={"RunDate": "2024-01-01"}
)
```

#### `pipeline_status`
Check the status of a pipeline run.
```python
pipeline_status(
    workspace="Analytics-Workspace",
    pipeline="Daily-Ingest",
    run_id="00000000-0000-0000-0000-000000000000"
)
```

#### `pipeline_logs`
Retrieve diagnostic logs for a pipeline run.
```python
pipeline_logs(
    workspace="Analytics-Workspace",
    pipeline="Daily-Ingest",
    run_id="00000000-0000-0000-0000-000000000000"
)
```

### Dataflow Operations

#### `dataflow_refresh`
Request a refresh for a Fabric Dataflow Gen2.
```python
dataflow_refresh(
    workspace="Analytics-Workspace",
    dataflow="Customer-Dim"
)
```

### Schedule Management

#### `schedule_list`
List refresh schedules for a workspace or specific item.
```python
schedule_list(workspace="Analytics-Workspace")
# or for a specific item
schedule_list(
    workspace="Analytics-Workspace",
    item="Sales-Model"
)
```

#### `schedule_set`
Create or update a refresh schedule for an item.
```python
schedule_set(
    workspace="Analytics-Workspace",
    item="Sales-Model",
    schedule={
        "frequency": "Daily",
        "timeZone": "UTC",
        "times": ["06:00"]
    }
)
```

---

## 10. Microsoft Graph Integration (8 tools)

### User & Directory

#### `graph_user`
Look up Azure AD profile details.
```python
graph_user(email="someone@contoso.com")
```

### Communication

#### `graph_mail`
Send an email using the signed-in identity.
```python
graph_mail(
    to="owner@contoso.com",
    subject="Fabric pipeline complete",
    body="<p>The nightly run succeeded.</p>"
)
```

### Teams Integration

#### `graph_teams_message`
Post a message to a Teams channel.
```python
graph_teams_message(
    team_id="00000000-0000-0000-0000-000000000000",
    channel_id="19:channel-id@thread.tacv2",
    text="Pipeline run finished with status Succeeded.",
    content_type="html"  # Options: html, text, markdown
)
```

#### `save_teams_channel_alias`
Create or update a named alias for a Teams channel.
```python
save_teams_channel_alias(
    alias="data-team",
    team_id="00000000-0000-0000-0000-000000000000",
    channel_id="19:channel-id@thread.tacv2"
)
```

#### `list_teams_channel_aliases`
List all saved Teams channel aliases.
```python
list_teams_channel_aliases()
```

#### `delete_teams_channel_alias`
Delete a saved Teams channel alias.
```python
delete_teams_channel_alias(alias="data-team")
```

#### `graph_teams_message_alias`
Post a message to a Teams channel using a saved alias.
```python
graph_teams_message_alias(
    alias="data-team",
    text="Pipeline completed successfully",
    content_type="html"
)
```

### File Operations

#### `graph_drive`
List files in OneDrive or SharePoint.
```python
graph_drive(
    drive_id="00000000-0000-0000-0000-000000000000",
    path="Shared Documents/Reports"
)
```

---

## 11. OneLake Operations (4 tools)

### `onelake_ls`
List files and folders within a OneLake path.
```python
onelake_ls(
    lakehouse="Sales-Data-Lake",
    path="Files/raw/customers",
    workspace="Analytics-Workspace"
)
```

### `onelake_read`
Read file contents from OneLake.
```python
onelake_read(
    lakehouse="Sales-Data-Lake",
    path="Files/raw/data.csv",
    workspace="Analytics-Workspace"
)
```

### `onelake_write`
Write content to OneLake.
```python
onelake_write(
    lakehouse="Sales-Data-Lake",
    path="Files/raw/new_data.csv",
    content="id,name,value\\n1,Test,100",
    workspace="Analytics-Workspace",
    overwrite=True,
    encoding="utf-8",
    is_base64=False
)
```

### `onelake_rm`
Delete a file or directory from OneLake.
```python
onelake_rm(
    lakehouse="Sales-Data-Lake",
    path="Files/raw/old_data.csv",
    workspace="Analytics-Workspace",
    recursive=False
)
```

---

## 12. Item & Permission Management (4 tools)

### `resolve_item`
Resolve an item name or ID to its canonical ID and metadata.
```python
resolve_item(
    workspace="Analytics-Workspace",
    name_or_id="Sales-Model",
    type="SemanticModel"
)
```

### `list_items`
List workspace items with optional filtering.
```python
list_items(
    workspace="Analytics-Workspace",
    type="Notebook",  # Optional filter
    search="sales",  # Optional search term
    top=100,
    skip=0
)
```

### `get_permissions`
Retrieve permission assignments for a workspace item.
```python
get_permissions(
    workspace="Analytics-Workspace",
    item_id="item-id"
)
```

### `set_permissions`
Set or update permissions for a workspace item.
```python
set_permissions(
    workspace="Analytics-Workspace",
    item_id="item-id",
    assignments=[
        {
            "principal": {"id": "user-id", "type": "User"},
            "role": "Contributor"
        }
    ],
    scope="All"
)
```

---

## 13. Data Loading (1 tool)

### `load_data_from_url`
Load data from URL into tables.
```python
load_data_from_url(
    url="https://example.com/data.csv",
    destination_table="new_data",
    workspace="Analytics-Workspace",
    lakehouse="Sales-Data-Lake"
)
```

---

## 14. Context Management (1 tool)

### `clear_context`
Clear current session context.
```python
clear_context()
```

---

## Summary

- **Total Tools:** 77
- **Workspace & Resource Management:** 10 tools
- **Data Operations:** 18 tools
- **Notebook & Code:** 19 tools
- **Semantic Models & DAX:** 9 tools
- **Reports & Power BI:** 6 tools
- **Pipelines & Automation:** 6 tools
- **Microsoft Graph:** 8 tools
- **Permissions & Items:** 4 tools

All tools support natural language interaction through Claude Desktop and Claude Code.
