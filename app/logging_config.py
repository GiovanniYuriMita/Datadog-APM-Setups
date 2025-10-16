"""
Logging Configuration for Datadog APM Integration

Este módulo demonstra como configurar logging estruturado em JSON com correlação APM.

Best Practices:
- Use formato JSON para logs estruturados
- Inclua trace_id e span_id para correlação com APM
- Desabilite logs redundantes (Werkzeug/Flask access logs)
- Configure nível apropriado (INFO em produção, DEBUG em dev)
"""

import logging
import sys
from pythonjsonlogger import jsonlogger
from config import LOG_LEVEL

class DatadogJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter que inclui campos do Datadog APM
    
    Best Practice: Logs em JSON são mais fáceis de:
    - Parsear e indexar no Datadog
    - Filtrar e buscar
    - Criar dashboards e alertas
    """
    
    def add_fields(self, log_record, record, message_dict):
        super(DatadogJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Adicionar campos do Datadog APM
        log_record['dd.service'] = getattr(record, 'dd.service', '')
        log_record['dd.env'] = getattr(record, 'dd.env', '')
        log_record['dd.version'] = getattr(record, 'dd.version', '')
        log_record['dd.trace_id'] = getattr(record, 'dd.trace_id', '0')
        log_record['dd.span_id'] = getattr(record, 'dd.span_id', '0')
        
        # Adicionar timestamp
        log_record['timestamp'] = self.formatTime(record, self.datefmt)
        
        # Adicionar severity
        log_record['severity'] = record.levelname
        
        # Adicionar source
        log_record['logger'] = record.name
        log_record['file'] = record.filename
        log_record['line'] = record.lineno

def setup_logging():
    """
    Configura logging em formato JSON para Datadog APM
    
    Best Practices Implementadas:
    1. Formato JSON para estruturação automática
    2. Correlação com APM (trace_id, span_id)
    3. Desabilita logs redundantes do Werkzeug
    4. Mantém apenas logs de negócio relevantes
    """
    
    # Configurar handler com formato JSON
    handler = logging.StreamHandler(sys.stdout)
    formatter = DatadogJsonFormatter(
        '%(timestamp)s %(severity)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    root_logger.addHandler(handler)
    
    # IMPORTANTE: Desabilitar logs do Werkzeug (redundantes com APM)
    # O APM já captura todos os requests HTTP
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logging.getLogger('werkzeug').disabled = True
    
    # Logger da aplicação
    app_logger = logging.getLogger(__name__)
    
    return app_logger

# Logger global para a aplicação
logger = setup_logging()

