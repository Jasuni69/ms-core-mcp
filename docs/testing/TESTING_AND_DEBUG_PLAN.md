# 🧪 Microsoft Fabric MCP Tools - Testing & Debug Plan

**Date:** November 3, 2025  
**Based on:** Notion page analysis and codebase review

---

## 📊 Executive Summary

### Current Test Coverage:
- **Well Tested:** 20+ tools (workspaces, lakehouses, tables, OneLake, notebooks creation, reports, semantic models)
- **Partially Tested:** 5 tools (warehouse creation, SQL queries, notebook content)
- **Untested:** 40+ tools (notebook execution, pipelines, Power BI, permissions, Graph API, Delta operations)

### Critical Findings:
1. ✅ **Major Discovery:** Notebook execution tools (`run_notebook_job`, `get_run_status`, `cancel_notebook_job`) exist but were not tested!
2. ⚠️ **LRO Bug:** Warehouse and notebook creation work but return misleading error messages
3. ❌ **Broken:** `update_notebook_cell` has JSON parsing errors
4. 🔍 **Untested:** Extensive Power BI, pipeline, and permission management capabilities

---

## 🎯 Priority 1: Fix Critical Bugs

### 1. LRO Response Handling (Warehouse & Notebook Creation)

**Issue:** Functions create items successfully but return error messages to users.

**Affected Tools:**
- `create_warehouse` (tools/warehouse.py)
- `create_pyspark_notebook` (tools/notebook.py)
- `create_fabric_notebook` (tools/notebook.py)
- `create_notebook` (tools/notebook.py)

**Root Cause Analysis:**
Located in `helpers/clients/fabric_client.py` (lines 551-585):
```python
# When LRO completes, response might be empty dict or status object
if lro and (len(response) == 0 or response.get("status") in ("Succeeded", ...)):
    # Tries to fetch item by name after 2 second wait
    # If not found immediately, logs warning but returns empty response
```

**Problem:** The function returns the empty LRO response instead of the fetched item details, causing tools to report errors even though creation succeeded.

**Recommended Fix:**
```python
# In fabric_client.py create_item method (line ~551)
if lro and (len(response) == 0 or response.get("status") in ("Succeeded", "succeeded", "Completed", "completed")):
    logger.info(f"LRO completed. Fetching item '{name}' details...")
    try:
        # Increase wait time for item propagation
        import asyncio
        await asyncio.sleep(3)  # Change from time.sleep(2) to async sleep
        
        items = await self.get_items(workspace_id=workspace_id, item_type=type)
        if items and isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and item.get("displayName") == name:
                    logger.info(f"Successfully found created item '{name}'")
                    return item  # Return the found item
        
        # If not found, return a success indicator with name
        logger.warning(f"Item '{name}' created but details not immediately available")
        return {"displayName": name, "status": "Created", "note": "Details will be available shortly"}
        
    except Exception as fetch_error:
        logger.error(f"Failed to fetch item after LRO: {fetch_error}")
        # Still return success indicator
        return {"displayName": name, "status": "Created", "error": str(fetch_error)}
```

**Test Plan:**
1. Create warehouse in test workspace
2. Verify successful creation message
3. Confirm warehouse exists via `list_warehouses`
4. Create notebook via `create_pyspark_notebook`
5. Verify successful creation message
6. Confirm notebook exists via `list_notebooks`

---

### 2. Notebook Cell Update JSON Parsing Error

**Issue:** `update_notebook_cell` fails with: `'Expecting value: line 1 column 1 (char 0)'`

**Affected Tool:** `update_notebook_cell` (tools/notebook.py, line ~1163)

**Likely Causes:**
1. Empty response from Fabric API when updating notebook definition
2. Notebook definition endpoint returns 204 No Content instead of JSON
3. Response encoding/decoding issue

**Debug Steps:**
1. Check what Fabric API returns for notebook update operations
2. Verify if the API expects PUT vs PATCH
3. Review response handling in `_make_request` for update operations
4. Check if notebooks need to be in specific state before updating

