"""The fix: one pure, tested feature library used by both train and serve.

Every function here takes only explicit arguments (raw data + an explicit
`as_of_date`) and returns a value. No hidden state, no wall-clock reads, no
global config. Call any function twice with the same arguments and you get
the same answer — that's the entire invariant this lesson is about.

The window/null-handling choices here are deliberate and documented, unlike
the naive scripts where they were accidental:
  - `orders_last_30d` uses an inclusive window: an order exactly 30 days
    before `as_of_date` counts.
  - `avg_order_value` returns 0.0 for a customer with no orders, not NaN —
    "no orders" is a real, meaningful state, not missing data.
"""

from __future__ import annotations

from datetime import date

import pandas as pd


def days_since_signup(signup_date: date, as_of_date: date) -> int:
    return (as_of_date - signup_date).days


def is_weekend_signup(signup_date: date) -> bool:
    return signup_date.weekday() >= 5


def orders_last_30d(order_dates: list[date], as_of_date: date) -> int:
    return sum(1 for d in order_dates if 0 <= (as_of_date - d).days <= 30)


def avg_order_value(order_amounts: list[float]) -> float:
    if not order_amounts:
        return 0.0
    return round(sum(order_amounts) / len(order_amounts), 2)


def compute_customer_features(
    signup_date: date, order_dates: list[date], order_amounts: list[float], as_of_date: date
) -> dict:
    return {
        "days_since_signup": days_since_signup(signup_date, as_of_date),
        "is_weekend_signup": is_weekend_signup(signup_date),
        "orders_last_30d": orders_last_30d(order_dates, as_of_date),
        "avg_order_value": avg_order_value(order_amounts),
    }


def build_feature_matrix(
    customers: pd.DataFrame, orders: pd.DataFrame, as_of_date: date
) -> pd.DataFrame:
    """Build the feature matrix for every customer, as of `as_of_date`.

    `customers` needs `customer_id`, `signup_date` (ISO string).
    `orders` needs `customer_id`, `order_date` (ISO string), `amount`.
    """
    orders_by_customer = {
        customer_id: group for customer_id, group in orders.groupby("customer_id")
    }

    rows = []
    for _, customer in customers.iterrows():
        customer_id = customer["customer_id"]
        signup = date.fromisoformat(customer["signup_date"])
        group = orders_by_customer.get(customer_id)
        if group is None:
            order_dates: list[date] = []
            order_amounts: list[float] = []
        else:
            order_dates = [date.fromisoformat(d) for d in group["order_date"]]
            order_amounts = list(group["amount"])

        features = compute_customer_features(signup, order_dates, order_amounts, as_of_date)
        features["customer_id"] = customer_id
        rows.append(features)

    columns = [
        "customer_id",
        "days_since_signup",
        "is_weekend_signup",
        "orders_last_30d",
        "avg_order_value",
    ]
    return pd.DataFrame(rows)[columns].sort_values("customer_id").reset_index(drop=True)
