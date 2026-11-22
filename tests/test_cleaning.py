import os
import sys

import pytest
from pyspark.sql import SparkSession

from supplierpulse.cleaning import clean_suppliers

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


@pytest.fixture(scope="session")
def spark():
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("supplierpulse-tests")
        .getOrCreate()
    )
    yield session
    session.stop()


def test_clean_suppliers_normalizes_country_and_name(spark):
    raw = spark.createDataFrame(
        [("S001", "  Acme  ", "fr", "4.5"), ("S002", "Bolt", "ES", "")],
        ["supplier_id", "name", "country", "rating"],
    )

    result = {r["supplier_id"]: r for r in clean_suppliers(raw).collect()}

    assert result["S001"]["name"] == "Acme"
    assert result["S001"]["country"] == "FR"
    assert result["S001"]["rating"] == 4.5
    assert result["S002"]["rating"] is None