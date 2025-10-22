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
from flask import Flask
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
    errors_bp
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
app.register_blueprint(middleware_demo_bp)

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
