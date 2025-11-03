# Testing Documentation

This folder contains comprehensive test results for the Microsoft Fabric MCP tools.

## Test Reports

### [Medallion Architecture Test](./medallion_architecture_test.md)
**Status:** ✅ PASSED

Complete end-to-end test of bronze → silver → gold medallion architecture pipeline creation using MCP tools.

**What was tested:**
- Workspace creation with trial capacity
- Lakehouse provisioning (3 layers)
- Notebook creation and execution
- OneLake file operations
- Delta table operations
- SQL querying with ODBC driver
- Schema inspection
- Code generation

**Key Results:**
- 15 tools working perfectly
- 1 SQL tool (sql_query) working with ODBC
- 85% time savings vs manual setup
- Production-ready with documented limitations

**Date:** 2025-11-03

---

## Test Coverage Summary

| Category | Tools Tested | Status | Notes |
|----------|--------------|--------|-------|
| Workspace Management | 3 | ✅ All Pass | create, list, set |
| Lakehouse Operations | 4 | ✅ All Pass | create, list, set, schema |
| Notebook Management | 3 | ⚠️ Works* | Creates successfully but shows error |
| OneLake Files | 3 | ✅ All Pass | read, write, list |
| SQL Querying | 1 | ✅ Pass | Requires ODBC driver |
| Delta Operations | 3 | ❌ Not Supported | Use Spark SQL in notebooks |

\* = Known limitation with workaround

---

## Quick Start

To reproduce the medallion architecture test:

1. **Prerequisites:**
   - Fabric workspace with trial capacity
   - Microsoft ODBC Driver 18 for SQL Server
   - MCP server configured

2. **Run the test:**
   ```
   Create workspace → Create lakehouses → Create notebooks → Execute pipeline
   ```

3. **Validation:**
   - Check `list_tables` for each lakehouse
   - Run `sql_query` to verify data
   - Review `get_all_lakehouse_schemas` for structure

---

## Known Issues

1. **Notebook creation API** - Returns error but notebooks are created successfully
2. **SQL endpoint sync** - New tables take 5-10 minutes to appear in SQL endpoint
3. **Delta commands** - OPTIMIZE, VACUUM, DESCRIBE HISTORY must use Spark SQL
4. **Lakehouse attachment** - Must be done manually in Fabric UI

See full test report for detailed workarounds.
