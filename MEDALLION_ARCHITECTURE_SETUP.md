# Medallion Architecture Setup Guide

## Architecture Overview

```
[Source Systems]
      │  (ingest once)
      ▼
[RAW-Bronze-Central Workspace]
  └─ bronze_central lakehouse  ← immutable, append-only, prod-grade history
      │
      │  (OneLake shortcuts / read-only views)
      ├─────────────┬─────────────┐
      │             │             │
      ▼             ▼             ▼
[DEV-Analytics]  [TEST-Analytics]  [PROD-Analytics]
  ├─ silver_dev     ├─ silver_test    ├─ silver_prod
  └─ gold_dev       └─ gold_test      └─ gold_prod
```

## Infrastructure Components

### 1. RAW-Bronze-Central Workspace

- **Lakehouse:** `bronze_central`
- **Purpose:** Immutable source data from all systems
- **Pattern:** Append-only, never delete or modify
- **Tables:** Name with pattern `{source}_{entity}_raw` (e.g., `salesforce_accounts_raw`)

### 2. DEV-Analytics Workspace

- **Silver Lakehouse:** `silver_dev`
  - Cleaned and enriched data
  - **Dev-specific:** Use sampling (e.g., 10% of data) for faster iteration

- **Gold Lakehouse:** `gold_dev`
  - Business-ready dimensional models
  - Fact tables: `fact_{entity}`
  - Dimension tables: `dim_{entity}`

### 3. TEST-Analytics Workspace

- **Silver Lakehouse:** `silver_test`
  - Cleaned and enriched data
  - **Test-specific:** Apply data masking for PII/sensitive data

- **Gold Lakehouse:** `gold_test`
  - Business-ready dimensional models
  - Validate transformations match production logic

### 4. PROD-Analytics Workspace

- **Silver Lakehouse:** `silver_prod`
  - Full production data, cleaned and enriched

- **Gold Lakehouse:** `gold_prod`
  - Production-ready dimensional models
  - Optimized for reporting and analytics

> **Note:** All MCP tools accept workspace and lakehouse names, so you don't need to track IDs. Use descriptive names for clarity and portability across environments.

---

## Setting Up OneLake Shortcuts (Automated)

### What Are OneLake Shortcuts?
OneLake shortcuts allow you to reference data from the central Bronze lakehouse without duplicating it. Each environment (Dev/Test/Prod) reads from the same source Bronze data but applies environment-specific transformations.

### Automated Shortcut Creation via MCP Tools

You can now create shortcuts programmatically using the MCP tools:

```python
# Create shortcut from DEV Silver to Bronze Central
onelake_create_shortcut(
    workspace="DEV-Analytics",
    lakehouse="silver_dev",
    shortcut_name="bronze_data",
    shortcut_path="Tables",
    target_workspace="RAW-Bronze-Central",
    target_lakehouse="bronze_central",
    target_path="Tables"
)

# Repeat for TEST
onelake_create_shortcut(
    workspace="TEST-Analytics",
    lakehouse="silver_test",
    shortcut_name="bronze_data",
    shortcut_path="Tables",
    target_workspace="RAW-Bronze-Central",
    target_lakehouse="bronze_central",
    target_path="Tables"
)

# Repeat for PROD
onelake_create_shortcut(
    workspace="PROD-Analytics",
    lakehouse="silver_prod",
    shortcut_name="bronze_data",
    shortcut_path="Tables",
    target_workspace="RAW-Bronze-Central",
    target_lakehouse="bronze_central",
    target_path="Tables"
)
```

### Verify Shortcuts

List shortcuts to confirm they were created:

```python
# Check DEV shortcuts
onelake_list_shortcuts(workspace="DEV-Analytics", lakehouse="silver_dev")

# Check TEST shortcuts
onelake_list_shortcuts(workspace="TEST-Analytics", lakehouse="silver_test")

# Check PROD shortcuts
onelake_list_shortcuts(workspace="PROD-Analytics", lakehouse="silver_prod")
```

### Manual Creation (Alternative)

If you prefer manual creation via Fabric UI:

1. Navigate to each Silver lakehouse (DEV/TEST/PROD)
2. Go to "Tables" section → "New shortcut" → "Microsoft OneLake"
3. Select workspace: **RAW-Bronze-Central**, lakehouse: **bronze_central**
4. Choose tables to reference and give descriptive names

---

## Development Workflow

### Bronze Layer (Ingest Once)
```python
# In RAW-Bronze-Central workspace
# Ingest from source systems into bronze_central

# Example: Ingest from API/database/file
load_data_from_url(
    url="https://source-system.com/data.csv",
    destination_table="source_system_entities_raw",
    workspace="RAW-Bronze-Central",
    lakehouse="bronze_central"
)
```

