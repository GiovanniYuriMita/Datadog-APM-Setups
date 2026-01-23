"""
Error Simulation Endpoints

Demonstra diferentes tipos de error handling e logging.

⭐ IMPORTANTE PARA DEMO ⭐
Este endpoint simula diferentes tipos de erros para demonstrar
como fazer logging apropriado em cada caso.
"""

import logging
import time
from flask import Blueprint, request, g
# Não precisamos mais de decorators - APM já captura requests

logger = logging.getLogger(__name__)

errors_bp = Blueprint('errors', __name__)


@errors_bp.route('/api/error/simulate', methods=['GET'])
def simulate_error():
    """
    Simula diferentes tipos de erros para demonstração.
    
    Best Practices Demonstradas:
    
    1. CATEGORIZAÇÃO DE ERROS
       - Diferencie erros de negócio vs erros técnicos
       - Use níveis apropriados (WARNING vs ERROR)
    
    2. ERROR CONTEXT
       - Sempre inclua contexto: o que estava fazendo quando falhou?
       - Inclua error_type para facilitar filtros no Datadog
    
    3. STACK TRACES
       - Use exc_info=True para erros inesperados
       - Não use para erros esperados (validação)
    
    Tipos de erro disponíveis:
    - division: Erro aritmético (ZeroDivisionError)
    - validation: Erro de validação (ValueError)
    - timeout: Simulação de timeout
    - generic: Erro genérico
    """
    
    error_type = request.args.get('type', 'generic')
    # Variáveis locais para Exception Replay
    user_id = request.args.get('user_id', 'demo-user')
    amount_raw = request.args.get('amount', '0')
    currency = request.args.get('currency', 'BRL')
    request_id = request.headers.get('X-Request-Id', 'req-demo')
    payment_ref = f"{user_id}:{currency}:{amount_raw}"
    
    g.error_context = {
        "request_id": request_id,
        "payment_ref": payment_ref
    }

    # LOG: Início da simulação
    logger.info(
        f"Simulating error of type: {error_type}",
        extra={
            'operation': 'error.simulation',
            'error.type': error_type,
            'is_test': True  # Flag para identificar que é teste
        }
    )

    # Simula diferentes tipos de erros
    if error_type == 'division':
        divisor = int(request.args.get('divisor', '0'))
        dividend = int(request.args.get('dividend', '1'))
        dividend / divisor  # ZeroDivisionError
        return ""

    if error_type == 'timeout':
        timeout_seconds = int(request.args.get('timeout', '30'))
        time.sleep(timeout_seconds)  # Simula timeout
        raise TimeoutError("Simulated request timeout")

    if error_type == 'validation':
        amount = float(amount_raw)
        if amount <= 0:
            raise ValueError("Invalid amount: must be greater than zero")
        raise ValueError("Invalid input parameters provided")

    raise Exception(f"Simulated {error_type} error for testing")

