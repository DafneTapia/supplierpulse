from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def clean_suppliers(df: DataFrame) -> DataFrame:
    """Normalize country codes, trim names and cast rating to double."""
    return (
        df.withColumn("name", F.trim(F.col("name")))
          .withColumn("country", F.upper(F.trim(F.col("country"))))
          .withColumn("rating", F.expr("try_cast(trim(rating) as double)"))
    )


def clean_orders(df: DataFrame) -> DataFrame:
    """Cast types and flag invalid rows with a rejection reason."""
    typed = (
        df.withColumn("amount", F.expr("try_cast(trim(amount) as double)"))
          .withColumn("order_date", F.expr("try_to_date(trim(order_date), 'yyyy-MM-dd')"))
    )
    return typed.withColumn(
        "reject_reason",
        F.when(F.col("amount").isNull(), "invalid_amount")
         .when(F.col("amount") <= 0, "non_positive_amount")
         .when(F.col("order_date").isNull(), "invalid_date"),
    )


def clean_deliveries(df: DataFrame) -> DataFrame:
    """Normalize status, cast dates and flag partial and late deliveries."""
    return (
        df.withColumn("status", F.lower(F.trim(F.col("status"))))
          .withColumn("promised_date", F.expr("try_to_date(promised_date, 'yyyy-MM-dd')"))
          .withColumn("delivered_date", F.expr("try_to_date(delivered_date, 'yyyy-MM-dd')"))
          .withColumn("is_partial", F.col("quantity_received") < F.col("quantity_ordered"))
          .withColumn("is_late", F.col("delivered_date") > F.col("promised_date"))
    )