### Silver Layer (Environment-Specific)

**DEV Environment (with sampling):**
```python
# In DEV-Analytics workspace
# Read from Bronze via shortcut, apply sampling

df = spark.table("bronze_central.source_system_entities_raw")
df_sample = df.sample(0.1)  # 10% sample for dev
df_cleaned = df_sample.dropDuplicates() \
                      .filter("status = 'active'") \
                      .withColumnRenamed("id", "entity_id")

df_cleaned.write.format("delta").mode("overwrite") \
    .saveAsTable("silver_dev.entities_clean")
```

**TEST Environment (with masking):**
```python
# In TEST-Analytics workspace
# Read from Bronze via shortcut, apply masking

from pyspark.sql.functions import sha2

df = spark.table("bronze_central.source_system_entities_raw")
df_masked = df.withColumn("email", sha2("email", 256)) \
              .withColumn("phone", sha2("phone", 256))

df_masked.write.format("delta").mode("overwrite") \
    .saveAsTable("silver_test.entities_clean")
```

**PROD Environment (full data):**
```python
# In PROD-Analytics workspace
# Read from Bronze via shortcut, full processing

df = spark.table("bronze_central.source_system_entities_raw")
df_cleaned = df.dropDuplicates() \
               .filter("status = 'active'") \
               .withColumnRenamed("id", "entity_id")

df_cleaned.write.format("delta").mode("overwrite") \
    .saveAsTable("silver_prod.entities_clean")
```

### Gold Layer (Dimensional Modeling)

```python
# Create fact table in each environment
# Example for PROD (similar pattern for Dev/Test)

# Read from Silver layer
df_silver = spark.table("silver_prod.entities_clean")

# Build dimensional model
df_fact = df_silver.select(
    "entity_id",
    "transaction_date",
    "amount",
    "customer_id",
    "product_id"
)

df_fact.write.format("delta").mode("overwrite") \
    .saveAsTable("gold_prod.fact_transactions")

# Optimize for reporting
optimize_delta(
    workspace="PROD-Analytics",
    lakehouse="gold_prod",
    table="fact_transactions",
    zorder_by=["transaction_date", "customer_id"]
)
```

---

## Optional: Orchestrating with Master Pipeline Pattern

### Why Use an Orchestrator Pipeline?

Instead of combining all transformations in one monolithic pipeline, you can create separate pipelines for each layer (Bronze, Silver, Gold) and orchestrate them with a master pipeline. This provides:

- **Separation of concerns**: Each layer has its own pipeline that can be developed/tested independently
- **Reusability**: Silver and Gold pipelines can be triggered manually or from different orchestrators
- **Easier debugging**: Clear which specific layer failed
- **Flexibility**: Run individual layers on-demand or chain them together

### Pattern Overview

```
┌─────────────────────────────────────────────────────────────────┐
│         Master Orchestrator Pipeline (scheduled nightly)        │
│                                                                   │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐  │
│  │ Execute_Bronze│───▶│ Execute_Silver│───▶│  Execute_Gold │  │
│  └───────┬───────┘    └───────┬───────┘    └───────┬───────┘  │
│          │                    │                    │            │
└──────────┼────────────────────┼────────────────────┼────────────┘
           │                    │                    │
           │ Invoke (wait)      │ Invoke (wait)      │ Invoke (wait)
           ▼                    ▼                    ▼
    ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
    │   Bronze    │      │   Silver    │      │    Gold     │
    │  Ingestion  │      │  Transform  │      │ Dimensional │
    │  Pipeline   │      │  Pipeline   │      │  Pipeline   │
    │             │      │             │      │             │
    │ [Notebook]  │      │ [Notebook]  │      │ [Notebook]  │
    │ Load raw    │      │ Clean &     │      │ Create fact │
    │ data into   │      │ enrich data │      │ & dimension │
    │ Bronze lake │      │ into Silver │      │ tables      │
    └─────────────┘      └─────────────┘      └─────────────┘
         │                      │                      │
         ▼                      ▼                      ▼
    [bronze_central]       [silver_prod]         [gold_prod]
```

**Flow:**
1. Orchestrator triggers Bronze pipeline → waits for completion
2. If Bronze succeeds → triggers Silver pipeline → waits for completion
3. If Silver succeeds → triggers Gold pipeline → waits for completion
4. Each child pipeline runs independently and can be manually triggered

### Implementation Steps

#### Step 1: Create Child Pipelines (one per layer)

