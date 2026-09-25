"""Regression tests for Lesson 00: the train/serve skew bug, and its fix."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent / "code"))

from feature_lib import avg_order_value, build_feature_matrix, orders_last_30d  # noqa: E402
from generate_data import make_customers_and_orders  # noqa: E402
from naive_serve import build_feature_matrix_naive_serve, diff_report  # noqa: E402
from naive_train import build_feature_matrix_naive_train  # noqa: E402

AS_OF_DATE = date(2026, 1, 1)


def _fixture_data():
    rng = np.random.default_rng(42)
    return make_customers_and_orders(rng, AS_OF_DATE)


def test_orders_last_30d_boundary_is_inclusive():
    order_exactly_30_days_ago = AS_OF_DATE.fromordinal(AS_OF_DATE.toordinal() - 30)
    assert orders_last_30d([order_exactly_30_days_ago], AS_OF_DATE) == 1


def test_avg_order_value_of_no_orders_is_zero_not_nan():
    assert avg_order_value([]) == 0.0


def test_feature_lib_is_deterministic():
    customers, orders = _fixture_data()
    first = build_feature_matrix(customers, orders, AS_OF_DATE)
    second = build_feature_matrix(customers, orders, AS_OF_DATE)
    assert first.equals(second)


def test_naive_train_and_naive_serve_disagree():
    """Proves the bug is real: two independent naive implementations,
    given the same raw data, compute different feature values."""
    customers, orders = _fixture_data()
    train_features = build_feature_matrix_naive_train(customers, orders, AS_OF_DATE)
    serve_features = build_feature_matrix_naive_serve(customers, orders, AS_OF_DATE)

    report = diff_report(train_features, serve_features)
    assert not report.empty, "expected the naive implementations to disagree"

    mismatched_features = set(report["feature"])
    assert "orders_last_30d" in mismatched_features, "window boundary bug should surface"
    assert "avg_order_value" in mismatched_features, "null-handling bug should surface"

    customer_1_row = report[(report.customer_id == 1) & (report.feature == "orders_last_30d")]
    assert not customer_1_row.empty, "customer 1's boundary order should trigger a mismatch"

    customer_2_row = report[(report.customer_id == 2) & (report.feature == "avg_order_value")]
    assert not customer_2_row.empty, "customer 2's zero orders should trigger a mismatch"


def test_shared_feature_lib_eliminates_skew():
    """The fix: both `train.py` and `serve.py` call `build_feature_matrix`.
    Rebuilding it independently for the same raw data must match exactly."""
    customers, orders = _fixture_data()
    train_features = build_feature_matrix(customers, orders, AS_OF_DATE)
    serve_features = build_feature_matrix(customers, orders, AS_OF_DATE)

    report = diff_report(train_features, serve_features)
    assert report.empty, f"expected zero skew, found:\n{report}"
