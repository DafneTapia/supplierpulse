import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

fake = Faker("fr_FR")
Faker.seed(42)
random.seed(42)

OUT = Path("data")
OUT.mkdir(exist_ok=True)

N_SUPPLIERS = 50
N_ORDERS = 500
COUNTRIES = ["FR", "ES", "DE", "IT", "PL"]


def generate_suppliers():
    rows = []
    for i in range(1, N_SUPPLIERS + 1):
        row = {
            "supplier_id": f"S{i:03d}",
            "name": fake.company(),
            "country": random.choice(COUNTRIES),
            "rating": round(random.uniform(2.5, 5.0), 1),
            "email": fake.company_email(),
        }
        r = random.random()
        if r < 0.06:
            row["rating"] = None                        # missing rating
        elif r < 0.12:
            row["country"] = row["country"].lower()     # "fr" instead of "FR"
        elif r < 0.16:
            row["name"] = f"  {row['name']}  "          # extra whitespace
        rows.append(row)
    for _ in range(3):                                  # duplicated rows
        rows.append(dict(random.choice(rows)))
    return rows


def generate_orders(suppliers):
    supplier_ids = [s["supplier_id"] for s in suppliers]
    start = date(2025, 1, 1)
    rows, true_dates = [], {}
    for i in range(1, N_ORDERS + 1):
        order_date = start + timedelta(days=random.randint(0, 600))
        row = {
            "order_id": f"O{i:05d}",
            "supplier_id": random.choice(supplier_ids),
            "order_date": order_date.isoformat(),
            "amount": round(random.uniform(100, 20000), 2),
            "currency": "EUR",
        }
        true_dates[row["order_id"]] = order_date
        r = random.random()
        if r < 0.03:
            row["amount"] = -row["amount"]              # negative amount
        elif r < 0.06:
            row["amount"] = "N/A"                       # non-numeric amount
        elif r < 0.09:
            row["order_date"] = "31/02/2025"            # impossible date
        elif r < 0.12:
            row["supplier_id"] = "S999"                 # unknown supplier
        rows.append(row)
    return rows, true_dates


def generate_deliveries(orders, true_dates):
    rows = []
    for order in orders:
        if random.random() < 0.08:
            continue                                    # order without delivery
        order_date = true_dates[order["order_id"]]
        quantity = random.randint(10, 500)
        delivered = order_date + timedelta(days=random.randint(2, 20))
        row = {
            "order_id": order["order_id"],
            "promised_date": (order_date + timedelta(days=10)).isoformat(),
            "delivered_date": delivered.isoformat(),
            "quantity_ordered": quantity,
            "quantity_received": quantity,
            "status": "delivered",
        }
        r = random.random()
        if r < 0.04:
            row["delivered_date"] = (order_date - timedelta(days=3)).isoformat()  # delivered before order
        elif r < 0.10:
            row["quantity_received"] = int(quantity * random.uniform(0.5, 0.95))  # partial delivery
            row["status"] = "partial"
        elif r < 0.14:
            row["status"] = "DELIVERED"                 # inconsistent casing
        rows.append(row)
    return rows


def save_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    suppliers = generate_suppliers()
    orders, true_dates = generate_orders(suppliers)
    deliveries = generate_deliveries(orders, true_dates)

    save_csv(OUT / "suppliers.csv", suppliers)
    save_csv(OUT / "orders.csv", orders)
    with open(OUT / "deliveries.json", "w", encoding="utf-8") as f:
        json.dump(deliveries, f, indent=2, ensure_ascii=False)

    print(f"Suppliers: {len(suppliers)}, orders: {len(orders)}, deliveries: {len(deliveries)}")