# Power BI Semantic Model Tools

This document describes the advanced Power BI semantic model tools that enable agentic interaction with Power BI models via MCP (Model Context Protocol).

## Overview

These tools allow you to explore semantic model schemas, manage DAX measures, and analyze query performance - enabling Claude to interact with Power BI models similar to capabilities shown in demonstrations of agent-driven Power BI workflows.

## Available Tools

### 1. Model Schema Exploration

#### `get_model_schema`

Retrieves the complete schema of a semantic model including tables, columns, measures, and relationships.

**Parameters:**
- `workspace` (optional): Name or ID of the workspace
- `model` (optional): Name or ID of the semantic model
- `ctx` (optional): Context object

**Returns:**
```json
{
  "modelName": "Sales Model",
  "modelId": "abc-123",
  "workspaceId": "def-456",
  "tables": [
    {
      "name": "Sales",
      "isHidden": false,
      "columns": [
        {
          "name": "OrderDate",
          "dataType": "DateTime",
          "isHidden": false,
          "sourceColumn": "OrderDate"
        }
      ],
      "measures": [
        {
          "name": "Total Sales",
          "expression": "SUM(Sales[Amount])",
          "formatString": "$#,0.00",
          "isHidden": false,
          "table": "Sales"
        }
      ]
    }
  ],
  "relationships": [
    {
      "name": "Sales-Date",
      "fromTable": "Sales",
      "fromColumn": "OrderDate",
      "toTable": "Date",
      "toColumn": "Date",
      "crossFilteringBehavior": "Both"
    }
  ],
  "measures": [...]
}
```

**Example:**
```python
schema = await get_model_schema(workspace="PowerBI_Test", model="Sales Model")
print(f"Model has {len(schema['tables'])} tables and {len(schema['measures'])} measures")
```

---

### 2. Measure Management

#### `list_measures`

Lists all DAX measures in a semantic model.

**Parameters:**
- `workspace` (optional): Name or ID of the workspace
- `model` (optional): Name or ID of the semantic model
- `ctx` (optional): Context object

**Returns:**
```json
{
  "modelName": "Sales Model",
  "measureCount": 15,
  "measures": [
    {
      "name": "Total Sales",
      "expression": "SUM(Sales[Amount])",
      "formatString": "$#,0.00",
      "isHidden": false,
      "table": "Sales"
    }
  ]
}
```

---

#### `get_measure`

Gets a specific DAX measure definition by name.

**Parameters:**
- `measure_name` (required): Name of the measure to retrieve
- `workspace` (optional): Name or ID of the workspace
- `model` (optional): Name or ID of the semantic model
- `ctx` (optional): Context object

**Returns:**
```json
{
  "found": true,
  "measure": {
    "name": "Total Sales",
    "expression": "SUM(Sales[Amount])",
    "formatString": "$#,0.00",
    "isHidden": false,
    "table": "Sales",
    "description": "Calculates total sales amount"
  }
}
```

---

#### `create_measure`

Creates a new DAX measure in a semantic model.

**Parameters:**
- `measure_name` (required): Name of the measure to create
- `dax_expression` (required): DAX formula for the measure
- `table_name` (required): Name of the table to add the measure to
- `workspace` (optional): Name or ID of the workspace
- `model` (optional): Name or ID of the semantic model
- `format_string` (optional): Display format string (e.g., "#,0.00", "0.0%")
- `description` (optional): Description of the measure
- `is_hidden` (optional): Whether to hide the measure from client tools (default: False)
- `ctx` (optional): Context object

**Returns:**
```json
{
  "success": true,
  "message": "Measure 'YTD Sales' created successfully",
  "measure": {
    "name": "YTD Sales",
    "expression": "TOTALYTD(SUM(Sales[Amount]), 'Date'[Date])",
    "formatString": "$#,0.00",
    "isHidden": false,
    "description": "Year-to-date sales"
  },
  "table": "Sales",
  "model": "Sales Model"
}
```

**Example:**
```python
result = await create_measure(
    measure_name="YTD Sales",
    dax_expression="TOTALYTD(SUM(Sales[Amount]), 'Date'[Date])",
    table_name="Sales",
    format_string="$#,0.00",
    description="Year-to-date sales"
)
```

---

#### `update_measure`

Updates an existing DAX measure in a semantic model.

**Parameters:**
- `measure_name` (required): Current name of the measure to update
- `workspace` (optional): Name or ID of the workspace
- `model` (optional): Name or ID of the semantic model
- `dax_expression` (optional): New DAX formula
- `format_string` (optional): New display format string
- `description` (optional): New description
- `is_hidden` (optional): New hidden status
- `new_name` (optional): New name for the measure
- `ctx` (optional): Context object

**Returns:**
```json
{
  "success": true,
  "message": "Measure 'Total Sales' updated successfully",
  "table": "Sales",
  "model": "Sales Model"
}
```

**Example:**
```python
result = await update_measure(
    measure_name="Total Sales",
    dax_expression="SUMX(Sales, Sales[Quantity] * Sales[Price])",
    description="Updated calculation including quantity"
)
```

---

#### `delete_measure`

Deletes a DAX measure from a semantic model.

**Parameters:**
- `measure_name` (required): Name of the measure to delete
- `workspace` (optional): Name or ID of the workspace
- `model` (optional): Name or ID of the semantic model
- `ctx` (optional): Context object

