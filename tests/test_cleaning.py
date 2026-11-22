import os
import sys

import pytest
from pyspark.sql import SparkSession

from supplierpulse.cleaning import clean_suppliers, clean_orders, clean_deliveries

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


def test_clean_orders_flags_invalid_rows(spark):
    raw = spark.createDataFrame(
        [
            ("O1", "S001", "2025-03-14", "100.5"),
            ("O2", "S001", "2025-03-14", "N/A"),
            ("O3", "S001", "2025-03-14", "-50"),
            ("O4", "S001", "31/02/2025", "200"),
        ],
        ["order_id", "supplier_id", "order_date", "amount"],
    )

    result = {r["order_id"]: r for r in clean_orders(raw).collect()}

    assert result["O1"]["reject_reason"] is None
    assert result["O2"]["reject_reason"] == "invalid_amount"
    assert result["O3"]["reject_reason"] == "non_positive_amount"
    assert result["O4"]["reject_reason"] == "invalid_date"


def test_clean_deliveries_normalizes_status_and_flags(spark):
    raw = spark.createDataFrame(
        [
            ("O1", "2025-03-24", "2025-03-20", 100, 100, "DELIVERED"),
            ("O2", "2025-03-24", "2025-03-28", 100, 60, "partial"),
        ],
        ["order_id", "promised_date", "delivered_date",
         "quantity_ordered", "quantity_received", "status"],
    )

    result = {r["order_id"]: r for r in clean_deliveries(raw).collect()}

    assert result["O1"]["status"] == "delivered"
    assert result["O1"]["is_late"] is False
    assert result["O2"]["is_partial"] is True
    assert result["O2"]["is_late"] is True