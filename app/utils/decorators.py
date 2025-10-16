"""
Request Logging Decorator

Demonstra como adicionar logging automático a todas as requisições.

Best Practice: Use decoradores para adicionar comportamento consistente
sem duplicar código em cada endpoint.
"""

import time
import logging
from functools import wraps
from flask import request

logger = logging.getLogger(__name__)


def log_request_context():
    """
    Decorator que adiciona logging automático para requests HTTP.
    
    Best Practices Demonstradas:
    1. Log no início e fim de cada request
    2. Inclui duração (performance monitoring)
    3. Inclui request_id para rastreamento
    4. Loga erros com contexto completo
    5. Usa structured logging (extra={})
    
    O que é logado:
    - Início: método, path, IP, user agent
    - Fim: duração, status (success/error)
    - Erro: stack trace completo, tipo de erro
    
    Uso:
        @app.route('/api/endpoint')
        @log_request_context()
        def my_endpoint():
            return {"status": "ok"}
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Gera ou extrai request ID para rastreamento
            request_id = request.headers.get('X-Request-ID', 
                                            f"req_{int(time.time() * 1000)}")
            user_agent = request.headers.get('User-Agent', 'unknown')
            
            # LOG 1: Request iniciado
            logger.info(
                f"Request started: {request.method} {request.path}",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.path,
                    'user_agent': user_agent[:50],  # Trunca user agents longos
                    'remote_addr': request.remote_addr
                }
            )
            
            start_time = time.time()
            
            try:
                # Executa o endpoint
                response = f(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # LOG 2: Request completado com sucesso
                logger.info(
                    f"Request completed: {request.method} {request.path}",
                    extra={
                        'request_id': request_id,
                        'duration_ms': round(duration_ms, 2),
                        'status': 'success'
                    }
                )
                
                return response
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # LOG 3: Request falhou - com contexto completo
                logger.error(
                    f"Request failed: {request.method} {request.path} - {str(e)}",
                    extra={
                        'request_id': request_id,
                        'duration_ms': round(duration_ms, 2),
                        'status': 'error',
                        'error_type': type(e).__name__
                    },
                    exc_info=True  # ✅ IMPORTANTE: Inclui stack trace completo
                )
                raise
        
        return decorated_function
    return decorator

