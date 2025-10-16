"""
Transaction Management Endpoints

Este é o arquivo MAIS IMPORTANTE para demonstração de logging!

Demonstra:
- ✅ Logging de operações críticas de negócio
- ✅ Transaction stages (auditoria completa)
- ✅ Validações com logs contextuais
- ✅ Error handling detalhado
- ✅ Nunca logar dados sensíveis (números de cartão, etc)
"""

import logging
import random
import time
from datetime import datetime
from flask import Blueprint, request, jsonify
from ddtrace import tracer
from utils import (
    hash_user_identifier,
    extract_device_info,
    extract_geo_info,
    extract_session_info,
    calculate_risk_score,
    extract_payment_context,
    get_inventory_context,
    get_business_metrics,
    get_performance_context
)
from models.data import MOCK_USERS, MOCK_PRODUCTS, TRANSACTIONS

logger = logging.getLogger(__name__)

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('/api/transaction', methods=['POST'])
def create_transaction():
    """
    Cria uma transação financeira.
    
    ⭐ ARQUIVO CHAVE PARA DEMONSTRAÇÃO ⭐
    
    Best Practices Demonstradas:
    
    1. TRANSACTION STAGES
       - Logue cada etapa crítica da transação
       - Facilita identificar onde falhou
    
    2. VALIDATION LOGGING
       - Logue falhas de validação com razão específica
       - Use WARNING para erros esperados (user input ruim)
    
    3. BUSINESS CONTEXT
       - Inclua metadata relevante: valores, quantidades, IDs
       - NUNCA logue números de cartão ou dados sensíveis
    
    4. ERROR HANDLING
       - Diferencie erros esperados vs inesperados
       - Use exc_info=True para erros inesperados
    
    5. AUDIT TRAIL
       - Transações são operações críticas - logue tudo
       - Mas proteja PII (use hashing)
    """
    
    with tracer.trace("transaction.create", service="chofs-api") as span:
        start_time = time.time()
        
        try:
            data = request.get_json()
            
            # Extrair contexto enriquecido da requisição
            device_info = extract_device_info()
            geo_info = extract_geo_info()
            session_info = extract_session_info()
            
            # ========================================
            # ETAPA 1: VALIDAÇÃO DE ENTRADA
            # ========================================
            
            required_fields = ['user_id', 'product_id', 'quantity']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                # LOG: Validação falhou - campos faltando
                # ✅ Use WARNING (não ERROR) - é erro de input do usuário
                logger.warning(
                    "Transaction validation failed - missing required fields",
                    extra={
                        'operation': 'transaction.create',
                        'validation_error': 'missing_fields',
                        'missing_fields': missing_fields,
                        'transaction_stage': 'validation'
                    }
                )
                return jsonify({"error": f"Missing required fields: {missing_fields}"}), 400
            
            user_id = data['user_id']
            product_id = data['product_id']
            quantity = data.get('quantity', 1)
            
            # Adiciona tags importantes ao span do APM
            span.set_tag("user_id_hash", hash_user_identifier(user_id))
            span.set_tag("product_id", product_id)
            span.set_tag("quantity", quantity)
            
            # ========================================
            # ETAPA 2: TRANSAÇÃO INICIADA
            # ========================================
            
            # LOG: Transação iniciada com contexto RICO
            # ✅ BOM: Primeira entrada no audit trail com contexto completo
            log_context = {
                'operation': 'transaction.create',
                'user_id_hash': hash_user_identifier(user_id),
                'product_id': product_id,
                'quantity': quantity,
                'transaction_stage': 'initiated',
                **device_info,  # Device, OS, Browser
                **geo_info,     # País, Cidade, Região
                **session_info  # Session ID, Referrer
            }
            
            logger.info(
                "Transaction initiated",
                extra=log_context
            )
            
            # ========================================
            # ETAPA 3: VALIDAÇÃO DE USUÁRIO
            # ========================================
            
            if user_id not in MOCK_USERS:
                # LOG: Usuário não encontrado
                logger.warning(
                    "Transaction failed - user not found",
                    extra={
                        'operation': 'transaction.create',
                        'user_id_hash': hash_user_identifier(user_id),
                        'failure_reason': 'user_not_found',
                        'transaction_stage': 'user_validation'
                    }
                )
                return jsonify({"error": "User not found"}), 404
            
            # ========================================
            # ETAPA 4: VALIDAÇÃO DE PRODUTO
            # ========================================
            
            if product_id not in MOCK_PRODUCTS:
                # LOG: Produto não encontrado
                logger.warning(
                    "Transaction failed - product not found",
                    extra={
                        'operation': 'transaction.create',
                        'user_id_hash': hash_user_identifier(user_id),
                        'product_id': product_id,
                        'failure_reason': 'product_not_found',
                        'transaction_stage': 'product_validation'
                    }
                )
                return jsonify({"error": "Product not found"}), 404
            
            product = MOCK_PRODUCTS[product_id]
            user = MOCK_USERS[user_id]
            total_amount = product['price'] * quantity
            
            # Calcular contexto adicional
            risk_context = calculate_risk_score(user, product, quantity)
            payment_context = extract_payment_context(user, total_amount)
            business_metrics = get_business_metrics(user)
            inventory_context = get_inventory_context(product, quantity)
            
            # ========================================
            # ETAPA 5: VERIFICAÇÃO DE ESTOQUE
            # ========================================
            
            if product['stock'] < quantity:
                # LOG com contexto de inventário COMPLETO
                logger.warning(
                    "Transaction failed - insufficient stock",
                    extra={
                        'operation': 'transaction.create',
                        'user_id_hash': hash_user_identifier(user_id),
                        'product_id': product_id,
                        'requested_quantity': quantity,
                        'available_stock': product['stock'],
                        'failure_reason': 'insufficient_stock',
                        'transaction_stage': 'inventory_check',
                        **inventory_context,  # SKU, vendor, threshold
                        **business_metrics,   # Account type, LTV
                        **geo_info,           # Localização do usuário
                        **device_info         # Device info
                    }
                )
                return jsonify({"error": "Insufficient stock"}), 400
            
            # ========================================
            # ETAPA 6: VERIFICAÇÃO DE SALDO
            # ========================================
            
            if user['balance'] < total_amount:
                # LOG com contexto de pagamento e usuário
                logger.warning(
                    "Transaction failed - insufficient funds",
                    extra={
                        'operation': 'transaction.create',
                        'user_id_hash': hash_user_identifier(user_id),
                        'product_id': product_id,
                        'total_amount': total_amount,
                        'failure_reason': 'insufficient_funds',
                        'transaction_stage': 'payment_validation',
                        **payment_context,   # Método, moeda, parcelamento
                        **business_metrics,  # Account type, LTV, VIP status
                        **risk_context,      # Risk score e level
                        **geo_info,          # Localização
                        **device_info        # Device info
                    }
                )
                return jsonify({"error": "Insufficient funds"}), 400
            
            # ========================================
            # ETAPA 7: PROCESSAMENTO (com falha simulada)
            # ========================================
            
            # Simula falha aleatória (10%) para demonstrar error logging
            if random.random() < 0.1:
                raise Exception("Simulated payment gateway timeout")
            
            # Processa transação
            transaction_id = f"txn_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
            
            user['balance'] -= total_amount
            product['stock'] -= quantity
            
            transaction = {
                'transaction_id': transaction_id,
                'user_id_hash': hash_user_identifier(user_id),  # Hash, não user_id real!
                'product_id': product_id,
                'quantity': quantity,
                'total_amount': total_amount,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'completed'
            }
            TRANSACTIONS.append(transaction)
            
            # ========================================
            # ETAPA 8: TRANSAÇÃO COMPLETADA
            # ========================================
            
            # Calcular métricas de performance
            performance_context = get_performance_context(start_time)
            
            # LOG: Transação completada com CONTEXTO RICO
            # ⭐ Este é o log mais importante - tem TODO o contexto!
            logger.info(
                "Transaction completed successfully",
                extra={
                    'operation': 'transaction.create',
                    'transaction_id': transaction_id,
                    'user_id_hash': hash_user_identifier(user_id),
                    'product_id': product_id,
                    'product_name': product['name'],
                    'quantity': quantity,
                    'total_amount': total_amount,
                    'remaining_balance': user['balance'],
                    'remaining_stock': product['stock'],
                    'transaction_stage': 'completed',
                    'status': 'success',
                    # Contexto de pagamento
                    **payment_context,
                    # Contexto de inventário
                    **inventory_context,
                    # Métricas de negócio
                    **business_metrics,
                    # Risk analysis
                    **risk_context,
                    # Geolocalização
                    **geo_info,
                    # Device info
                    **device_info,
                    # Session tracking
                    **session_info,
                    # Performance
                    **performance_context
                }
            )
            
            return jsonify({
                'transaction_id': transaction_id,
                'status': 'completed',
                'total_amount': total_amount,
                'remaining_balance': user['balance']
            }), 201
            
        except Exception as e:
            # LOG: Erro crítico durante processamento
            # ✅ BOM: Use padrões Datadog (error.type, error.message, error.stack)
            import traceback
            logger.error(
                f"Transaction processing failed with error: {str(e)}",
                extra={
                    'operation': 'transaction.create',
                    'user_id_hash': hash_user_identifier(data.get('user_id', 'unknown')),
                    'product_id': data.get('product_id', 'unknown'),
                    'error.type': type(e).__name__,
                    'error.message': str(e),
                    'error.stack': traceback.format_exc(),
                    'transaction_stage': 'processing',
                    'status': 'error'
                }
            )
            return jsonify({"error": "Transaction processing failed"}), 500

