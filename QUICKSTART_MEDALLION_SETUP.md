# Quickstart: Automated Medallion Architecture Setup

## What This Does

This guide automates the creation of a production-ready medallion architecture in Microsoft Fabric with:
- Central Bronze lakehouse for immutable raw data
- Separate Dev/Test/Prod environments with Silver (cleaned) and Gold (dimensional) lakehouses
- Automated OneLake shortcuts connecting all environments to Bronze (no data duplication)

## Prerequisites

- Microsoft Fabric workspace access
- MCP server running with Fabric authentication
- Trial capacity ID (optional): `33b5b3ba-a330-4efc-bbb0-23c9da4f4008`

## Complete Setup (Copy & Run)

### Step 1: Create Infrastructure

Ask the AI:
> "Create a medallion architecture with these components:
> 1. RAW-Bronze-Central workspace with bronze_central lakehouse
> 2. DEV-Analytics workspace with silver_dev and gold_dev lakehouses
> 3. TEST-Analytics workspace with silver_test and gold_test lakehouses
> 4. PROD-Analytics workspace with silver_prod and gold_prod lakehouses"

The AI will execute:
```python
# Create Bronze workspace
create_workspace(
    display_name="RAW-Bronze-Central",
    description="Central immutable Bronze layer",
    capacity_id="33b5b3ba-a330-4efc-bbb0-23c9da4f4008"
)
create_lakehouse(name="bronze_central", workspace="RAW-Bronze-Central")

# Create DEV workspace
create_workspace(display_name="DEV-Analytics", capacity_id="...")
create_lakehouse(name="silver_dev", workspace="DEV-Analytics")
create_lakehouse(name="gold_dev", workspace="DEV-Analytics")

# Repeat for TEST and PROD...
```

### Step 2: Connect Environments via Shortcuts

Ask the AI:
> "Create OneLake shortcuts from each Silver lakehouse (DEV/TEST/PROD) to the central Bronze lakehouse"

The AI will execute:
```python
# DEV → Bronze
onelake_create_shortcut(
    workspace="DEV-Analytics",
    lakehouse="silver_dev",
    shortcut_name="bronze_data",
    shortcut_path="Tables",
    target_workspace="RAW-Bronze-Central",
    target_lakehouse="bronze_central",
    target_path="Tables"
)

# TEST → Bronze (repeat)
# PROD → Bronze (repeat)
```

### Step 3: Verify Setup

Ask the AI:
> "List the OneLake shortcuts in each Silver lakehouse to confirm they're connected"

The AI will verify all shortcuts are operational.

## Architecture Result

```
[Source Systems]
      │  (ingest once)
      ▼
[RAW-Bronze-Central]
  └─ bronze_central ← immutable raw data
      │
      │  (OneLake shortcuts - no duplication)
      ├─────────────┬─────────────┐
      ▼             ▼             ▼
[DEV-Analytics] [TEST-Analytics] [PROD-Analytics]
  ├─ silver_dev   ├─ silver_test   ├─ silver_prod
  └─ gold_dev     └─ gold_test     └─ gold_prod
```

## Usage After Setup

### Reading Bronze Data in Any Environment

In Dev/Test/Prod notebooks:
```python
# Read from Bronze via shortcut
df = spark.table("bronze_data.customers_raw")

# Apply environment-specific processing
# DEV: Sample 10% for speed
df_dev = df.sample(0.1)

# TEST: Mask PII
df_test = df.withColumn("email", sha2("email", 256))

# PROD: Full data
df_prod = df  # no sampling
```

### Silver Transformations

```python
# Clean and enrich
df_silver = df.dropDuplicates() \
              .filter("status = 'active'") \
              .withColumnRenamed("id", "customer_id")

df_silver.write.format("delta").mode("overwrite") \
    .saveAsTable("silver_dev.customers_clean")
```

### Gold Dimensional Models

