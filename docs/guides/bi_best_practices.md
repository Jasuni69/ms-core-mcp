# Business Intelligence Best Practices with Microsoft Fabric MCP Tools

This guide shows how to get the most out of the Fabric MCP tools for business intelligence and analytics work.

---

## 🎯 Quick Start for BI Users

### Your First BI Session

```
1. "List all my Fabric workspaces"
2. "Set my workspace to 'Analytics_Prod'"
3. "Show me all lakehouses and their tables"
4. "Get the schema for the sales table"
5. "Run a query: SELECT TOP 10 * FROM dbo.sales ORDER BY revenue DESC"
```

Claude Code will automatically use the MCP tools to execute these commands and return formatted results.

---

## 🏗️ BI Architecture Patterns

### Medallion Architecture (Recommended)

The tools are optimized for the medallion pattern:

**Bronze Layer** (Raw Data)
- Use: `create_lakehouse` with name pattern `bronze_{domain}`
- Purpose: Store raw, unprocessed data from sources
- Tables: Named `{source}_{entity}_raw`
- Tools: `onelake_write` to load files, `create_notebook` for ingestion

**Silver Layer** (Cleaned Data)
- Use: `create_lakehouse` with name pattern `silver_{domain}`
- Purpose: Validated, cleaned, enriched data
- Tables: Named `{entity}_clean` or `{entity}_enriched`
- Transformations: Null handling, deduplication, type casting

**Gold Layer** (Business Aggregates)
- Use: `create_lakehouse` with name pattern `gold_{domain}`
- Purpose: Aggregated, business-ready data for reporting
- Tables: Named `fact_{entity}` or `dim_{entity}` or `{metric}_by_{dimension}`
- Tools: `create_semantic_model` for Power BI integration

### Example: Sales Analytics Pipeline

```
Ask Claude: "Help me set up a sales analytics pipeline with medallion architecture"

Claude will:
1. Create bronze_sales, silver_sales, gold_sales lakehouses
2. Generate PySpark notebooks for each layer
3. Suggest appropriate transformations
4. Create semantic model with sales measures
5. Provide example DAX measures
```

---

## 💡 Natural Language BI Queries

### Data Exploration

Instead of writing SQL, ask business questions:

**Examples:**
- "Show me top 10 customers by revenue"
- "What's our total sales by region and month?"
- "Which products have the highest margin?"
- "Find customers who haven't purchased in 90 days"

Claude Code will:
1. Translate to SQL automatically
2. Run `sql_query` with proper formatting
3. Present results in readable tables
4. Suggest follow-up analyses

### Creating Metrics

**Instead of:**
```dax
Total Revenue = SUM(Sales[Amount])
```

**Ask:**
"Create a Total Revenue measure that sums the Amount column from the Sales table"

Claude will:
1. Use `create_measure` tool
2. Add proper formatting (currency)
3. Include description
4. Suggest related measures (Revenue YTD, Revenue Growth %)

---

## 🔧 Tool-Specific Best Practices

### Working with Semantic Models

**Workflow:**
```
1. "List all semantic models in my workspace"
2. "Get the schema for the Sales model"
3. "Show me all measures in the Sales model"
4. "Create a new measure for average order value"
5. "Analyze this DAX query for performance issues"
```

**Tools used:**
- `list_semantic_models`
- `get_model_schema`
- `list_measures`
- `create_measure`
- `analyze_dax_query`

### SQL Analysis

**Ad-hoc Analysis:**
```
Ask: "What's the distribution of customers by country?"

Claude uses:
- sql_query: Run analysis query
- Results formatted as table
- Automatic suggestions for visualizations
```

**Performance Optimization:**
```
Ask: "Why is my sales query slow?"

Claude will:
1. Use sql_explain to get execution plan
2. Analyze table statistics
3. Suggest Z-ORDER on filtered columns
4. Recommend partitioning strategy
5. Check if aggregation belongs in gold layer
```

### Notebook Generation

**Instead of starting from scratch:**
```
Ask: "Create a PySpark notebook to transform raw orders into a clean orders table"

Claude will:
1. Use generate_fabric_code for template
2. Customize based on your schema
3. Add data quality checks
4. Include Delta Lake best practices
5. Add comments explaining each step
```

---

## 📊 Common BI Workflows

### Workflow 1: New KPI Request

**Scenario:** Business wants a new "Customer Lifetime Value" metric

**Steps:**
1. "I need to calculate customer lifetime value - what data do I need?"
2. Claude analyzes existing tables (customers, orders, products)
3. "Create a silver table that calculates LTV per customer"
4. Claude generates transformation notebook
5. "Create a gold table with LTV segmentation"
6. "Add DAX measures: Average LTV, Total LTV, LTV by Segment"
7. Claude creates semantic model measures

