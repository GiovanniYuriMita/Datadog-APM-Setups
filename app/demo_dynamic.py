"""
Helpers for Datadog Dynamic Instrumentation workshop scenarios.

These functions are intentionally crafted to be good probe targets:
- `process_batch` exposes useful inputs/outputs for snapshot logs
- slow functions emulate latency investigations
- buggy functions hide exceptions and create "mystery" behavior
"""

import hashlib
import random
import time
from typing import Any


def process_batch(
    batch_id: str,
    records: list[dict[str, Any]],
    tax_rate: float = 0.1,
    discount_threshold: float = 800.0
) -> dict[str, Any]:
    """
    Process an order-like batch and return summarized output.
    """
    started_at = time.time()
    normalized_records = []
    total_before_tax = 0.0
    errors = []

    for record in records:
        item_id = str(record.get("item_id", "unknown"))
        unit_price = float(record.get("unit_price", 0.0))
        quantity = int(record.get("quantity", 1))
        if quantity <= 0:
            errors.append({"item_id": item_id, "reason": "invalid_quantity"})
            continue

        subtotal = unit_price * quantity
        total_before_tax += subtotal
        normalized_records.append(
            {
                "item_id": item_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "subtotal": round(subtotal, 2),
            }
        )

    discount = 0.0
    if total_before_tax > discount_threshold:
        discount = round(total_before_tax * 0.07, 2)

    taxable_amount = max(total_before_tax - discount, 0.0)
    tax_amount = round(taxable_amount * tax_rate, 2)
    final_amount = round(taxable_amount + tax_amount, 2)
    elapsed_ms = int((time.time() - started_at) * 1000)

    return {
        "batch_id": batch_id,
        "record_count": len(records),
        "valid_count": len(normalized_records),
        "errors": errors,
        "input_records": normalized_records,
        "totals": {
            "before_tax": round(total_before_tax, 2),
            "discount": discount,
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "final_amount": final_amount,
        },
        "elapsed_ms": elapsed_ms,
    }


def slow_inventory_dependency(
    product_ids: list[str],
    per_item_delay_ms: int = 1200
) -> dict[str, Any]:
    """
    Simulates a slow dependency call by sleeping per item.
    """
    checks = []
    for product_id in product_ids:
        time.sleep(max(per_item_delay_ms, 0) / 1000.0)
        checks.append(
            {
                "product_id": product_id,
                "available": random.choice([True, True, True, False]),
            }
        )
    return {"checks": checks, "dependency": "inventory_provider_v2"}


def investigate_slow_checkout(
    user_id: str,
    records: list[dict[str, Any]],
    total_delay_seconds: int = 10
) -> dict[str, Any]:
    """
    Purposefully slow workflow (~10s) for APM investigation demos.
    """
    total_delay_seconds = max(total_delay_seconds, 0)
    # Split delay so traces can show different "stages" during analysis.
    initial_wait = min(2, total_delay_seconds)
    dependency_wait = max(total_delay_seconds - initial_wait, 0)

    time.sleep(initial_wait)
    pricing_result = process_batch(
        batch_id=f"batch-{int(time.time())}",
        records=records,
        tax_rate=0.12,
        discount_threshold=1200.0,
    )

    dependency_result = slow_inventory_dependency(
        product_ids=[str(item.get("item_id", "unknown")) for item in records],
        per_item_delay_ms=int((dependency_wait * 1000) / max(len(records), 1)),
    )

    return {
        "user_id_hash": hashlib.sha256(user_id.encode()).hexdigest()[:12],
        "slowdown_reason": "external_inventory_dependency",
        "pricing_result": pricing_result,
        "dependency_result": dependency_result,
        "delay_budget_seconds": total_delay_seconds,
    }


def hidden_exception_path(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Raises exceptions for malformed payloads.
    """
    transaction_id = payload.get("transaction_id")
    retries = int(payload.get("retries", 1))
    if not transaction_id:
        raise KeyError("transaction_id is required")
    if retries < 0:
        raise ValueError("retries cannot be negative")

    factor = float(payload.get("factor", 1))
    baseline = float(payload.get("baseline", 100))
    return {
        "transaction_id": transaction_id,
        "risk_score": round((baseline * factor) / retries, 2),
        "retries": retries,
    }
