"""
Datadog APM Logging Best Practices Demo API - Main Application

Arquivo principal simplificado que orquestra todos os componentes.

ESTRUTURA DO PROJETO:
├── app.py                  # ← VOCÊ ESTÁ AQUI (orquestrador)
├── config.py               # Configurações
├── logging_config.py       # Setup de logging
├── utils/                  # Utilitários
│   ├── security.py         # Proteção de PII (masking, hashing)
│   └── decorators.py       # Request logging decorator
├── models/                 # Dados
│   └── data.py             # Mock data (users, products, transactions)
└── routes/                 # Endpoints (cada arquivo demonstra conceitos específicos)
    ├── home.py             # Endpoint raiz
    ├── health.py           # ⭐ DEBUG logging (health checks)
    ├── users.py            # ⭐ PII protection (masking, hashing)
    ├── products.py         # Logging simples
    ├── transactions.py     # ⭐⭐⭐ MAIS IMPORTANTE! Transaction stages, validações
    ├── analytics.py        # Logging de queries
    └── errors.py           # ⭐ Error handling (try/catch, categorização)

ARQUIVOS PRINCIPAIS PARA DEMONSTRAÇÃO:
1. routes/transactions.py - Logging de operações críticas
2. routes/users.py        - Proteção de PII
3. routes/errors.py       - Error handling
4. utils/security.py      - Funções de segurança
5. utils/decorators.py    - Request tracking
"""

import os
import traceback
from flask import Flask, request, make_response, jsonify, g
from werkzeug.exceptions import HTTPException
from ddtrace import tracer, patch_all
from ddtrace.debugging import DynamicInstrumentation

# Importa configuração
import config
from logging_config import logger

# Importa middleware do Datadog
from utils.datadog_middleware import DatadogTracingMiddleware

# Importa blueprints (rotas)
from routes import (
    health_bp,
    home_bp,
    users_bp,
    products_bp,
    transactions_bp,
    analytics_bp,
    errors_bp,
    dynamic_demo_bp,
)
from routes.middleware_demo import middleware_demo_bp

# ============================================================================
# DATADOG APM SETUP
# ============================================================================

# Habilita Dynamic Instrumentation
DynamicInstrumentation.enable()

# Habilita auto-instrumentação para Flask e bibliotecas
# Isso captura automaticamente requests HTTP, database calls, etc
patch_all()

# ============================================================================
# FLASK APP SETUP
# ============================================================================

app = Flask(__name__)

# ============================================================================
# CORS SETUP (RUM <-> TRACES CORRELATION HEADERS)
# ============================================================================

_CORS_ALLOWED_HEADERS = [
    "Content-Type",
    "Accept",
    "X-Request-Id",
    "x-datadog-trace-id",
    "x-datadog-parent-id",
    "x-datadog-origin",
    "x-datadog-sampling-priority",
    "traceparent",
    "tracestate",
    "b3",
    "x-b3-traceid",
    "x-b3-spanid",
    "x-b3-sampled",
    "x-b3-flags"
]

_CORS_ALLOWED_METHODS = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
_CORS_ALLOWED_HEADERS_VALUE = ", ".join(_CORS_ALLOWED_HEADERS)


@app.before_request
def _handle_preflight():
    if request.method != "OPTIONS":
        return None
    response = make_response("", 204)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = _CORS_ALLOWED_METHODS
    response.headers["Access-Control-Allow-Headers"] = _CORS_ALLOWED_HEADERS_VALUE
    response.headers["Access-Control-Max-Age"] = "600"
    return response


@app.after_request
def _add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = _CORS_ALLOWED_METHODS
    response.headers["Access-Control-Allow-Headers"] = _CORS_ALLOWED_HEADERS_VALUE
    return response

# Inicializa middleware do Datadog para capturar payloads
DatadogTracingMiddleware(app)

# Registra todos os blueprints (endpoints)
app.register_blueprint(home_bp)
app.register_blueprint(health_bp)
app.register_blueprint(users_bp)
app.register_blueprint(products_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(errors_bp)
app.register_blueprint(dynamic_demo_bp)
app.register_blueprint(middleware_demo_bp)

# ============================================================================
# ERROR HANDLING (attach error tags to active span)
# ============================================================================

def _tag_error_on_span(exc):
    span = tracer.current_span() or tracer.current_root_span()
    if not span:
        return
    stack = traceback.format_exc()
    span.set_tag("error", True)
    span.set_tag("error.type", type(exc).__name__)
    span.set_tag("error.message", str(exc))
    span.set_tag("error.stack", stack)
    span.set_exc_info(type(exc), exc, exc.__traceback__)


@app.errorhandler(Exception)
def handle_exception(exc):
    status_code = 500
    error_message = "Internal server error"
    error_category = "unexpected"
    request_id = request.headers.get("X-Request-Id")
    session_id = request.headers.get("X-Session-Id")

    if isinstance(exc, ValueError):
        status_code = 400
        error_message = str(exc)
        error_category = "business_logic"
    elif isinstance(exc, ZeroDivisionError):
        status_code = 400
        error_message = "Division by zero"
        error_category = "arithmetic_error"
    elif isinstance(exc, TimeoutError):
        status_code = 504
        error_message = "Request timeout"
        error_category = "timeout"
    elif isinstance(exc, HTTPException):
        status_code = exc.code or 500
        error_message = exc.description or error_message
        error_category = "http_error"

    _tag_error_on_span(exc)

    logger_level = logger.warning if status_code < 500 else logger.error
    logger_level(
        f"API error handled: {error_message}",
        extra={
            "operation": "api.error_handler",
            "request_id": request_id,
            "session_id": session_id,
            "http.method": request.method,
            "http.url": request.path,
            "error.type": type(exc).__name__,
            "error.message": str(exc),
            "error.stack": traceback.format_exc(),
            "error_category": error_category,
        }
    )

    payload = {"error": error_message}
    payload.update({
        "request_id": request_id,
        "session_id": session_id,
        "http": {
            "method": request.method,
            "path": request.path,
            "query": request.args.to_dict(flat=True),
        },
        "client": {
            "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
            "user_agent": request.user_agent.string,
        },
    })
    if hasattr(g, "error_context"):
        payload.update(g.error_context)

    return jsonify(payload), status_code

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == "__main__":
    # Log de inicialização da aplicação
    logger.info(
        "Starting Datadog APM Logging Best Practices Demo API",
        extra={
            'service': config.SERVICE_NAME,
            'environment': config.ENVIRONMENT,
            'version': config.VERSION,
            'event': 'application_startup'
        }
    )
    
    # Inicia servidor Flask
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
