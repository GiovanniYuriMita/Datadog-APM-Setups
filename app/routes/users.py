"""
User Management Endpoints

Demonstra:
- Proteção de PII (mascaramento de email)
- Hashing de user IDs
- Logging de operações com contexto
- Uso de custom spans do Datadog
"""

import logging
import time
from flask import Blueprint, jsonify
from ddtrace import tracer
from utils import (
    hash_user_identifier,
    mask_sensitive_data,
    extract_device_info,
    extract_geo_info,
    extract_session_info,
    get_business_metrics,
    get_performance_context
)
from models.data import MOCK_USERS

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__)


@users_bp.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    Busca informações de um usuário.
    
    Best Practices Demonstradas:
    1. ✅ Hash de user_id para não expor PII em logs
    2. ✅ Mascaramento de email na resposta (para demo)
    3. ✅ Logging estruturado com 'extra={}'
    4. ✅ Custom span no Datadog APM
    5. ✅ Log de diferentes cenários (sucesso, não encontrado, erro)
    """
    
    # Cria custom span para rastreamento no Datadog APM
    with tracer.trace("user.fetch", service="chofs-api") as span:
        start_time = time.time()
        
        # Adiciona tag ao span (NÃO use user_id real, use hash!)
        span.set_tag("user_id_hash", hash_user_identifier(user_id))
        
        # Extrair contexto enriquecido
        device_info = extract_device_info()
        geo_info = extract_geo_info()
        session_info = extract_session_info()
        
        # LOG 1: Operação iniciada COM CONTEXTO RICO
        # ✅ BOM: Hash + device + geo + session
        logger.info(
            "Fetching user profile",
            extra={
                'operation': 'user.fetch',
                'user_id_hash': hash_user_identifier(user_id),
                'requested_fields': 'all',
                **device_info,
                **geo_info,
                **session_info
            }
        )
        
        try:
            # Validação: usuário existe?
            if user_id not in MOCK_USERS:
                # LOG 2: Usuário não encontrado
                # ✅ BOM: Use WARNING para casos esperados mas não ideais
                logger.warning(
                    "User not found",
                    extra={
                        'operation': 'user.fetch',
                        'user_id_hash': hash_user_identifier(user_id),
                        'reason': 'user_not_in_database'
                    }
                )
                return jsonify({"error": "User not found"}), 404
            
            user = MOCK_USERS[user_id].copy()
            
            # Extrair métricas de negócio
            business_metrics = get_business_metrics(user)
            performance_context = get_performance_context(start_time)
            
            # LOG 3: Sucesso COM CONTEXTO RICO
            # ✅ BOM: Log completo (sem PII) para analytics
            logger.info(
                "User profile fetched successfully",
                extra={
                    'operation': 'user.fetch',
                    'user_id_hash': hash_user_identifier(user_id),
                    'has_balance': user['balance'] > 0,  # Boolean, não valor
                    **business_metrics,      # Account type, LTV, VIP
                    **geo_info,              # País, cidade
                    **device_info,           # Device, OS, browser
                    **session_info,          # Session tracking
                    **performance_context    # Duração da query
                }
            )
            
            # ⚠️ IMPORTANTE: Nunca logue o email completo!
            # Para esta demo, mascaramos na resposta também
            return jsonify({
                "user_id": user_id,
                "name": user['name'],
                "email": mask_sensitive_data(user['email'], 3),
                "balance": user['balance']
            }), 200
            
        except Exception as e:
            # LOG 4: Erro inesperado
            # ✅ BOM: Use padrões Datadog (error.type, error.message, error.stack)
            import traceback
            logger.error(
                f"Unexpected error fetching user profile: {str(e)}",
                extra={
                    'operation': 'user.fetch',
                    'user_id_hash': hash_user_identifier(user_id),
                    'error.type': type(e).__name__,
                    'error.message': str(e),
                    'error.stack': traceback.format_exc()
                }
            )
            return jsonify({"error": "Internal server error"}), 500

