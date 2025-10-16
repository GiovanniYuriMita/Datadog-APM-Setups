"""
Product Management Endpoints

Demonstra logging simples para operações de leitura.
"""

import logging
from flask import Blueprint, jsonify
from ddtrace import tracer
# Não precisamos mais de decorators - APM já captura requests
from models.data import MOCK_PRODUCTS

logger = logging.getLogger(__name__)

products_bp = Blueprint('products', __name__)


@products_bp.route('/api/products', methods=['GET'])
def list_products():
    """
    Lista todos os produtos disponíveis.
    
    Best Practices:
    - Log operações de leitura com contexto relevante
    - Inclua contadores e métricas úteis
    - Use custom spans para rastreamento no APM
    """
    
    with tracer.trace("product.list", service="chofs-api") as span:
        # Adiciona métrica ao span
        span.set_tag("product_count", len(MOCK_PRODUCTS))
        
        # LOG: Operação simples mas com contexto
        logger.info(
            "Products list requested",
            extra={
                'operation': 'product.list',
                'product_count': len(MOCK_PRODUCTS)
            }
        )
        
        return jsonify({
            'products': [
                {
                    'product_id': pid,
                    'name': product['name'],
                    'price': product['price'],
                    'stock': product['stock']
                }
                for pid, product in MOCK_PRODUCTS.items()
            ]
        }), 200

