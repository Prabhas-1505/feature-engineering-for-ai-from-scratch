"""The naive implementation, serving side.

Written independently of `naive_train.py` — by a different engineer, weeks
later, working from a description of the features rather than the training
code itself. It "looks" like the same four features. It isn't:

  - `orders_last_30d` uses an *inclusive* window here: an order exactly 30
    days before `as_of_date` DOES count. `naive_train.py` used a strict
    window. Off-by-one.
  - `avg_order_value` for a customer with zero orders is left as NaN here —
    there's no sklearn matrix forcing a fill at serving time, so nobody
    noticed it needed one. `naive_train.py` filled it to 0.0.

Run this after `naive_train.py` (it reads the CSV that script wrote) to see
the mismatch, computed and printed, not asserted.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

AS_OF_DATE = date(2026, 1, 1)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def compute_customer_features_naive_serve(
    signup_date: date, order_dates: list[date], order_amounts: list[float], as_of_date: date
) -> dict:
    days_since_signup = (as_of_date - signup_date).days
    is_weekend_signup = signup_date.weekday() >= 5
    orders_last_30d = sum(1 for d in order_dates if 0 <= (as_of_date - d).days <= 30)
    avg_order_value = (
        round(sum(order_amounts) / len(order_amounts), 2) if order_amounts else float("nan")
    )
    return {
        "days_since_signup": days_since_signup,
        "is_weekend_signup": is_weekend_signup,
        "orders_last_30d": orders_last_30d,
        "avg_order_value": avg_order_value,
    }


def build_feature_matrix_naive_serve(
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
        features = compute_customer_features_naive_serve(
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


def diff_report(train_features: pd.DataFrame, serve_features: pd.DataFrame) -> pd.DataFrame:
    merged = train_features.merge(serve_features, on="customer_id", suffixes=("_train", "_serve"))
    mismatches = []
    for col in ["days_since_signup", "is_weekend_signup", "orders_last_30d", "avg_order_value"]:
        train_col, serve_col = merged[f"{col}_train"], merged[f"{col}_serve"]
        differs = ~((train_col == serve_col) | (train_col.isna() & serve_col.isna()))
        for _, row in merged[differs].iterrows():
            mismatches.append(
                {
                    "customer_id": row["customer_id"],
                    "feature": col,
                    "train_value": row[f"{col}_train"],
                    "serve_value": row[f"{col}_serve"],
                }
            )
    return pd.DataFrame(mismatches)


def main() -> None:
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    orders = pd.read_csv(DATA_DIR / "orders.csv")

    train_path = DATA_DIR / "features_train_naive.csv"
    if not train_path.exists():
        raise SystemExit(
            "Run naive_train.py first — it writes the file this script compares against."
        )
    train_features = pd.read_csv(train_path)

    serve_features = build_feature_matrix_naive_serve(customers, orders, AS_OF_DATE)

    report = diff_report(train_features, serve_features)
    if report.empty:
        print("No mismatches found (unexpected for the naive implementation).")
    else:
        print(
            f"TRAIN/SERVE SKEW: {len(report)} feature values disagree between "
            f"naive_train.py and naive_serve.py for the same raw data:\n"
        )
        print(report.to_string(index=False))


if __name__ == "__main__":
    main()
