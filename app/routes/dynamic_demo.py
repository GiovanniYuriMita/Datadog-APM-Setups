"""
Dynamic Instrumentation demo endpoints.
"""

import logging
from flask import Blueprint, jsonify, request

import demo_dynamic

logger = logging.getLogger(__name__)

dynamic_demo_bp = Blueprint("dynamic_demo", __name__)


@dynamic_demo_bp.route("/api/dynamic/process-batch", methods=["POST"])
def process_batch_demo():
    payload = request.get_json() or {}
    batch_id = payload.get("batch_id", "batch-demo-001")
    records = payload.get("records") or []
    tax_rate = float(payload.get("tax_rate", 0.1))
    discount_threshold = float(payload.get("discount_threshold", 800))

    result = demo_dynamic.process_batch(
        batch_id=batch_id,
        records=records,
        tax_rate=tax_rate,
        discount_threshold=discount_threshold,
    )
    logger.info(
        "Dynamic demo batch processed",
        extra={
            "operation": "dynamic.process_batch",
            "batch_id": batch_id,
            "record_count": len(records),
            "final_amount": result["totals"]["final_amount"],
        },
    )
    return jsonify(result), 200


@dynamic_demo_bp.route("/api/dynamic/slow-checkout", methods=["POST"])
def slow_checkout_demo():
    payload = request.get_json() or {}
    user_id = str(payload.get("user_id", "demo-user"))
    records = payload.get("records") or [
        {"item_id": "prod_001", "unit_price": 999.99, "quantity": 1},
        {"item_id": "prod_002", "unit_price": 29.99, "quantity": 2},
    ]
    delay_seconds = int(payload.get("delay_seconds", 10))

    result = demo_dynamic.investigate_slow_checkout(
        user_id=user_id,
        records=records,
        total_delay_seconds=delay_seconds,
    )
    return jsonify(result), 200


@dynamic_demo_bp.route("/api/dynamic/hidden-error", methods=["POST"])
def hidden_error_demo():
    """
    Intentionally returns HTTP 200 even when internal processing fails.

    This simulates production bugs where frontend reports failure, but backend
    traces may look successful unless deeper instrumentation is added.
    """
    payload = request.get_json() or {}
    try:
        result = demo_dynamic.hidden_exception_path(payload)
        return jsonify({"status": "ok", "result": result}), 200
    except Exception as exc:
        # Purposely wrong behavior for demo: swallow exception and return 200.
        logger.warning(
            "Hidden exception swallowed in dynamic demo",
            extra={
                "operation": "dynamic.hidden_error",
                "error_type": type(exc).__name__,
            },
        )
        return jsonify(
            {
                "status": "ok",
                "message": "Processed with fallback",
                "fallback_used": True,
            }
        ), 200