**Recommended Investigation:**
```python
# Add debug logging to update_notebook_cell
logger.debug(f"Updating cell {cell_index} in notebook {notebook_id}")
logger.debug(f"Request payload: {payload}")

response = await client._make_request(...)
logger.debug(f"Response type: {type(response)}")
logger.debug(f"Response content: {response}")
```

**Test Plan:**
1. Create test notebook with `create_pyspark_notebook`
2. Attempt to update cell 0 with simple code
3. Check logs for response details
4. Try alternative: Get notebook content, modify locally, update entire definition

---

## 🧪 Priority 2: Test Critical Untested Features

### 1. Notebook Execution (MAJOR DISCOVERY!)

**Status:** ✅ Code exists, ❓ Not tested in Notion page

**Available Tools:**
- `run_notebook_job(workspace, notebook, parameters, configuration)` - Execute notebooks!
- `get_run_status(workspace, notebook, job_id)` - Monitor execution
- `cancel_notebook_job(workspace, notebook, job_id)` - Cancel execution

**Test Scenarios:**

#### Test 1: Basic Notebook Execution
```python
# 1. Create a simple PySpark notebook
create_pyspark_notebook(workspace="test-workspace", notebook_name="test_execution", template_type="basic")

# 2. Run the notebook
run_notebook_job(workspace="test-workspace", notebook="test_execution")

# 3. Check status
get_run_status(workspace="test-workspace", notebook="test_execution", job_id="<from_run_response>")
```

#### Test 2: Parameterized Execution
```python
# Run notebook with parameters
run_notebook_job(
    workspace="test-workspace",
    notebook="data_processing_nb",
    parameters={
        "input_table": "raw_data",
        "output_table": "processed_data",
        "date": "2025-11-03"
    }
)
```

#### Test 3: Execution with Configuration
```python
# Run with custom Spark configuration
run_notebook_job(
    workspace="test-workspace",
    notebook="ml_training",
    configuration={
        "spark.executor.memory": "4g",
        "spark.executor.cores": "2"
    }
)
```

#### Test 4: Monitor and Cancel
```python
# Start long-running job
job = run_notebook_job(workspace="test-workspace", notebook="long_job")

# Check status
status = get_run_status(workspace="test-workspace", notebook="long_job", job_id=job["id"])

# Cancel if needed
cancel_notebook_job(workspace="test-workspace", notebook="long_job", job_id=job["id"])
```

---

### 2. Delta Lake Operations

**Status:** ✅ Code exists, ❓ Not tested

**Available Tools:**
- `table_preview(workspace, lakehouse, table, limit)` - Preview table data
- `describe_history(workspace, lakehouse, table, limit)` - Get Delta history
- `optimize_delta(workspace, lakehouse, table, zorder_by)` - Optimize with Z-ordering
- `vacuum_delta(workspace, lakehouse, table, retain_hours)` - Clean old versions

**Test Scenarios:**

#### Test 1: Table Preview
```python
# Preview first 50 rows of a table
table_preview(
    workspace="test-workspace",
    lakehouse="brons",
    table="publicholidays",
    limit=50
)
```

#### Test 2: Delta History
```python
# View version history
describe_history(
    workspace="test-workspace",
    lakehouse="brons",
    table="publicholidays",
    limit=20
)
```

#### Test 3: Optimize Delta Table
```python
# Optimize with Z-ordering on frequently filtered columns
optimize_delta(
    workspace="test-workspace",
    lakehouse="brons",
    table="publicholidays",
    zorder_by=["countryOrRegion", "date"]
)
```

#### Test 4: Vacuum Old Files
```python
# Clean up files older than 7 days (168 hours)
vacuum_delta(
    workspace="test-workspace",
    lakehouse="brons",
    table="publicholidays",
    retain_hours=168
)
```

---

### 3. SQL Operations