```python
# Bronze layer pipeline
create_data_pipeline(
    pipeline_name="Bronze_Ingestion_PROD",
    workspace="PROD-Analytics",
    description="Ingest raw data into Bronze lakehouse",
    pipeline_definition={
        "properties": {
            "activities": [
                {
                    "name": "Run_Bronze_Notebook",
                    "type": "Notebook",
                    "typeProperties": {
                        "notebook": {
                            "referenceName": "bronze_ingest_notebook",
                            "type": "NotebookReference"
                        }
                    },
                    "dependsOn": []
                }
            ]
        }
    }
)

# Silver layer pipeline
create_data_pipeline(
    pipeline_name="Silver_Transform_PROD",
    workspace="PROD-Analytics",
    description="Clean and enrich data into Silver lakehouse",
    pipeline_definition={
        "properties": {
            "activities": [
                {
                    "name": "Run_Silver_Notebook",
                    "type": "Notebook",
                    "typeProperties": {
                        "notebook": {
                            "referenceName": "silver_transform_notebook",
                            "type": "NotebookReference"
                        }
                    },
                    "dependsOn": []
                }
            ]
        }
    }
)

# Gold layer pipeline
create_data_pipeline(
    pipeline_name="Gold_Dimensional_PROD",
    workspace="PROD-Analytics",
    description="Create dimensional models in Gold lakehouse",
    pipeline_definition={
        "properties": {
            "activities": [
                {
                    "name": "Run_Gold_Notebook",
                    "type": "Notebook",
                    "typeProperties": {
                        "notebook": {
                            "referenceName": "gold_transform_notebook",
                            "type": "NotebookReference"
                        }
                    },
                    "dependsOn": []
                }
            ]
        }
    }
)
```

#### Step 2: Create Master Orchestrator

**Important**: The orchestrator uses `Invoke` activity type with pipeline **IDs** (not names) in `referenceName`:

```python
# Note: Replace these IDs with actual IDs returned from Step 1
bronze_pipeline_id = "your-bronze-pipeline-id"
silver_pipeline_id = "your-silver-pipeline-id"
gold_pipeline_id = "your-gold-pipeline-id"

# Master orchestrator pipeline
create_data_pipeline(
    pipeline_name="Medallion_Orchestrator_PROD",
    workspace="PROD-Analytics",
    description="Orchestrates Bronze → Silver → Gold execution",
    pipeline_definition={
        "properties": {
            "activities": [
                {
                    "name": "Execute_Bronze",
                    "type": "Invoke",
                    "typeProperties": {
                        "pipeline": {
                            "referenceName": bronze_pipeline_id,
                            "type": "PipelineReference"
                        },
                        "waitOnCompletion": True
                    },
                    "dependsOn": []
                },
                {
                    "name": "Execute_Silver",
                    "type": "Invoke",
                    "typeProperties": {
                        "pipeline": {
                            "referenceName": silver_pipeline_id,
                            "type": "PipelineReference"
                        },
                        "waitOnCompletion": True
                    },
                    "dependsOn": [
                        {
                            "activity": "Execute_Bronze",
                            "dependencyConditions": ["Succeeded"]
                        }
                    ]
                },
                {
                    "name": "Execute_Gold",
                    "type": "Invoke",
                    "typeProperties": {
                        "pipeline": {
                            "referenceName": gold_pipeline_id,
                            "type": "PipelineReference"
                        },
                        "waitOnCompletion": True
                    },
                    "dependsOn": [
                        {
                            "activity": "Execute_Silver",
                            "dependencyConditions": ["Succeeded"]
                        }
                    ]
                }
            ]
        }
    }
)
```

### Key Configuration Details

- **`type: "Invoke"`**: Activity type for executing child pipelines
- **`referenceName`**: Must be the pipeline **ID** (UUID), not the display name
- **`waitOnCompletion: True`**: Parent pipeline waits for child to complete before proceeding
- **`dependencyConditions: ["Succeeded"]`**: Only proceed if previous activity succeeded

### Running the Orchestrator

**Manual trigger:**
```python
pipeline_run(
    workspace="PROD-Analytics",
    pipeline="Medallion_Orchestrator_PROD"
)
```

**Schedule for nightly runs:**
```python
schedule_set(
    workspace="PROD-Analytics",
    item="Medallion_Orchestrator_PROD",
    schedule={
        "enabled": True,
        "type": "Scheduled",
        "frequency": "Daily",
        "time": "02:00",
        "timeZone": "UTC"
    }
)
```

### Advanced: Parallel Execution

You can also run multiple pipelines in parallel by removing dependencies:

