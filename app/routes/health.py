"""
Health Check Endpoint

Demonstra logging apropriado para health checks.

Best Practice: Use DEBUG level para health checks evitar poluição de logs.
"""

import logging
from datetime import datetime
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Best Practice:
    - Use nível DEBUG para health checks (muito frequentes)
    - Em produção, considere não logar health checks
    - Kubernetes/Docker fazem health checks a cada poucos segundos
    
    ❌ RUIM: logger.info("Health check") - Polui logs
    ✅ BOM: logger.debug("Health check") - Só aparece quando necessário
    """
    logger.debug("Health check requested")  # DEBUG, não INFO!
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

