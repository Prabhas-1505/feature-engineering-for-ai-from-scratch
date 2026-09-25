"""Deterministic synthetic customer/orders dataset for Lesson 00.

No network access required. Same seed always produces the same data, so the
train/serve skew demonstrated later in this lesson is reproducible.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_CUSTOMERS = 200
AS_OF_DATE = date(2026, 1, 1)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def make_customers_and_orders(
    rng: np.random.Generator, as_of_date: date = AS_OF_DATE
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build a small customers + orders dataset for a fixed `as_of_date`.

    Two rows are pinned deliberately (not left to chance) because Lesson 00
    needs them to exist every time this function runs:
      - customer 1 has an order exactly 30 days before `as_of_date`, which
        is where the naive implementations' window boundaries disagree.
      - customer 2 has zero orders, which is where the naive
        implementations' null-handling disagrees.
    """
    customer_ids = list(range(1, N_CUSTOMERS + 1))
    signup_offsets = rng.integers(30, 730, size=N_CUSTOMERS)
    signup_dates = [as_of_date - timedelta(days=int(d)) for d in signup_offsets]
    high_value = rng.integers(0, 2, size=N_CUSTOMERS)

    customers = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "signup_date": [d.isoformat() for d in signup_dates],
            "high_value": high_value,
        }
    )

    order_rows: list[dict] = []
    next_order_id = 1
    for idx, customer_id in enumerate(customer_ids):
        if customer_id == 2:
            continue  # pinned: zero orders

        n_orders = int(rng.integers(0, 6))
        signup = signup_dates[idx]
        for _ in range(n_orders):
            max_offset = max((as_of_date - signup).days, 1)
            offset = int(rng.integers(0, max_offset))
            order_date = as_of_date - timedelta(days=offset)
            amount = round(float(rng.uniform(10, 500)), 2)
            order_rows.append(
                {
                    "order_id": next_order_id,
                    "customer_id": customer_id,
                    "order_date": order_date.isoformat(),
                    "amount": amount,
                }
            )
            next_order_id += 1

    # pinned: order exactly 30 days before as_of_date for customer 1
    order_rows.append(
        {
            "order_id": next_order_id,
            "customer_id": 1,
            "order_date": (as_of_date - timedelta(days=30)).isoformat(),
            "amount": 123.45,
        }
    )

    orders = pd.DataFrame(order_rows).sort_values("order_id").reset_index(drop=True)
    return customers, orders


def main() -> None:
    rng = np.random.default_rng(SEED)
    customers, orders = make_customers_and_orders(rng)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    customers.to_csv(DATA_DIR / "customers.csv", index=False)
    orders.to_csv(DATA_DIR / "orders.csv", index=False)
    print(f"Wrote {len(customers)} customers and {len(orders)} orders to {DATA_DIR}")


if __name__ == "__main__":
    main()
