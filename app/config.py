"""
Configuration and Constants

Centraliza todas as configurações da aplicação.
"""

import os

# Service Configuration
SERVICE_NAME = os.getenv('DD_SERVICE', 'chofs-api')
ENVIRONMENT = os.getenv('DD_ENV', 'development')
VERSION = os.getenv('DD_VERSION', 'unknown')

# Server Configuration
HOST = '0.0.0.0'
PORT = 8080
DEBUG = False

# Logging Configuration
LOG_FORMAT = (
    '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
    '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s '
    'dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
    '- %(message)s'
)
LOG_LEVEL = 'INFO'