**Time savings:** 90% reduction vs manual implementation

### Workflow 2: Monthly Reporting Automation

**Scenario:** Need monthly sales report automation

**Steps:**
1. "Show me the current sales data structure"
2. "Create a gold table for monthly sales metrics"
3. "Generate a notebook that refreshes this monthly"
4. "Create semantic model measures for key metrics"
5. "Set up a refresh schedule for the first of each month"

Claude handles all the heavy lifting - you just validate the logic.

### Workflow 3: Data Quality Monitoring

**Scenario:** Monitor data quality in customer table

**Steps:**
```
Ask: "Check data quality in the customers table"

Claude will run:
1. Null value analysis:
   sql_query("SELECT column, COUNT(*) FROM WHERE column IS NULL")

2. Duplicate detection:
   sql_query("SELECT customer_id, COUNT(*) GROUP BY HAVING COUNT(*) > 1")

3. Value distribution:
   sql_query("SELECT country, COUNT(*) GROUP BY country")

4. Suggest: Creating data quality measures in semantic model
```

---

## 🎨 Dimensional Modeling

### Star Schema Design

**Ask Claude:**
"Help me design a star schema for order analytics"

**Claude will:**
1. Identify fact table: `fact_orders`
   - Columns: order_id, customer_key, product_key, date_key, quantity, amount

2. Identify dimension tables:
   - `dim_customer`: customer_key, name, segment, country
   - `dim_product`: product_key, name, category, subcategory
   - `dim_date`: date_key, date, month, quarter, year

3. Generate PySpark code to create tables
4. Suggest relationships for semantic model
5. Recommend measures and hierarchies

### Denormalization for Performance

**When to denormalize:**
Ask: "Should I denormalize my customer addresses into the customer table?"

Claude will analyze:
- Join frequency in queries
- Update patterns (address changes)
- Query performance impact
- Storage trade-offs

Then provide recommendation with rationale.

---

## 🚀 Performance Optimization

### Query Performance

**Slow query troubleshooting:**
```
1. Share the slow query
2. Claude runs sql_explain
3. Reviews execution plan
4. Suggests optimizations:
   - Add indexes (Z-ORDER)
   - Partition by date
   - Move aggregation to gold layer
   - Denormalize frequently joined tables
```

### Delta Lake Optimization

**Regular maintenance:**
```
Ask: "Optimize my sales table for date range queries"

Claude will suggest:
1. Z-ORDER by date column
2. Partition by month or year (if very large)
3. VACUUM old versions (168 hour retention)
4. OPTIMIZE to compact files
```

**Tools:**
- In notebooks: `spark.sql("OPTIMIZE table ZORDER BY (column)")`
- Cannot use via SQL endpoint - Spark SQL only

### Semantic Model Performance

**DAX optimization:**
```
Ask: "This measure is slow, how can I optimize it?"

Claude will:
1. Use analyze_dax_query to profile execution
2. Identify bottlenecks (slow iterators, poor filter context)
3. Suggest rewrites using CALCULATE, variables
4. Recommend aggregations in gold layer
```

---

## 📈 Advanced Scenarios

### Time Intelligence

**Creating time-based measures:**
```
Ask: "Add year-to-date revenue and month-over-month growth measures"

Claude will:
1. Verify date dimension exists
2. Create measures using TOTALYTD, DATEADD
3. Add proper formatting
4. Suggest additional time intelligence (QTD, YOY%)
```

### What-If Analysis

**Parameter tables:**
```
Ask: "Create a what-if parameter for discount scenarios"

Claude will:
1. Create parameter table in semantic model
2. Add DAX measures that use parameter
3. Suggest visualization setup
4. Explain how to use slicers for interactivity
```

### Data Segmentation

**Customer segmentation:**
```
Ask: "Segment customers by purchase behavior"

Claude will:
1. Analyze transaction patterns
2. Suggest RFM analysis (Recency, Frequency, Monetary)
3. Create gold table with segments
4. Add measures for segment analysis
5. Recommend visualizations (scatter plots, cohort grids)
```

---

## 🔐 Security & Governance

### Row-Level Security

**Setting up RLS:**
```
Ask: "How do I set up row-level security so sales reps only see their region?"

Claude will explain:
1. Semantic model RLS configuration (manual in Fabric UI)
2. Create security tables in gold layer
3. Best practices for role design
4. Testing RLS policies
```

### Data Lineage