**Status:** ⚠️ Partially tested (needs SQL endpoint provisioning)

**Available Tools:**
- `sql_query(query, workspace, lakehouse, warehouse, type, max_rows)` - Execute SQL
- `sql_explain(query, workspace, lakehouse, warehouse, type)` - Get execution plan
- `sql_export(query, target_path, workspace, lakehouse, export_lakehouse, warehouse, file_format, overwrite)` - Export results

**Test Scenarios:**

#### Test 1: Query Lakehouse (after SQL endpoint is ready)
```python
# Query existing table
sql_query(
    query="SELECT countryOrRegion, COUNT(*) as holiday_count FROM publicholidays GROUP BY countryOrRegion ORDER BY holiday_count DESC",
    workspace="test-workspace",
    lakehouse="brons",
    max_rows=100
)
```

#### Test 2: Query Execution Plan
```python
# Analyze query performance
sql_explain(
    query="SELECT * FROM publicholidays WHERE date >= '2025-01-01'",
    workspace="test-workspace",
    lakehouse="brons"
)
```

#### Test 3: Export Query Results
```python
# Export to Parquet
sql_export(
    query="SELECT * FROM publicholidays WHERE countryOrRegion = 'Norway'",
    target_path="Files/exports/norway_holidays.parquet",
    workspace="test-workspace",
    lakehouse="brons",
    export_lakehouse="brons",
    file_format="parquet",
    overwrite=True
)
```

---

### 4. Power BI & Semantic Models

**Status:** ✅ Listing tested, ❓ Advanced operations not tested

**Available Tools:**
- `semantic_model_refresh(workspace, model_id)` - Refresh semantic models
- `dax_query(workspace, model_id, query)` - Execute DAX queries
- `report_export(workspace, report_id, format)` - Export reports
- `report_params_list(workspace, report_id)` - List report parameters

**Test Scenarios:**

#### Test 1: Refresh Semantic Model
```python
# Trigger model refresh
semantic_model_refresh(
    workspace="test-workspace",
    model_id="<semantic_model_id>"
)
```

#### Test 2: Execute DAX Query
```python
# Query semantic model with DAX
dax_query(
    workspace="test-workspace",
    model_id="<semantic_model_id>",
    query="""
    EVALUATE
    SUMMARIZECOLUMNS(
        'Date'[Year],
        'Sales'[Country],
        "TotalSales", SUM('Sales'[Amount])
    )
    ORDER BY [Year], [Country]
    """
)
```

#### Test 3: Export Report
```python
# Export report to PDF
report_export(
    workspace="test-workspace",
    report_id="<report_id>",
    format="PDF"
)
```

#### Test 4: List Report Parameters
```python
# Get available parameters
report_params_list(
    workspace="test-workspace",
    report_id="<report_id>"
)
```

---

### 5. Pipeline Operations

**Status:** ❓ Not tested

**Available Tools:**
- `pipeline_run(workspace, pipeline, parameters)` - Run data pipelines
- `pipeline_status(workspace, pipeline, run_id)` - Check pipeline status
- `pipeline_logs(workspace, pipeline, run_id)` - Get pipeline logs
- `dataflow_refresh(workspace, dataflow_id)` - Refresh dataflows
- `schedule_list(workspace, item_id, item_type)` - List schedules
- `schedule_set(workspace, item_id, item_type, schedule)` - Set/update schedules

**Test Scenarios:**

#### Test 1: Run Pipeline
```python
# Execute data pipeline
pipeline_run(
    workspace="test-workspace",
    pipeline="data_ingestion_pipeline",
    parameters={
        "source_date": "2025-11-03",
        "batch_size": 1000
    }
)
```

#### Test 2: Monitor Pipeline
```python
# Check pipeline execution status
pipeline_status(
    workspace="test-workspace",
    pipeline="data_ingestion_pipeline",
    run_id="<run_id_from_run>"
)
```

