# 🔍 Untested MCP Tools - Priority Analysis

## 📊 **HIGH PRIORITY** (Business-Critical Features)

### 1. Power BI / Analytics (4 tools) 🎯
**Impact:** Direct business intelligence and reporting
- `dax_query` - Execute DAX queries on semantic models
- `semantic_model_refresh` - Trigger semantic model refresh
- `report_export` - Export Power BI reports (PDF, PPTX, etc.)
- `report_params_list` - List parameters for reports

**Why Important:** Power BI is core to analytics - these enable automated reporting and data refresh

---

### 2. Data Pipelines & Orchestration (6 tools) 🔄
**Impact:** Automation and data workflows
- `pipeline_run` - Execute data pipelines
- `pipeline_status` - Check pipeline execution status
- `pipeline_logs` - Retrieve pipeline execution logs
- `dataflow_refresh` - Trigger dataflow refreshes
- `schedule_list` - List scheduled jobs
- `schedule_set` - Create/update schedules

**Why Important:** Critical for ETL automation and production workflows

---

### 3. SQL Operations (4 tools) 📊
**Impact:** Data querying and analysis
- `sql_query` - Execute SQL queries against lakehouse/warehouse
- `sql_explain` - Get query execution plans (performance tuning)
- `sql_export` - Export query results to OneLake (CSV, Parquet)
- `get_sql_endpoint` - Get SQL connection endpoint info

**Why Important:** Core data access - **Note:** Notion page says SQL requires endpoint activation

---

## 📦 **MEDIUM PRIORITY** (Operational Features)

### 4. Delta Table Operations (5 tools) 🗄️
**Impact:** Data maintenance and optimization
- `table_preview` - Preview table data (with row limit)
- `describe_history` - View Delta table history/versions
- `optimize_delta` - Optimize and compact Delta tables (ZORDER)
- `vacuum_delta` - Clean up old Delta versions

**Why Important:** Performance optimization and data management

---

### 5. Items & Permissions (4 tools) 🔐
**Impact:** Access control and item management
- `resolve_item` - Resolve item names to IDs (helper utility)
- `list_items` - List all items in workspace (filter by type)
- `get_permissions` - Get permissions for workspace items
- `set_permissions` - Set/update permissions for items

**Why Important:** Security and access management

---

### 6. Microsoft Graph Integration (7 tools) 📧
**Impact:** Teams and email integration
- `graph_user` - Get user information
- `graph_mail` - Send emails via Graph API
- `graph_teams_message` - Send Teams messages
- `graph_drive` - Access OneDrive files
- `save_teams_channel_alias` - Create Teams channel alias
- `list_teams_channel_aliases` - List saved aliases
- `delete_teams_channel_alias` - Delete alias

**Why Important:** Integration with M365 ecosystem for notifications

---

## 🛠️ **LOW PRIORITY** (Developer Tools)

### 7. Spark Environment Management (3 tools) ⚙️
**Impact:** Spark cluster configuration
- `install_requirements` - Install Python requirements.txt
- `install_wheel` - Install Python wheel packages
- `cluster_info` - Get Spark cluster information

**Why Important:** Development environment setup

---

### 8. Code Generation & Validation (5 tools) 🤖
**Impact:** Developer productivity
- `generate_pyspark_code` - Generate PySpark code templates
- `validate_pyspark_code` - Validate PySpark code syntax
- `generate_fabric_code` - Generate Fabric-specific code
- `validate_fabric_code` - Validate Fabric code
- `analyze_notebook_performance` - Performance analysis

**Why Important:** Nice-to-have development aids

---

### 9. Data Loading (1 tool) 📥
**Impact:** Data ingestion
- `load_data_from_url` - Load data from URLs (CSV, Parquet)

**Why Important:** Alternative data loading method (mentioned in Notion as available)

---

## 📋 **Testing Recommendations by Category**

### 🔥 **Test First** (Maximum Business Value)
1. **Power BI Tools** - `dax_query`, `semantic_model_refresh`
2. **Pipeline Tools** - `pipeline_run`, `pipeline_status` 
3. **SQL Tools** - `sql_query`, `sql_export` (if endpoint available)

### ⚡ **Test Next** (Operational Value)
4. **Delta Operations** - `table_preview`, `optimize_delta`
5. **Permissions** - `get_permissions`, `list_items`

### 🔍 **Test Later** (Developer Tools)
6. **Graph API** - `graph_teams_message`, `graph_mail`
7. **Spark Tools** - `cluster_info`, `install_requirements`
8. **Code Gen** - `generate_pyspark_code`, `validate_pyspark_code`

---

## ✅ **Already Tested (from Notion page)**
- Workspace: create, list, set ✅
- Lakehouse: create, list, set ✅
- Warehouse: create (partial), list ✅
- Notebook: create, list, get_content, update_cell, run_job (capacity issue) ✅
- Tables: list, get_schema, get_all_schemas ✅
- OneLake: read, write, rm, ls ✅
- Reports: list, get ✅
- Semantic Models: list, get ✅

---

## 🎯 **Total Untested Tools: 39**
- **High Priority:** 14 tools
- **Medium Priority:** 16 tools  
- **Low Priority:** 9 tools







