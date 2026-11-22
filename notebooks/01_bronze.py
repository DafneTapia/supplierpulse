# Databricks notebook source
from pyspark.sql import functions as F

BASE = "/Volumes/workspace/default/supplierpulse"

def add_metadata(df):
    """Add traceability columns to a raw DataFrame."""
    return (
        df.withColumn("_ingested_at", F.current_timestamp())
          .withColumn("_source_file", F.col("_metadata.file_path"))
    )

suppliers = add_metadata(
    spark.read.option("header", True).csv(f"{BASE}/suppliers.csv")
)
orders = add_metadata(
    spark.read.option("header", True).csv(f"{BASE}/orders.csv")
)
deliveries = add_metadata(
    spark.read.option("multiLine", True).json(f"{BASE}/deliveries.json")
)

for name, df in [("suppliers", suppliers), ("orders", orders), ("deliveries", deliveries)]:
    df.write.mode("overwrite").saveAsTable(f"workspace.default.bronze_{name}")
    print(f"bronze_{name}: {df.count()} rows")