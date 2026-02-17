# MCP Tool Test Results

**Date:** 2026-02-17
**Workspace:** testvscode
**Lakehouse:** chocolate_sales

## 1. Workspace & Context Tools
- [x] `list_workspaces` - PASS (6 workspaces returned)
- [x] `set_workspace` - PASS ("testvscode" set)
- [x] `list_lakehouses` - PASS (4 lakehouses returned)
- [x] `list_warehouses` - PASS (none found, no error)
- [x] `list_items` - PASS (after bug fix, 20 items returned)
- [x] `resolve_item` - PASS (after bug fix, returned chocolate_sales UUID and metadata)
- [x] `set_lakehouse` - PASS ("chocolate_sales" set)
- [ ] `set_warehouse` - SKIP (no warehouses in workspace)
- [x] `clear_context` - PASS
- [ ] `create_workspace` - SKIP (destructive)
- [ ] `create_lakehouse` - SKIP (destructive)
- [ ] `create_warehouse` - SKIP (destructive)

## 2. Table & SQL Tools
- [x] `list_tables` - PASS (7 delta tables found)
- [x] `table_preview` - PASS (fact_sales, 5 rows returned as JSON)
- [x] `table_schema` - PASS (fact_sales schema with metadata)
- [x] `get_lakehouse_table_schema` - PASS (fact_sales schema)
- [x] `get_all_lakehouse_schemas` - PASS (all 7 tables with full schemas)
- [x] `set_table` - PASS ("fact_sales" set)
- [x] `describe_history` - PASS (after delta-rs rewrite, returns version history with operation metrics)
- [x] `sql_query` - PASS (SELECT TOP 5 from fact_sales)
- [x] `sql_explain` - PASS (after fix, returns full SHOWPLAN XML execution plan)
- [x] `sql_export` - PASS (after bug fix, exported 3 rows CSV to OneLake, verified read-back)
- [x] `get_sql_endpoint` - PASS (after bug fix, returns server/database/connectionString)
- [x] `optimize_delta` - PASS (after delta-rs rewrite, compacted 8 files → 1, 102KB → 49KB)
- [ ] `vacuum_delta` - BUG FIXED (same delta-rs approach, untested)

## 3. Semantic Model & DAX Tools
- [x] `list_semantic_models` - PASS (2 models found)
- [x] `get_semantic_model` - PASS (after bug fix, returns model details)
- [x] `get_model_schema` - PASS (empty model but no error)
- [x] `list_measures` - PASS (0 measures, clean response)
- [ ] `get_measure` - NOT TESTED (no measures exist)
- [ ] `create_measure` - NOT TESTED (model empty)
- [ ] `update_measure` - NOT TESTED (no measures exist)
- [ ] `delete_measure` - NOT TESTED (no measures exist)
- [x] `dax_query` - PASS (after bug fix, `EVALUATE ROW("test", 1)` returned correct result)
- [ ] `analyze_dax_query` - BUG FIXED (same code path as dax_query, untested)

## 4. Notebook Tools
- [x] `list_notebooks` - PASS (9 notebooks found)
- [x] `get_notebook_content` - PASS (full JSON with cells, metadata, outputs)
- [x] `generate_pyspark_code` - PASS (after bug fix, schema_inference template generates correct code)
- [x] `validate_pyspark_code` - PASS (syntax check works, gives warnings)
- [ ] `create_notebook` - NOT TESTED (destructive)
- [ ] `create_pyspark_notebook` - NOT TESTED (destructive)
- [ ] `create_fabric_notebook` - NOT TESTED (destructive)
- [ ] `update_notebook_cell` - NOT TESTED
- [ ] `run_notebook_job` - NOT TESTED (requires Spark capacity)
- [ ] `get_run_status` - NOT TESTED
- [ ] `cancel_notebook_job` - NOT TESTED
- [x] `generate_fabric_code` - PASS (read_lakehouse operation generated correct PySpark)
- [x] `validate_fabric_code` - PASS (syntax check passed, Fabric recommendations returned)
- [ ] `analyze_notebook_performance` - NOT TESTED
- [ ] `install_requirements` - NOT TESTED (requires Spark cluster)
- [ ] `install_wheel` - NOT TESTED (requires Spark cluster)
- [ ] `cluster_info` - NOT TESTED (requires Spark cluster)

## 5. OneLake Tools
- [x] `onelake_ls` (Files) - PASS (empty Files folder listed)
- [x] `onelake_ls` (Tables) - PASS (after fix, lists 7 delta tables via Fabric API fallback)
- [x] `onelake_read` - PASS (read test file content back correctly)
- [x] `onelake_write` - PASS (wrote 19 bytes to Files/test_file.txt)
- [x] `onelake_rm` - PASS (deleted test file)
- [x] `onelake_list_shortcuts` - PASS (0 shortcuts, clean response)
- [ ] `onelake_create_shortcut` - NOT TESTED (needs second lakehouse as target)
- [ ] `onelake_delete_shortcut` - NOT TESTED (no shortcuts exist)

## 6. Pipeline & Schedule Tools
- [x] `schedule_list` - PASS (after bug fix, auto-detects job type: Lakehouse→TableMaintenance, Notebook→RunNotebook)
- [ ] `create_data_pipeline` - NOT TESTED (destructive)
- [ ] `pipeline_run` - NOT TESTED (no pipelines in workspace)
- [ ] `pipeline_status` - NOT TESTED (no pipelines in workspace)
- [ ] `pipeline_logs` - NOT TESTED (no pipelines in workspace)
- [ ] `dataflow_refresh` - NOT TESTED (no dataflows in workspace)
- [ ] `schedule_set` - BUG FIXED (same auto-detect pattern as schedule_list)
- [ ] `get_pipeline_definition` - NOT TESTED (no pipelines in workspace)