#### Test 3: View Pipeline Logs
```python
# Get detailed execution logs
pipeline_logs(
    workspace="test-workspace",
    pipeline="data_ingestion_pipeline",
    run_id="<run_id>"
)
```

#### Test 4: Schedule Pipeline
```python
# Set up daily schedule
schedule_set(
    workspace="test-workspace",
    item_id="<pipeline_id>",
    item_type="pipeline",
    schedule={
        "frequency": "daily",
        "time": "02:00",
        "timezone": "UTC"
    }
)
```

---

### 6. Permissions & Security

**Status:** ❓ Not tested

**Available Tools:**
- `resolve_item(workspace, name_or_id, type)` - Resolve item ID
- `list_items(workspace, type, search, top, skip)` - List with filtering
- `get_permissions(workspace, item_id)` - Get item permissions
- `set_permissions(workspace, item_id, assignments, scope)` - Set permissions

**Test Scenarios:**

#### Test 1: Resolve Item ID
```python
# Get canonical ID for item
resolve_item(
    workspace="test-workspace",
    name_or_id="test_lakehouse_mcp",
    type="lakehouse"
)
```

#### Test 2: List Items with Filter
```python
# Search for notebooks containing "test"
list_items(
    workspace="test-workspace",
    type="notebook",
    search="test",
    top=50
)
```

#### Test 3: Get Current Permissions
```python
# View who has access
get_permissions(
    workspace="test-workspace",
    item_id="<lakehouse_id>"
)
```

#### Test 4: Grant Permissions
```python
# Give user read access
set_permissions(
    workspace="test-workspace",
    item_id="<lakehouse_id>",
    assignments=[
        {
            "principal": {"id": "<user_id>", "type": "User"},
            "role": "Reader"
        }
    ]
)
```

---

## 🔍 Priority 3: Advanced Feature Testing

### 1. Spark Environment Management

**Available Tools:**
- `install_requirements(workspace, requirements_txt)` - Install Python packages
- `install_wheel(workspace, wheel_url)` - Install wheel packages
- `cluster_info(workspace)` - Get Spark cluster info

**Test Scenarios:**

#### Test 1: Install Python Packages
```python
# Install custom requirements
install_requirements(
    workspace="test-workspace",
    requirements_txt="""
pandas==2.0.0
numpy==1.24.0
scikit-learn==1.3.0
"""
)
```

#### Test 2: Install Custom Wheel
```python
# Install proprietary package
install_wheel(
    workspace="test-workspace",
    wheel_url="https://storage.example.com/packages/custom-lib-1.0.0-py3-none-any.whl"
)
```

#### Test 3: Check Cluster Configuration
```python
# Get Spark cluster details
cluster_info(workspace="test-workspace")
```

---

### 2. Code Generation & Validation

**Available Tools:**
- `generate_pyspark_code(operation, source_table, target_table, columns, filter_condition)`
- `validate_pyspark_code(code)`
- `generate_fabric_code(operation, lakehouse_name, table_name, target_table)`
- `validate_fabric_code(code)`
- `analyze_notebook_performance(workspace, notebook_id)`

**Test Scenarios:**

#### Test 1: Generate PySpark Code
```python
# Generate ETL code
generate_pyspark_code(
    operation="transform",
    source_table="brons.raw_data",
    target_table="silver.clean_data",
    columns="id, name, date, amount",
    filter_condition="date >= '2025-01-01'"
)
```

#### Test 2: Validate Code
```python
# Check code quality
validate_pyspark_code(
    code="""
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()
df = spark.read.table("brons.raw_data")
df_filtered = df.filter("date >= '2025-01-01'")
df_filtered.write.mode("overwrite").saveAsTable("silver.clean_data")
"""
)
```

#### Test 3: Generate Fabric-Specific Code
```python
# Generate Delta merge code
generate_fabric_code(
    operation="merge_delta",
    lakehouse_name="brons",
    table_name="source_data",
    target_table="target_data"
)
```

