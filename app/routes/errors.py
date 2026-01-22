"""
Error Simulation Endpoints

Demonstra diferentes tipos de error handling e logging.

⭐ IMPORTANTE PARA DEMO ⭐
Este endpoint simula diferentes tipos de erros para demonstrar
como fazer logging apropriado em cada caso.
"""

import logging
import time
import traceback
from flask import Blueprint, request, jsonify
from ddtrace import tracer
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
    
    def _attach_error(span, exc, stack):
        if not span:
            return
        span.set_tag("error", True)
        span.set_tag("error.type", type(exc).__name__)
        span.set_tag("error.message", str(exc))
        span.set_tag("error.stack", stack)
        span.set_exc_info(type(exc), exc, exc.__traceback__)

    with tracer.trace("error.simulation", service="chofs-api") as span:
        span.set_tag("error.type", error_type)
        
        # LOG: Início da simulação
        logger.info(
            f"Simulating error of type: {error_type}",
            extra={
                'operation': 'error.simulation',
                'error.type': error_type,
                'is_test': True  # Flag para identificar que é teste
            }
        )
        
        try:
            # Simula diferentes tipos de erros
            if error_type == 'division':
                result = 1 / 0  # ZeroDivisionError
                
            elif error_type == 'timeout':
                time.sleep(30)  # Simula timeout
                
            elif error_type == 'validation':
                raise ValueError("Invalid input parameters provided")
                
            else:
                raise Exception(f"Simulated {error_type} error for testing")
        
        # ========================================
        # EXEMPLO 1: ERRO ARITMÉTICO
        # ========================================
        except ZeroDivisionError as e:
            # LOG: Erro específico e esperado
            # ✅ BOM: Use padrões Datadog (error.type, error.message, error.stack)
            error_stack = traceback.format_exc()
            _attach_error(span, e, error_stack)
            _attach_error(tracer.current_root_span(), e, error_stack)
            logger.error(
                "Division by zero error occurred",
                extra={
                    'operation': 'error.simulation',
                    'error.type': 'ZeroDivisionError',
                    'error.message': str(e),
                    'error.stack': error_stack,
                    'error_category': 'arithmetic_error',
                    'is_test': True
                }
            )
            return jsonify({"error": "Division by zero"}), 400
        
        # ========================================
        # EXEMPLO 2: ERRO DE VALIDAÇÃO
        # ========================================
        except ValueError as e:
            # LOG: Erro de validação (erro de negócio)
            # ✅ Use WARNING (não ERROR) + padrões Datadog
            error_stack = traceback.format_exc()
            _attach_error(span, e, error_stack)
            _attach_error(tracer.current_root_span(), e, error_stack)
            logger.warning(
                f"Validation error: {str(e)}",
                extra={
                    'operation': 'error.simulation',
                    'error.type': 'ValueError',
                    'error.message': str(e),
                    'error_category': 'business_logic',
                    'is_test': True
                }
            )
            return jsonify({"error": str(e)}), 400
        
        # ========================================
        # EXEMPLO 3: ERRO GENÉRICO/INESPERADO
        # ========================================
        except Exception as e:
            # LOG: Erro inesperado - precisa investigação
            # ✅ BOM: Use padrões Datadog (error.type, error.message, error.stack)
            error_stack = traceback.format_exc()
            _attach_error(span, e, error_stack)
            _attach_error(tracer.current_root_span(), e, error_stack)
            logger.error(
                f"Unexpected error in simulation: {str(e)}",
                extra={
                    'operation': 'error.simulation',
                    'error.type': type(e).__name__,
                    'error.message': str(e),
                    'error.stack': error_stack,
                    'error_category': 'unexpected',
                    'is_test': True
                }
            )
            return jsonify({"error": "Internal server error"}), 500