```python
# Run Silver transforms for different tables in parallel
{
    "activities": [
        {
            "name": "Execute_Silver_Customers",
            "type": "Invoke",
            "typeProperties": {
                "pipeline": {"referenceName": "silver_customers_id", "type": "PipelineReference"},
                "waitOnCompletion": False  # Don't wait, run async
            },
            "dependsOn": []
        },
        {
            "name": "Execute_Silver_Orders",
            "type": "Invoke",
            "typeProperties": {
                "pipeline": {"referenceName": "silver_orders_id", "type": "PipelineReference"},
                "waitOnCompletion": False  # Don't wait, run async
            },
            "dependsOn": []  # No dependency = runs in parallel
        }
    ]
}
```

---

## Best Practices

### Bronze Layer
- Never modify or delete data in Bronze
- Use append-only pattern for historical tracking
- Include ingestion timestamp: `_ingestion_date`, `_ingestion_time`
- Store raw data exactly as received (minimal transformation)
- Table naming: `{source_system}_{entity}_raw`

### Silver Layer
- Clean, deduplicate, and enrich data
- Apply business rules consistently across environments
- Environment-specific configs:
  - **Dev:** Sample data (10-20%) for speed
  - **Test:** Mask PII, use representative data
  - **Prod:** Full data, no sampling
- Table naming: `{entity}_clean` or `{entity}_enriched`

### Gold Layer
- Business-ready dimensional models (star schema)
- Denormalize for reporting performance
- Create aggregation tables for common queries
- Table naming: `fact_{entity}`, `dim_{entity}`, `{metric}_by_{dimension}`
- Optimize with Z-ORDER and partitioning

### Data Governance
- Document data lineage (Bronze → Silver → Gold)
- Add table and column descriptions
- Implement data quality checks at each layer
- Use Delta Lake time travel for auditing
- Apply row-level security in Prod

---

## Environment Promotion Strategy

### Code Promotion
1. Develop notebooks in **DEV-Analytics**
2. Test notebooks in **TEST-Analytics** (validate against masked data)
3. Deploy notebooks to **PROD-Analytics** via CI/CD

### Testing Strategy
- **Dev:** Rapid iteration, frequent breaks expected
- **Test:** Integration testing, data quality validation
- **Prod:** Production data, scheduled refreshes

### Deployment Checklist
- [ ] Notebooks tested in Dev with sample data
- [ ] Notebooks validated in Test with full logic
- [ ] Data quality checks passing
- [ ] Performance optimization applied (Z-ORDER, partitioning)
- [ ] Documentation updated
- [ ] Monitoring and alerting configured
- [ ] Schedule configured for production refresh

---

## Monitoring & Maintenance

### Regular Tasks
- **Bronze:** Monitor ingestion jobs, check for failures
- **Silver:** Validate data quality, check for schema drift
- **Gold:** Optimize tables monthly, vacuum old files
- **All layers:** Review query performance, adjust Z-ORDER as needed

### Helpful Commands
```python
# Check table history
describe_history(
    workspace="PROD-Analytics",
    lakehouse="gold_prod",
    table="fact_transactions",
    limit=20
)

# Optimize tables (weekly)
optimize_delta(
    workspace="PROD-Analytics",
    lakehouse="gold_prod",
    table="fact_transactions",
    zorder_by=["transaction_date"]
)

# Clean up old files (monthly)
vacuum_delta(
    workspace="PROD-Analytics",
    lakehouse="gold_prod",
    table="fact_transactions",
    retain_hours=168  # 7 days
)
```

---

## Summary

Your medallion architecture is fully automated and operational:

### Infrastructure Created:
- ✅ 1 central **RAW-Bronze-Central** workspace with `bronze_central` lakehouse (immutable source data)
- ✅ 3 environment workspaces (Dev/Test/Prod) each with Silver and Gold lakehouses
- ✅ OneLake shortcuts connecting each Silver lakehouse to the central Bronze

### Key Benefits:
- **No data duplication** - All environments read from the same Bronze source
- **Environment isolation** - Each environment applies its own transformations
- **Scalable pattern** - Ingest once in Bronze, transform per environment
- **Enterprise-ready** - Production-grade medallion architecture

### What's Connected:
```
RAW-Bronze-Central/bronze_central
    ↓ (shortcuts)
    ├─→ DEV-Analytics/silver_dev/Tables/bronze_data
    ├─→ TEST-Analytics/silver_test/Tables/bronze_data
    └─→ PROD-Analytics/silver_prod/Tables/bronze_data
```

### Ready to Use:
Your data flow is now active. Start ingesting data into Bronze, and all environments can immediately access it via shortcuts for their Silver/Gold transformations.
