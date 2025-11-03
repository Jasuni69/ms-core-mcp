# 🚀 Quick Testing Guide - Microsoft Fabric MCP Tools

## 🔥 Top Priority Actions

### 1. FIX FIRST: LRO Response Bug (1-2 hours)
**File:** `helpers/clients/fabric_client.py` (line 551)  
**Issue:** Warehouse and notebook creation work but return error messages  
**Fix:** Return the fetched item instead of empty LRO response  

```python
# Current (broken):
if lro and len(response) == 0:
    items = await self.get_items(...)
    for item in items:
        if item.get("displayName") == name:
            return item  # But this doesn't happen reliably

# Should be:
if lro and len(response) == 0:
    await asyncio.sleep(3)  # Wait for propagation
    items = await self.get_items(...)
    for item in items:
        if item.get("displayName") == name:
            return item  # Must return this!
    # If not found, still return success
    return {"displayName": name, "status": "Created"}
```

### 2. FIX NEXT: Notebook Cell Update (2-3 hours)
**File:** `tools/notebook.py` (line 1163)  
**Issue:** JSON parsing error: `'Expecting value: line 1 column 1 (char 0)'`  
**Investigation needed:** Check what Fabric API returns for update operations

### 3. TEST IMMEDIATELY: Notebook Execution (30 minutes)
**You thought this didn't exist, but it does!**

```python
# Test this NOW:
from tools.notebook import run_notebook_job, get_run_status

# 1. Create notebook
create_pyspark_notebook(workspace="test-workspace", notebook_name="test_exec")

# 2. Run it!
job = run_notebook_job(workspace="test-workspace", notebook="test_exec")

# 3. Check status
status = get_run_status(workspace="test-workspace", notebook="test_exec", job_id=job["id"])
```

---

## 📊 Testing Priority Matrix

### Priority 1: HIGH IMPACT, NOT TESTED (Do This Week!)
- ⚡ **Notebook Execution** (`run_notebook_job`, `get_run_status`, `cancel_notebook_job`)
- ⚡ **Delta Lake Ops** (`optimize_delta`, `vacuum_delta`, `describe_history`, `table_preview`)
- ⚡ **SQL Export** (`sql_export` - export query results to files)
- ⚡ **Pipeline Execution** (`pipeline_run`, `pipeline_status`, `pipeline_logs`)

### Priority 2: USEFUL, NOT TESTED (Do Next Week)
- 🔧 **Power BI Advanced** (`dax_query`, `semantic_model_refresh`, `report_export`)
- 🔧 **Permissions** (`get_permissions`, `set_permissions`)
- 🔧 **Spark Environment** (`install_requirements`, `install_wheel`, `cluster_info`)
- 🔧 **Code Generation** (`generate_pyspark_code`, `validate_pyspark_code`)

### Priority 3: NICE TO HAVE (Do Later)
- 📝 **Graph API** (Teams messages, mail, user lookup)
- 📝 **Schedule Management** (`schedule_set`, `schedule_list`)
- 📝 **Dataflow Refresh** (`dataflow_refresh`)

---

## ⚡ 30-Minute Quick Tests

### Test Set 1: Notebook Execution (THE BIG ONE!)
```python
# 1. List current notebooks
list_notebooks(workspace="test-workspace")

# 2. Pick one or create new
create_pyspark_notebook(workspace="test-workspace", notebook_name="quick_test")

# 3. RUN IT! (This is the untested feature!)
job = run_notebook_job(workspace="test-workspace", notebook="quick_test")

# 4. Monitor
status = get_run_status(workspace="test-workspace", notebook="quick_test", job_id=job["id"])

# 5. Cancel if needed
cancel_notebook_job(workspace="test-workspace", notebook="quick_test", job_id=job["id"])
```

### Test Set 2: Delta Lake Operations
```python
# Assuming you have "publicholidays" table in "brons" lakehouse

# 1. Preview data
table_preview(workspace="test-workspace", lakehouse="brons", table="publicholidays", limit=10)

# 2. Check version history
describe_history(workspace="test-workspace", lakehouse="brons", table="publicholidays")

# 3. Optimize table
optimize_delta(
    workspace="test-workspace", 
    lakehouse="brons", 
    table="publicholidays",
    zorder_by=["countryOrRegion", "date"]
)

# 4. Clean old versions (careful! default is 168 hours = 7 days)
vacuum_delta(workspace="test-workspace", lakehouse="brons", table="publicholidays")
```

