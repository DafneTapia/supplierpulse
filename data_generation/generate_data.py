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


def generar_proveedores():
    filas = []
    for i in range(1, N_SUPPLIERS + 1):
        fila = {
            "supplier_id": f"S{i:03d}",
            "name": fake.company(),
            "country": random.choice(COUNTRIES),
            "rating": round(random.uniform(2.5, 5.0), 1),
            "email": fake.company_email(),
        }
        r = random.random()
        if r < 0.06:
            fila["rating"] = None                       # rating vacío
        elif r < 0.12:
            fila["country"] = fila["country"].lower()   # "fr" en vez de "FR"
        elif r < 0.16:
            fila["name"] = f"  {fila['name']}  "        # espacios sobrantes
        filas.append(fila)
    for _ in range(3):                                  # filas duplicadas
        filas.append(dict(random.choice(filas)))
    return filas


def generar_pedidos(proveedores):
    ids = [p["supplier_id"] for p in proveedores]
    inicio = date(2025, 1, 1)
    filas, fechas_reales = [], {}
    for i in range(1, N_ORDERS + 1):
        fecha = inicio + timedelta(days=random.randint(0, 600))
        fila = {
            "order_id": f"O{i:05d}",
            "supplier_id": random.choice(ids),
            "order_date": fecha.isoformat(),
            "amount": round(random.uniform(100, 20000), 2),
            "currency": "EUR",
        }
        fechas_reales[fila["order_id"]] = fecha
        r = random.random()
        if r < 0.03:
            fila["amount"] = -fila["amount"]            # importe negativo
        elif r < 0.06:
            fila["amount"] = "N/A"                      # importe no numérico
        elif r < 0.09:
            fila["order_date"] = "31/02/2025"           # fecha imposible
        elif r < 0.12:
            fila["supplier_id"] = "S999"                # proveedor inexistente
        filas.append(fila)
    return filas, fechas_reales


def generar_entregas(pedidos, fechas_reales):
    filas = []
    for p in pedidos:
        if random.random() < 0.08:
            continue                                    # pedido sin entrega
        fecha = fechas_reales[p["order_id"]]
        cantidad = random.randint(10, 500)
        entrega = fecha + timedelta(days=random.randint(2, 20))
        fila = {
            "order_id": p["order_id"],
            "promised_date": (fecha + timedelta(days=10)).isoformat(),
            "delivered_date": entrega.isoformat(),
            "quantity_ordered": cantidad,
            "quantity_received": cantidad,
            "status": "delivered",
        }
        r = random.random()
        if r < 0.04:
            fila["delivered_date"] = (fecha - timedelta(days=3)).isoformat()  # antes del pedido
        elif r < 0.10:
            fila["quantity_received"] = int(cantidad * random.uniform(0.5, 0.95))  # entrega parcial
            fila["status"] = "partial"
        elif r < 0.14:
            fila["status"] = "DELIVERED"                # mayúsculas inconsistentes
        filas.append(fila)
    return filas


def guardar_csv(ruta, filas):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=filas[0].keys())
        writer.writeheader()
        writer.writerows(filas)


if __name__ == "__main__":
    proveedores = generar_proveedores()
    pedidos, fechas_reales = generar_pedidos(proveedores)
    entregas = generar_entregas(pedidos, fechas_reales)

    guardar_csv(OUT / "suppliers.csv", proveedores)
    guardar_csv(OUT / "orders.csv", pedidos)
    with open(OUT / "deliveries.json", "w", encoding="utf-8") as f:
        json.dump(entregas, f, indent=2, ensure_ascii=False)

    print(f"Proveedores: {len(proveedores)}, pedidos: {len(pedidos)}, entregas: {len(entregas)}")