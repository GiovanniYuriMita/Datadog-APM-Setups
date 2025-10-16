"""
Analytics Endpoints

Demonstra logging para operações de analytics/reporting.
"""

import logging
from flask import Blueprint, jsonify
from ddtrace import tracer
# Não precisamos mais de decorators - APM já captura requests
from models.data import TRANSACTIONS

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/api/analytics/transactions', methods=['GET'])
def get_transaction_analytics():
    """
    Retorna analytics de transações.
    
    Best Practices:
    - Logue queries de analytics para entender uso do sistema
    - Inclua parâmetros de query e resultados (contadores)
    - Use spans para rastrear performance
    """
    
    with tracer.trace("analytics.transactions", service="chofs-api") as span:
        
        # Calcula métricas
        total_transactions = len(TRANSACTIONS)
        total_revenue = sum(t['total_amount'] for t in TRANSACTIONS)
        
        # Adiciona métricas ao span
        span.set_tag("total_transactions", total_transactions)
        span.set_tag("total_revenue", total_revenue)
        
        # LOG: Query de analytics executada
        # ✅ BOM: Inclui resultados agregados
        logger.info(
            "Transaction analytics computed",
            extra={
                'operation': 'analytics.transactions',
                'total_transactions': total_transactions,
                'total_revenue': round(total_revenue, 2),
                'time_range': 'all_time'
            }
        )
        
        return jsonify({
            'total_transactions': total_transactions,
            'total_revenue': round(total_revenue, 2),
            'transactions': TRANSACTIONS[-10:]  # Últimas 10 transações
        }), 200