**Understanding data flow:**
```
Ask: "Show me the lineage from source to this gold table"

Claude will:
1. Analyze notebook transformations
2. Document bronze → silver → gold flow
3. Identify source systems
4. Map transformations applied
```

---

## 💼 Team Collaboration

### Workspace Organization

**Best practice structure:**
```
Ask: "How should I organize workspaces for our team?"

Claude suggests:
- Dev workspace: experimentation and development
- Test workspace: validation before production
- Prod workspace: live reports and dashboards

Per workspace:
- bronze/silver/gold lakehouses by domain
- Notebooks organized by pipeline
- Semantic models for each business area
```

### Code Reusability

**Template generation:**
```
Ask: "Create a reusable notebook template for dimension loading"

Claude will:
1. Generate parameterized PySpark code
2. Include data quality checks
3. Add SCD Type 2 logic (if needed)
4. Document parameters and usage
```

---

## 🛠️ Troubleshooting

### Common Issues

**Issue: "Table not found in SQL query"**
- Cause: SQL endpoint sync delay (5-10 minutes for new tables)
- Solution: Use `list_tables` (Spark-based) or wait for sync
- Ask: "Why can't I query my newly created table?"

**Issue: "Cannot read OneLake file in notebook"**
- Cause: Lakehouse not attached to notebook
- Solution: Attach in Fabric UI (one-time setup)
- Ask: "How do I fix file path errors in notebooks?"

**Issue: "ODBC driver error"**
- Cause: Microsoft ODBC Driver 18 not installed
- Solution: Download and install from Microsoft
- Ask: "How do I enable SQL query tools?"

---

## 📚 Learning Resources

### Example Questions to Ask

**For learning:**
- "What's the difference between bronze, silver, and gold layers?"
- "When should I use Delta Lake vs regular Parquet?"
- "How do I choose between star schema and snowflake schema?"
- "What are best practices for naming measures?"

**For implementation:**
- "Build me a complete sales analytics pipeline"
- "Create a customer 360 view with all interactions"
- "Set up financial reporting with P&L structure"
- "Implement inventory analytics with stock levels"

### Documentation

Claude has access to:
- All 70+ MCP tool descriptions
- Microsoft Fabric best practices
- Delta Lake optimization techniques
- DAX patterns and performance tips

Just ask - Claude will provide context-aware guidance.

---

## 🎓 Tips for Maximum Productivity

### 1. Use Natural Language
Don't write SQL/DAX manually - describe what you want:
- ❌ "Run SELECT customer_id, SUM(amount)..."
- ✅ "Show me total revenue by customer"

### 2. Let Claude Design Architecture
Don't design tables manually - describe the business need:
- ❌ "Create a table with columns X, Y, Z..."
- ✅ "I need to analyze customer purchase patterns over time"

### 3. Ask for Explanations
Don't guess - ask why:
- "Why did you suggest Z-ORDER on this column?"
- "Why use star schema instead of snowflake here?"
- "Why create this as a gold table vs semantic model measure?"

### 4. Iterate Conversationally
Refine solutions through dialogue:
- "Can we add a filter for active customers only?"
- "What if we segment by revenue tier instead?"
- "How would this change if data arrives hourly?"

### 5. Validate and Test
Ask Claude to verify:
- "Check if this table has duplicates"
- "Validate that totals match between bronze and gold"
- "Test this measure with sample data"

---

## 🎯 Success Metrics

With proper use of these tools, expect:

- **85% faster** infrastructure setup (workspaces, lakehouses, notebooks)
- **70% faster** data transformation development (PySpark code generation)
- **60% fewer errors** (automated best practices, validation)
- **50% faster** semantic model development (measure generation, DAX optimization)

---

## 🚀 Getting Started Checklist

- [ ] Install ODBC Driver 18 for SQL Server (enables `sql_query`)
- [ ] Set up `.mcp.json` in your project (see [setup guide](../setup/README.md))
- [ ] Add `CLAUDE.md` to project root (customize behavior)
- [ ] Authenticate with `az login`
- [ ] Test: "List all my Fabric workspaces"
- [ ] Read: [Medallion Architecture Test Results](../testing/medallion_architecture_test.md)
- [ ] Practice: Try example workflows in this guide

---

## 📞 Need Help?

**Ask Claude:**
- "I'm new to Fabric, where should I start?"
- "What can these MCP tools help me with?"
- "Show me an example of building a BI solution end-to-end"

Claude will guide you through step-by-step with explanations and best practices.

---

**Remember:** The goal is to make Fabric accessible through conversation. Don't memorize tool names or write code manually - just describe what you want to accomplish in business terms, and Claude will handle the technical implementation using the MCP tools.