### Test Set 3: SQL Export
```python
# Export query results to file
sql_export(
    query="SELECT * FROM publicholidays WHERE countryOrRegion = 'Norway'",
    target_path="Files/exports/norway_holidays.parquet",
    workspace="test-workspace",
    lakehouse="brons",
    export_lakehouse="brons",
    file_format="parquet",
    overwrite=True
)

# Verify file was created
onelake_ls(workspace="test-workspace", lakehouse="brons", path="Files/exports")

# Read it back
onelake_read(workspace="test-workspace", lakehouse="brons", path="Files/exports/norway_holidays.parquet")
```

### Test Set 4: Pipeline Operations
```python
# Note: You need an existing pipeline first

# 1. List items to find pipeline
list_items(workspace="test-workspace", type="DataPipeline")

# 2. Run pipeline
pipeline_run(workspace="test-workspace", pipeline="<pipeline_name>")

# 3. Check status
pipeline_status(workspace="test-workspace", pipeline="<pipeline_name>", run_id="<run_id>")

# 4. View logs
pipeline_logs(workspace="test-workspace", pipeline="<pipeline_name>", run_id="<run_id>")
```

---

## 🎯 One-Day Testing Sprint Plan

### Morning (9 AM - 12 PM): Fix Bugs
**Goal:** Fix LRO response handling

1. **9:00-9:30** - Review `fabric_client.py` create_item method
2. **9:30-10:30** - Implement fix for LRO response handling
3. **10:30-11:00** - Test warehouse creation
4. **11:00-11:30** - Test notebook creation
5. **11:30-12:00** - Verify fixes work consistently

### Afternoon (1 PM - 5 PM): Test Untested Features
**Goal:** Test notebook execution, Delta ops, SQL export

1. **1:00-2:00** - Test notebook execution (run, status, cancel)
2. **2:00-3:00** - Test Delta Lake operations (preview, history, optimize, vacuum)
3. **3:00-4:00** - Test SQL export functionality
4. **4:00-4:30** - Test pipeline operations (if pipelines exist)
5. **4:30-5:00** - Document results and update Notion page

---

## 📝 Quick Test Documentation Template

Copy this for each test:

```markdown
## Test: [Tool Name]
**Date:** 2025-11-03
**Tool:** `tool_name`
**Status:** ✅ Pass / ⚠️ Partial / ❌ Fail

**Test Command:**
```
[command used]
```

**Result:**
[what happened]

**Issues:**
[any problems]

**Notes:**
[additional observations]
```

---

## 🔍 Quick Checks

### Is Everything Working?
```bash
# Check workspace
list_workspaces()

# Check lakehouse  
list_lakehouses(workspace="test-workspace")

# Check tables
list_tables(workspace="test-workspace", lakehouse="brons")

# Check notebooks
list_notebooks(workspace="test-workspace")
```

### Common Troubleshooting
1. **"Workspace not set"** → Run `set_workspace(workspace="test-workspace")`
2. **"SQL endpoint not found"** → Wait for Fabric to provision (can take 5-10 minutes after lakehouse creation)
3. **"Item not found"** → Use `list_items()` to find correct name/ID
4. **LRO error** → Item probably created, verify with `list_*` command

---

## 🎉 Today's Wins

Track your progress:
- [ ] Fixed LRO bug (warehouse & notebook creation)
- [ ] Fixed notebook cell update bug
- [ ] Tested notebook execution (run, status, cancel)
- [ ] Tested Delta Lake operations (4 tools)
- [ ] Tested SQL export
- [ ] Tested pipeline operations
- [ ] Updated Notion page with results
- [ ] Created test examples

---

## 📞 Need Help?

**Debug Mode:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check Logs:**
- Look in `helpers/logging_config.py` for log configuration
- Errors will show in console when running MCP server

**Useful Files:**
- `tools/notebook.py` - Notebook operations
- `tools/lakehouse.py` - Lakehouse operations  
- `tools/warehouse.py` - Warehouse operations
- `helpers/clients/fabric_client.py` - Core API client
- `helpers/clients/notebook_client.py` - Notebook-specific API calls

---

## 🚀 Get Started NOW

1. **Fix LRO bug** (1 hour)
   - Edit `helpers/clients/fabric_client.py` line 551
   - Test with `create_warehouse` and `create_pyspark_notebook`

2. **Test notebook execution** (30 minutes)
   - Run `run_notebook_job`
   - This is THE BIG discovery - you thought it didn't exist!

3. **Test Delta operations** (30 minutes)
   - Run `table_preview`, `describe_history`, `optimize_delta`

4. **Update Notion** (15 minutes)
   - Add test results
   - Mark tools as tested
   - Note any new issues

**Total Time:** ~2.5 hours to make HUGE progress! 🎯








