# Medallion Architecture - Notebook Code

## 📋 Notebook 1: Bronze Layer - CSV Ingestion

**Notebook Name:** `01_Bronze_Ingest_Customer_Data`

```python
# Cell 1: Initialize and read CSV from OneLake Files
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

print(f"Spark version: {spark.version}")

# Read the CSV file from OneLake Files area
df_csv = spark.read \
    .format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("Files/raw/customers/customer_data_20251103.csv")

print(f"Loaded {df_csv.count()} customer records")
df_csv.printSchema()
df_csv.show()
```

```python
# Cell 2: Write to Bronze Delta table
df_csv.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("customers_raw")

print(f"Successfully wrote {df_csv.count()} records to bronze table 'customers_raw'")

# Verify the write
verification_df = spark.table("customers_raw")
print(f"Verification - Table now has {verification_df.count()} records")
verification_df.show()
```

---

## 📋 Notebook 2: Silver Layer - Data Cleaning & Transformation

**Notebook Name:** `02_Silver_Transform_Customers`

```python
# Cell 1: Read from Bronze and clean data
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from delta.tables import DeltaTable

# Read from bronze lakehouse
df_bronze = spark.table("bronze_customer_data.customers_raw")

print(f"Bronze records: {df_bronze.count()}")
df_bronze.show()
```

```python
# Cell 2: Apply transformations and data quality rules
# Clean and transform data
df_silver = df_bronze \
    .filter(col("customer_id").isNotNull()) \
    .filter(col("email").isNotNull()) \
    .withColumn("full_name", concat_ws(" ", col("first_name"), col("last_name"))) \
    .withColumn("signup_year", year(col("signup_date"))) \
    .withColumn("signup_month", month(col("signup_date"))) \
    .withColumn("is_high_value", when(col("lifetime_value") > 2000, lit(True)).otherwise(lit(False))) \
    .withColumn("purchase_tier",
        when(col("total_purchases") >= 7, lit("Platinum"))
        .when(col("total_purchases") >= 5, lit("Gold"))
        .when(col("total_purchases") >= 3, lit("Silver"))
        .otherwise(lit("Bronze"))
    ) \
    .withColumn("processed_timestamp", current_timestamp())

print(f"Silver records after cleaning: {df_silver.count()}")
df_silver.printSchema()
df_silver.show()
```

```python
# Cell 3: Write to Silver Delta table
# Change lakehouse context to silver_customers
# Note: In Fabric UI, add silver_customers lakehouse to this notebook

df_silver.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("silver_customers.customers_clean")

print("Successfully wrote to silver layer!")

# Verify
silver_check = spark.table("silver_customers.customers_clean")
print(f"Silver table has {silver_check.count()} records")
silver_check.show()
```

---

## 📋 Notebook 3: Gold Layer - Business Aggregations

**Notebook Name:** `03_Gold_Customer_Metrics`

```python
# Cell 1: Read from Silver
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window
from delta.tables import DeltaTable

# Read from silver lakehouse
df_silver = spark.table("silver_customers.customers_clean")

print(f"Silver records: {df_silver.count()}")
df_silver.show()
```

```python
# Cell 2: Create business-ready aggregations for gold layer
# Customer metrics by country
df_country_metrics = df_silver.groupBy("country").agg(
    count("customer_id").alias("total_customers"),
    sum("total_purchases").alias("total_purchases"),
    round(avg("lifetime_value"), 2).alias("avg_lifetime_value"),
    round(sum("lifetime_value"), 2).alias("total_revenue"),
    count(when(col("is_high_value") == True, 1)).alias("high_value_customers")
).orderBy(desc("total_revenue"))

print("Country-level metrics:")
df_country_metrics.show()
```

```python
# Cell 3: Customer tier analysis
df_tier_metrics = df_silver.groupBy("purchase_tier").agg(
    count("customer_id").alias("customer_count"),
    round(avg("lifetime_value"), 2).alias("avg_lifetime_value"),
    round(avg("total_purchases"), 2).alias("avg_purchases"),
    round(sum("lifetime_value"), 2).alias("total_tier_revenue")
).orderBy("purchase_tier")

print("Customer tier metrics:")
df_tier_metrics.show()
```

```python
# Cell 4: Time-based cohort analysis
df_cohort_metrics = df_silver.groupBy("signup_year", "signup_month").agg(
    count("customer_id").alias("new_customers"),
    round(avg("lifetime_value"), 2).alias("avg_cohort_ltv"),
    round(sum("lifetime_value"), 2).alias("cohort_revenue")
).orderBy("signup_year", "signup_month")

print("Cohort analysis:")
df_cohort_metrics.show()
```

```python
# Cell 5: Write all metrics to Gold layer
# Note: In Fabric UI, add gold_customer_metrics lakehouse to this notebook

# Write country metrics
df_country_metrics.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("gold_customer_metrics.country_metrics")

# Write tier metrics
df_tier_metrics.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("gold_customer_metrics.tier_metrics")

# Write cohort metrics
df_cohort_metrics.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("gold_customer_metrics.cohort_metrics")

print("✅ Successfully wrote all gold layer metrics!")
print(f"- Country metrics: {df_country_metrics.count()} records")
print(f"- Tier metrics: {df_tier_metrics.count()} records")
print(f"- Cohort metrics: {df_cohort_metrics.count()} records")
```

---

## 🚀 Usage Instructions

1. **Open the notebooks in Fabric UI:**
   - Navigate to workspace: `Medallion_Architecture_Test`
   - Open notebook: `01_Bronze_Ingest_Customer_Data`

2. **Configure lakehouse connections:**
   - For Notebook 1: Add `bronze_customer_data` lakehouse
   - For Notebook 2: Add both `bronze_customer_data` and `silver_customers` lakehouses
   - For Notebook 3: Add both `silver_customers` and `gold_customer_metrics` lakehouses

3. **Run notebooks sequentially:**
   - Run all cells in Notebook 1 first (bronze ingestion)
   - Then run Notebook 2 (silver transformation)
   - Finally run Notebook 3 (gold aggregation)

4. **Verify results using MCP tools:**
   - Use `table_preview` to check data
   - Use `table_schema` to verify structure
   - Use `sql_query` to run ad-hoc queries

---

## 📊 Expected Outcomes

**Bronze Layer:**
- Table: `customers_raw` (10 records)

**Silver Layer:**
- Table: `customers_clean` (10 records, enriched with calculated fields)

**Gold Layer:**
- Table: `country_metrics` (~10 records, one per country)
- Table: `tier_metrics` (4 records: Platinum, Gold, Silver, Bronze)
- Table: `cohort_metrics` (~4 records for different signup months)