**Returns:**
```json
{
  "success": true,
  "message": "Measure 'Old Metric' deleted successfully",
  "table": "Sales",
  "model": "Sales Model"
}
```

**Example:**
```python
result = await delete_measure(measure_name="Old Metric")
```

---

### 3. Performance Analysis

#### `analyze_dax_query`

Analyzes a DAX query for performance insights and execution plan.

**Parameters:**
- `dax_query` (required): DAX query to analyze
- `workspace` (optional): Name or ID of the workspace
- `model` (optional): Name or ID of the semantic model
- `include_execution_plan` (optional): Whether to include execution plan info (default: True)
- `ctx` (optional): Context object

**Returns:**
```json
{
  "modelName": "Sales Model",
  "modelId": "abc-123",
  "workspaceId": "def-456",
  "executionTimeSeconds": 0.542,
  "query": "EVALUATE TOPN(100, Sales)",
  "rowCount": 100,
  "columns": ["OrderID", "Amount", "Date"],
  "sampleRows": [...],
  "executionPlan": {
    "note": "Full execution plan analysis requires XMLA endpoint access via external tools",
    "basicMetrics": {
      "executionTimeSeconds": 0.542,
      "rowsReturned": 100
    },
    "recommendation": "For detailed performance analysis, use DAX Studio or Tabular Editor with XMLA endpoint"
  }
}
```

**Example:**
```python
result = await analyze_dax_query(
    dax_query="EVALUATE TOPN(100, FILTER(Sales, Sales[Amount] > 1000))"
)
print(f"Query executed in {result['executionTimeSeconds']}s, returned {result['rowCount']} rows")
```

---

## Usage Workflows

### Workflow 1: Exploring a Model

```python
# 1. Get the complete schema
schema = await get_model_schema(workspace="PowerBI_Test", model="Sales Model")

# 2. Explore tables
for table in schema['tables']:
    print(f"Table: {table['name']}")
    print(f"  Columns: {len(table['columns'])}")
    print(f"  Measures: {len(table['measures'])}")

# 3. List all measures
measures = await list_measures()
print(f"Total measures: {measures['measureCount']}")
```

### Workflow 2: Creating a New Measure

```python
# 1. Check if measure already exists
existing = await get_measure(measure_name="Profit Margin")
if existing['found']:
    print("Measure already exists!")
else:
    # 2. Create the new measure
    result = await create_measure(
        measure_name="Profit Margin",
        dax_expression="DIVIDE([Total Profit], [Total Sales], 0)",
        table_name="Sales",
        format_string="0.0%",
        description="Profit margin percentage"
    )
    print(result['message'])
```

### Workflow 3: Performance Optimization

```python
# 1. Test a query and measure performance
result = await analyze_dax_query(
    dax_query="EVALUATE FILTER(Sales, Sales[Region] = \"West\")"
)

# 2. Check execution time
if result['executionTimeSeconds'] > 1.0:
    print(f"Slow query detected: {result['executionTimeSeconds']}s")
    print(f"Rows returned: {result['rowCount']}")
    # Consider optimization strategies
```

### Workflow 4: Bulk Measure Updates

```python
# 1. List all measures
measures = await list_measures()

# 2. Update format strings for currency measures
for measure in measures['measures']:
    if 'Sales' in measure['name'] or 'Revenue' in measure['name']:
        await update_measure(
            measure_name=measure['name'],
            format_string="$#,0.00"
        )
```

---

## Implementation Details

### API Endpoints Used

All tools use Microsoft Fabric REST API endpoints:

- **Model Definition**: `POST /workspaces/{workspaceId}/semanticModels/{semanticModelId}/getDefinition`
- **Model Update**: `POST /workspaces/{workspaceId}/semanticModels/{semanticModelId}/updateDefinition`
- **DAX Query**: `POST /workspaces/{workspaceId}/semanticModels/{semanticModelId}/dax/query`

### TMSL Format

Model definitions are retrieved in TMSL (Tabular Model Scripting Language) format - a JSON-based structure containing:
- Tables with columns and measures
- Relationships
- Data sources
- Security roles

### Limitations

1. **Execution Plans**: Full DAX query execution plans require XMLA endpoint access (not available via REST API)
2. **Model Size**: Large models may take time to retrieve and update
3. **Concurrent Edits**: Multiple simultaneous updates may conflict
4. **Permissions**: Requires appropriate workspace and dataset permissions

---

## Error Handling

All tools return error information in a consistent format:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common errors:
- "Workspace must be specified or set with set_workspace"
- "Model must be specified or set"
- "Table 'TableName' not found in model"
- "Measure 'MeasureName' not found in model"
- "Measure 'MeasureName' already exists in table 'TableName'"

---

## Testing

A comprehensive test script is available at `tests/debug_scripts/test_semantic_model_tools.py`.

Run tests with:
```bash
uv run python tests/debug_scripts/test_semantic_model_tools.py
```

---

## Related Tools

These tools complement existing Power BI tools:

- `dax_query` (in `tools/powerbi.py`): Execute DAX queries
- `semantic_model_refresh`: Trigger model refresh
- `list_semantic_models`: List available models
- `get_semantic_model`: Get model details

---

## Future Enhancements

Potential additions:
- Table creation/modification
- Column management
- Relationship management
- Security role management
- Partition optimization
- Incremental refresh configuration

---

**Last Updated:** November 3, 2025
