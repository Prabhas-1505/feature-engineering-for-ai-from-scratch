"""The naive implementation, training side.

This is how a training notebook typically starts: features computed inline,
whatever choices happen to make the training pipeline work. Nobody wrote
these choices down anywhere — they live only in this file.

Two choices matter for what happens next (see `naive_serve.py`):
  - `orders_last_30d` uses a *strict* window: an order exactly 30 days
    before `as_of_date` does NOT count.
  - `avg_order_value` for a customer with zero orders is filled to 0.0,
    because `LogisticRegression` can't handle NaN in the training matrix.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression

AS_OF_DATE = date(2026, 1, 1)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def compute_customer_features_naive_train(
    signup_date: date, order_dates: list[date], order_amounts: list[float], as_of_date: date
) -> dict:
    days_since_signup = (as_of_date - signup_date).days
    is_weekend_signup = signup_date.weekday() >= 5
    orders_last_30d = sum(1 for d in order_dates if 0 <= (as_of_date - d).days < 30)
    avg_order_value = round(sum(order_amounts) / len(order_amounts), 2) if order_amounts else 0.0
    return {
        "days_since_signup": days_since_signup,
        "is_weekend_signup": is_weekend_signup,
        "orders_last_30d": orders_last_30d,
        "avg_order_value": avg_order_value,
    }


def build_feature_matrix_naive_train(
    customers: pd.DataFrame, orders: pd.DataFrame, as_of_date: date
) -> pd.DataFrame:
    orders_by_customer = {cid: g for cid, g in orders.groupby("customer_id")}
    rows = []
    for _, customer in customers.iterrows():
        customer_id = customer["customer_id"]
        signup = date.fromisoformat(customer["signup_date"])
        group = orders_by_customer.get(customer_id)
        if group is None:
            order_dates, order_amounts = [], []
        else:
            order_dates = [date.fromisoformat(d) for d in group["order_date"]]
            order_amounts = list(group["amount"])
        features = compute_customer_features_naive_train(
            signup, order_dates, order_amounts, as_of_date
        )
        features["customer_id"] = customer_id
        rows.append(features)
    cols = [
        "customer_id",
        "days_since_signup",
        "is_weekend_signup",
        "orders_last_30d",
        "avg_order_value",
    ]
    return pd.DataFrame(rows)[cols].sort_values("customer_id").reset_index(drop=True)


def main() -> None:
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    orders = pd.read_csv(DATA_DIR / "orders.csv")

    features = build_feature_matrix_naive_train(customers, orders, AS_OF_DATE)
    features.to_csv(DATA_DIR / "features_train_naive.csv", index=False)

    X = features[["days_since_signup", "is_weekend_signup", "orders_last_30d", "avg_order_value"]]
    y = customers.sort_values("customer_id")["high_value"].reset_index(drop=True)
    model = LogisticRegression(max_iter=1000).fit(X, y)
    print(f"Trained on {len(X)} customers. Train accuracy: {model.score(X, y):.3f}")
    print(f"Wrote naive training-time features to {DATA_DIR / 'features_train_naive.csv'}")


if __name__ == "__main__":
    main()
