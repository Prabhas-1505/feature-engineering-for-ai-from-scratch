"""The fix, serving side: build features through the same `feature_lib`.

Run after `train.py`. Recomputes features independently (simulating a
serving process that never saw the training run) and diffs against what
training produced. With a single shared library, there's nothing left to
disagree about.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
from feature_lib import build_feature_matrix
from naive_serve import diff_report

AS_OF_DATE = date(2026, 1, 1)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    orders = pd.read_csv(DATA_DIR / "orders.csv")

    train_path = DATA_DIR / "features_train_fixed.csv"
    if not train_path.exists():
        raise SystemExit("Run train.py first — it writes the file this script compares against.")
    train_features = pd.read_csv(train_path)

    serve_features = build_feature_matrix(customers, orders, AS_OF_DATE)

    report = diff_report(train_features, serve_features)
    if report.empty:
        print(
            "No mismatches: train.py and serve.py agree on every feature, "
            "for every customer, because both call feature_lib.build_feature_matrix."
        )
    else:
        print(f"Unexpected skew ({len(report)} mismatches) — feature_lib should be deterministic:")
        print(report.to_string(index=False))


if __name__ == "__main__":
    main()
