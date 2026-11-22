from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def clean_suppliers(df: DataFrame) -> DataFrame:
    """Normalize country codes, trim names and cast rating to double."""
    return (
        df.withColumn("name", F.trim(F.col("name")))
          .withColumn("country", F.upper(F.trim(F.col("country"))))
          .withColumn("rating", F.expr("try_cast(trim(rating) as double)"))
    )