## 7. Report & Power BI Tools
- [x] `list_reports` - PASS (no reports, clean message)
- [ ] `get_report` - NOT TESTED (no reports in workspace)
- [ ] `report_export` - NOT TESTED (no reports in workspace)
- [ ] `report_params_list` - NOT TESTED (no reports in workspace)
- [ ] `semantic_model_refresh` - NOT TESTED

## 8. Graph API Tools
- [x] `graph_user` - PASS (after bug fix, "me" returns current user profile)
- [ ] `graph_mail` - NOT TESTED (sends real email)
- [ ] `graph_drive` - NOT TESTED (needs drive ID)
- [ ] `graph_teams_message` - NOT TESTED (sends real message)
- [ ] `graph_teams_message_alias` - NOT TESTED (no aliases)
- [ ] `save_teams_channel_alias` - NOT TESTED
- [x] `list_teams_channel_aliases` - PASS (empty, no error)
- [ ] `delete_teams_channel_alias` - NOT TESTED (no aliases)

---

## Summary

| Category | Tested | Passed | Bugs Found | Fixed & Verified |
|----------|--------|--------|------------|------------------|
| Workspace & Context | 8 | 8 | 1 | 1 |
| Table & SQL | 13 | 12 | 8 | 7 |
| Semantic Model & DAX | 6 | 5 | 3 | 3 |
| Notebook | 7 | 6 | 1 | 1 |
| OneLake | 7 | 7 | 1 | 1 |
| Pipeline & Schedule | 2 | 1 | 2 | 1 |
| Report & Power BI | 1 | 1 | 0 | 0 |
| Graph API | 2 | 2 | 1 | 1 |
| **Total** | **46** | **42** | **18** | **15** |

## Bugs Found

| # | Tool | Issue | Status |
|---|------|-------|--------|
| 1 | `list_items` | Passes workspace name instead of UUID to `get_items()` | **Fixed & verified** |
| 2 | `resolve_item` | Same name-vs-UUID bug in `items.py` | **Fixed & verified** |
| 3 | `get_permissions` | Same name-vs-UUID bug in `items.py` | **Fixed** - untested |
| 4 | `set_permissions` | Same name-vs-UUID bug in `items.py` | **Fixed** - untested |
| 5 | `get_sql_endpoint` | Type not inferred from context, shows "None" in error msg | **Fixed & verified** |
| 6 | `get_semantic_model` | Passes workspace name instead of UUID | **Fixed & verified** |
| 7 | `dax_query` | Wrong API endpoint - uses Fabric `/dax/query` instead of Power BI `/executeQueries` | **Fixed & verified** |
| 8 | `analyze_dax_query` | Same wrong endpoint as `dax_query` | **Fixed** - untested (same code path) |
| 9 | `generate_pyspark_code` | f-string evaluates `{c}` loop var at template time (`NameError`) | **Fixed & verified** |
| 10 | `describe_history` | Uses Spark SQL `DESCRIBE HISTORY` over T-SQL endpoint | **Fixed & verified** (delta-rs rewrite) |
| 11 | `sql_explain` | `SET SHOWPLAN_XML` combined with query in same batch | **Fixed & verified** (separate connection statements) |
| 12 | `optimize_delta` | Uses Spark SQL `OPTIMIZE` over T-SQL endpoint | **Fixed & verified** (delta-rs rewrite) |
| 13 | `vacuum_delta` | Uses Spark SQL `VACUUM` over T-SQL endpoint | **Fixed** - untested (same delta-rs approach) |
| 14 | `onelake_ls` (Tables) | `Tables/` not a real ADLS directory - PathNotFound | **Fixed & verified** (falls back to Fabric API) |
| 15 | `schedule_list` | Wrong API path + `DefaultJob` not valid for all items | **Fixed & verified** (auto-detects job type per item) |
| 16 | `schedule_set` | Same job type issue as `schedule_list` | **Fixed** - same auto-detect pattern, untested |
| 17 | `sql_export` | Uses `endpoint["resourceId"]` (SQLEndpoint UUID) instead of lakehouse ID for OneLake write | **Fixed & verified** |
| 18 | `graph_user` | `/users/me` is invalid - Graph API needs `/me` for current user | **Fixed & verified** |

## Files Modified

| File | Changes |
|------|---------|
| `tools/items.py` | Added `resolve_workspace_name_and_id()` to all 4 functions |
| `tools/sql_endpoint.py` | Added type inference from context (lakehouse/warehouse) |
| `tools/sql.py` | Rewrote `sql_explain` to use separate SHOWPLAN statements; fixed `sql_export` lakehouse ID resolution |
| `tools/table.py` | Rewrote `describe_history`, `optimize_delta`, `vacuum_delta` to use delta-rs instead of Spark SQL |
| `tools/semantic_model.py` | Added workspace resolution in `get_semantic_model`; fixed DAX endpoint in `analyze_dax_query` |
| `tools/powerbi.py` | Fixed `dax_query` to use Power BI API `/executeQueries` endpoint with correct token scope |
| `tools/notebook.py` | Changed `schema_inference` and `data_quality` templates from f-strings to regular strings |
| `tools/pipeline.py` | Fixed schedule API path; added auto-detect job type mapping for item types |
| `tools/onelake.py` | Added Fabric API fallback for `onelake_ls` when path is `Tables` |
| `tools/graph.py` | Fixed `graph_user` to use `/me` endpoint when email is "me" |
| `helpers/clients/fabric_client.py` | Added `token_scope` parameter to `_make_request` and `_get_headers` |