#### Test 4: Analyze Notebook Performance
```python
# Get optimization recommendations
analyze_notebook_performance(
    workspace="test-workspace",
    notebook_id="<notebook_id>"
)
```

---

### 3. Microsoft Graph Integration

**Available Tools:**
- `graph_user(email)` - Get user information
- `graph_mail(...)` - Access mail
- `graph_teams_message(team_id, channel_id, message)` - Send Teams messages
- `graph_drive(...)` - Access OneDrive/SharePoint
- `save_teams_channel_alias(alias, team_id, channel_id)` - Save aliases
- `list_teams_channel_aliases()` - List saved aliases
- `delete_teams_channel_alias(alias)` - Delete aliases

**Test Scenarios:**

#### Test 1: Get User Info
```python
# Lookup user details
graph_user(email="user@example.com")
```

#### Test 2: Send Teams Notification
```python
# Post to Teams channel
graph_teams_message(
    team_id="<team_id>",
    channel_id="<channel_id>",
    message="Data pipeline completed successfully! 🎉"
)
```

#### Test 3: Save Channel Alias
```python
# Create shortcut for frequently used channel
save_teams_channel_alias(
    alias="data-team",
    team_id="<team_id>",
    channel_id="<channel_id>"
)
```

#### Test 4: Use Alias
```python
# Send message using alias
graph_teams_message_alias(
    alias="data-team",
    message="New data available in lakehouse"
)
```

---

### 4. Data Loading

**Available Tools:**
- `load_data_from_url(url, destination_table, workspace, lakehouse, warehouse)`
- `onelake_ls(workspace, lakehouse, path)` - List OneLake files

**Test Scenarios:**

#### Test 1: Load CSV from URL
```python
# Load public dataset
load_data_from_url(
    url="https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv",
    destination_table="covid_data",
    workspace="test-workspace",
    lakehouse="brons"
)
```

#### Test 2: Load Parquet from URL
```python
# Load Parquet file
load_data_from_url(
    url="https://storage.example.com/data/sales_2025.parquet",
    destination_table="sales",
    workspace="test-workspace",
    warehouse="test_warehouse"
)
```

#### Test 3: List OneLake Files
```python
# Browse lakehouse files
onelake_ls(
    workspace="test-workspace",
    lakehouse="brons",
    path="Files/raw_data"
)
```

---

## 📋 Testing Matrix

| Category | Tool Count | Tested | Working | Partial | Broken | Untested |
|----------|-----------|--------|---------|---------|--------|----------|
| **Workspace** | 3 | 3 | 3 | 0 | 0 | 0 |
| **Lakehouse** | 3 | 3 | 3 | 0 | 0 | 0 |
| **Tables** | 12 | 3 | 3 | 0 | 0 | 9 |
| **OneLake** | 4 | 3 | 3 | 0 | 0 | 1 |
| **Notebooks** | 14 | 4 | 3 | 1 | 1 | 9 |
| **Warehouse** | 3 | 2 | 1 | 1 | 0 | 1 |
| **SQL** | 4 | 1 | 0 | 1 | 0 | 3 |
| **Power BI** | 7 | 2 | 2 | 0 | 0 | 5 |
| **Pipelines** | 6 | 0 | 0 | 0 | 0 | 6 |
| **Permissions** | 4 | 0 | 0 | 0 | 0 | 4 |
| **Graph API** | 7 | 0 | 0 | 0 | 0 | 7 |
| **Data Loading** | 1 | 0 | 0 | 0 | 0 | 1 |
| **Spark Env** | 3 | 0 | 0 | 0 | 0 | 3 |
| **Code Gen** | 5 | 0 | 0 | 0 | 0 | 5 |
| **TOTAL** | **76** | **21** | **18** | **3** | **1** | **55** |

**Coverage:** 27.6% tested, 72.4% untested

---

## 🎯 Recommended Testing Sequence

