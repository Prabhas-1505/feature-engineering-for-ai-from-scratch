"""The fix, training side: build features through `feature_lib`, nothing inline."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
from feature_lib import build_feature_matrix
from sklearn.linear_model import LogisticRegression

AS_OF_DATE = date(2026, 1, 1)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    orders = pd.read_csv(DATA_DIR / "orders.csv")

    features = build_feature_matrix(customers, orders, AS_OF_DATE)
    features.to_csv(DATA_DIR / "features_train_fixed.csv", index=False)

    X = features[["days_since_signup", "is_weekend_signup", "orders_last_30d", "avg_order_value"]]
    y = customers.sort_values("customer_id")["high_value"].reset_index(drop=True)
    model = LogisticRegression(max_iter=1000).fit(X, y)
    print(f"Trained on {len(X)} customers. Train accuracy: {model.score(X, y):.3f}")
    print(f"Wrote training-time features to {DATA_DIR / 'features_train_fixed.csv'}")


if __name__ == "__main__":
    main()