```python
# Create fact table
df_fact = spark.sql("""
    SELECT
        customer_id,
        order_date,
        amount,
        product_id
    FROM silver_dev.orders_clean
""")

df_fact.write.format("delta").mode("overwrite") \
    .saveAsTable("gold_dev.fact_sales")

# Optimize for reporting
optimize_delta(
    workspace="DEV-Analytics",
    lakehouse="gold_dev",
    table="fact_sales",
    zorder_by=["order_date", "customer_id"]
)
```

## Naming Conventions

### Bronze (Raw Data)
- Pattern: `{source}_{entity}_raw`
- Examples: `salesforce_accounts_raw`, `api_orders_raw`
- Never modify, only append

### Silver (Cleaned Data)
- Pattern: `{entity}_clean` or `{entity}_enriched`
- Examples: `customers_clean`, `orders_enriched`
- Apply business rules, dedupe, type conversions

### Gold (Dimensional)
- Facts: `fact_{entity}` (e.g., `fact_sales`, `fact_transactions`)
- Dimensions: `dim_{entity}` (e.g., `dim_customer`, `dim_product`)
- Aggregations: `{metric}_by_{dimension}` (e.g., `revenue_by_region`)

## Available MCP Tools for Shortcuts

### Create Shortcut
```python
onelake_create_shortcut(
    workspace="source-workspace",
    lakehouse="source-lakehouse",
    shortcut_name="shortcut-name",
    shortcut_path="Tables",  # or "Files"
    target_workspace="target-workspace",
    target_lakehouse="target-lakehouse",
    target_path="Tables"
)
```

### List Shortcuts
```python
onelake_list_shortcuts(
    workspace="workspace-name",
    lakehouse="lakehouse-name"
)
```

### Delete Shortcut
```python
onelake_delete_shortcut(
    workspace="workspace-name",
    lakehouse="lakehouse-name",
    shortcut_path="Tables",
    shortcut_name="shortcut-name"
)
```

## Environment-Specific Patterns

### DEV Environment
- **Purpose:** Rapid iteration, experimentation
- **Data:** Sample 10-20% of Bronze for speed
- **Quality:** Frequent breaks expected
- **Optimization:** Skip for speed

### TEST Environment
- **Purpose:** Integration testing, validation
- **Data:** Full Bronze with PII masking
- **Quality:** Must match production logic
- **Optimization:** Optional

### PROD Environment
- **Purpose:** Production reporting and analytics
- **Data:** Full Bronze, no sampling
- **Quality:** Production-grade, monitored
- **Optimization:** Required (Z-ORDER, partitioning)

## Promotion Strategy

1. **Develop in DEV** → Test with sample data
2. **Validate in TEST** → Full data, masked PII
3. **Deploy to PROD** → Production data, scheduled refreshes

Code is promoted (notebooks, pipelines), not data. All environments read from the same Bronze source.

## Troubleshooting

### Issue: Can't see Bronze data in Silver
**Solution:** Check OneLake shortcuts exist using `onelake_list_shortcuts`

### Issue: Shortcuts not visible in Fabric UI
**Solution:** Refresh the lakehouse in Fabric UI, wait 1-2 minutes for sync

### Issue: "Workspace not set" error
**Solution:** Run `set_workspace("workspace-name")` before operations

## Next Steps After Setup

1. **Ingest data into Bronze:** Use `load_data_from_url()` or create ingestion notebooks
2. **Build Silver transformations:** Create notebooks to clean/enrich Bronze data
3. **Design Gold models:** Implement star schema with facts and dimensions
4. **Create semantic models:** Build Power BI models on top of Gold
5. **Add monitoring:** Track data quality, refresh status, query performance

## Summary

This setup provides a complete, automated, production-ready medallion architecture where:
- Bronze stores immutable raw data (ingest once)
- Silver provides cleaned/enriched views per environment
- Gold delivers business-ready dimensional models
- OneLake shortcuts eliminate data duplication
- Environment separation enables safe development workflow

Read [MEDALLION_ARCHITECTURE_SETUP.md](MEDALLION_ARCHITECTURE_SETUP.md) for detailed documentation.
