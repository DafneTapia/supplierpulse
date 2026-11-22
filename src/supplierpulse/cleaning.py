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