"""
Home/Index Endpoint

Endpoint raiz com documentação da API.
"""

from flask import Blueprint, jsonify
from models.data import MOCK_USERS, MOCK_PRODUCTS

home_bp = Blueprint('home', __name__)


@home_bp.route('/', methods=['GET'])
def index():
    """
    Endpoint de boas-vindas com documentação da API.
    
    Best Practice: Forneça documentação fácil de acessar.
    """
    return jsonify({
        "message": "Datadog APM Logging Best Practices Demo API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health - Health check",
            "user": "GET /api/user/<user_id> - Get user profile",
            "products": "GET /api/products - List all products",
            "transaction": "POST /api/transaction - Create transaction",
            "analytics": "GET /api/analytics/transactions - Get transaction analytics",
            "error": "GET /api/error/simulate?type=<error_type> - Simulate errors",
            "dynamic_process_batch": "POST /api/dynamic/process-batch - Batch demo for dynamic instrumentation",
            "dynamic_slow_checkout": "POST /api/dynamic/slow-checkout - Slow endpoint (~10s) for investigation",
            "dynamic_hidden_error": "POST /api/dynamic/hidden-error - Swallowed exception returning 200"
        },
        "test_data": {
            "available_users": list(MOCK_USERS.keys()),
            "available_products": list(MOCK_PRODUCTS.keys())
        }
    }), 200