### Week 1: Fix Critical Issues
1. **Day 1-2:** Fix LRO response handling bug (warehouse & notebook creation)
2. **Day 3-4:** Debug and fix `update_notebook_cell` JSON parsing
3. **Day 5:** Regression testing on all working tools

### Week 2: Test Core Untested Features
1. **Day 1-2:** Notebook execution (run, status, cancel) - HIGH PRIORITY
2. **Day 3:** Delta Lake operations (preview, history, optimize, vacuum)
3. **Day 4:** SQL operations (query, explain, export)
4. **Day 5:** Power BI operations (DAX, refresh, export)

### Week 3: Test Advanced Features
1. **Day 1:** Pipeline operations
2. **Day 2:** Permissions & security
3. **Day 3:** Spark environment management
4. **Day 4:** Code generation & validation
5. **Day 5:** Graph API integration

### Week 4: Integration & Documentation
1. **Day 1-2:** End-to-end workflow testing
2. **Day 3:** Performance testing
3. **Day 4:** Update documentation
4. **Day 5:** Create examples and tutorials

---

## 🐛 Known Issues Summary

### Critical (Fix Immediately)
1. **LRO Response Bug:** Warehouse and notebook creation return error messages despite success
2. **Notebook Cell Update:** JSON parsing error prevents cell updates

### Medium (Fix Soon)
1. **SQL Endpoint:** Requires manual provisioning before queries work
2. **Notebook Content:** Empty responses for notebooks created in UI

### Low (Monitor)
1. **Folder Management:** No API support (Fabric platform limitation)
2. **Generic create_notebook:** Attribute error (use specific templates instead)

---

## 📝 Test Documentation Template

For each test, document:
```markdown
### Test: [Tool Name] - [Scenario]
**Date:** YYYY-MM-DD
**Tester:** Name
**Tool:** tool_name
**Parameters:**
- param1: value1
- param2: value2

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happened]

**Status:** ✅ Pass / ⚠️ Partial / ❌ Fail

**Notes:**
- Additional observations
- Edge cases discovered
- Performance metrics

**Screenshots/Logs:**
[Attach relevant evidence]
```

---

## 🔄 Continuous Testing Checklist

After each fix or feature implementation:
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Documentation updated
- [ ] Notion page updated with results
- [ ] Examples created/updated
- [ ] Regression tests run on related features
- [ ] Performance benchmarks recorded

---

## 📚 Resources

### Fabric API Documentation
- [Core API](https://learn.microsoft.com/en-us/rest/api/fabric/)
- [Lakehouse API](https://learn.microsoft.com/en-us/rest/api/fabric/lakehouse/)
- [Notebook API](https://learn.microsoft.com/en-us/rest/api/fabric/notebook/)
- [Warehouse API](https://learn.microsoft.com/en-us/rest/api/fabric/warehouse/)

### Testing Tools
- MCP Inspector for manual testing
- Python pytest for automated tests
- Fabric workspace for live testing
- Claude Desktop for AI-assisted testing

---

## 🎉 Success Metrics

### Phase 1 (Critical Fixes)
- [ ] All creation operations return success messages
- [ ] Notebook cell updates work without errors
- [ ] Zero false error reports to users

### Phase 2 (Core Features)
- [ ] Notebook execution fully tested and documented
- [ ] Delta Lake operations verified
- [ ] SQL operations working (after endpoint provisioning)
- [ ] Power BI integration tested

### Phase 3 (Advanced Features)
- [ ] Pipeline orchestration tested
- [ ] Permission management verified
- [ ] Graph API integration working
- [ ] Code generation producing valid output

### Final Goal
- [ ] 90%+ test coverage
- [ ] Zero critical bugs
- [ ] Complete documentation
- [ ] Example workflows for all major features
- [ ] Performance benchmarks established

---

**Next Steps:**
1. Review this plan with team
2. Prioritize fixes and tests
3. Begin Week 1 tasks
4. Update Notion page with progress
5. Create tracking board for test execution

