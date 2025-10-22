"""
Datadog Tracing Middleware

Middleware para capturar payloads de requisição e resposta como span tags do Datadog.
Baseado na lógica PHP fornecida, adaptado para Python/Flask.

Funcionalidades:
- Captura payload de requisição como span tags
- Captura payload de resposta como span tags
- Adiciona informações HTTP básicas
- Trunca payloads grandes para evitar span bloat
- Suporte a diferentes tipos de conteúdo
"""

import json
import time
from typing import Any, Dict, Optional
from flask import request, g
from ddtrace import tracer
import logging

logger = logging.getLogger(__name__)


class DatadogTracingMiddleware:
    """
    Middleware para adicionar informações de requisição e resposta como span tags do Datadog.
    """
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa o middleware com a aplicação Flask."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Executado antes de cada requisição."""
        try:
            # Inicia o timer para calcular tempo de resposta
            g.request_start_time = time.time()
            
            # Obtém o span ativo
            active_span = tracer.current_span()
            if not active_span:
                return
            
            # Adiciona informações básicas da requisição
            self._add_request_basic_info(active_span)
            
            # Adiciona payload da requisição
            self._add_request_payload_tags(active_span)
            
            # Adiciona informações específicas da rota
            self._add_route_specific_tags(active_span)
            
        except Exception as e:
            logger.error(f'Datadog tracing error (before_request): {e}')
    
    def after_request(self, response):
        """Executado após cada requisição."""
        try:
            # Obtém o span ativo
            active_span = tracer.current_span()
            if not active_span:
                return response
            
            # Adiciona informações da resposta
            self._add_response_tags(active_span, response)
            
            # Adiciona payload da resposta se aplicável
            self._add_response_payload_tags(active_span, response)
            
        except Exception as e:
            logger.error(f'Datadog tracing error (after_request): {e}')
        
        return response
    
    def _add_request_basic_info(self, span):
        """Adiciona informações básicas da requisição."""
        try:
            # Informações HTTP básicas
            span.set_tag('http.method', request.method)
            span.set_tag('http.url', request.url)
            span.set_tag('http.route', request.endpoint or request.path)
            span.set_tag('http.user_agent', request.headers.get('User-Agent', ''))
            
            # Request ID se disponível
            request_id = request.headers.get('X-Request-ID')
            if request_id:
                span.set_tag('http.request_id', request_id)
            
            # Content-Type
            content_type = request.headers.get('Content-Type', '')
            if content_type:
                span.set_tag('http.content_type', content_type)
                
        except Exception as e:
            logger.error(f'Error adding request basic info: {e}')
    
    def _add_request_payload_tags(self, span):
        """Adiciona payload da requisição como span tags."""
        try:
            content_type = request.headers.get('Content-Type', '')
            
            # Captura raw body para conteúdo texto
            if self._is_text_content(content_type):
                raw_data = request.get_data(as_text=True)
                if raw_data:
                    max_length = 4096
                    if len(raw_data) <= max_length:
                        span.set_tag('http.request.body_raw', raw_data)
                    else:
                        span.set_tag('http.request.body_raw', raw_data[:max_length])
                        span.set_tag('http.request.body_raw_truncated', 'true')
            
            # Captura JSON payload
            if 'application/json' in content_type:
                try:
                    json_data = request.get_json()
                    if json_data:
                        self._add_payload_tags(json_data, span, 'http.payload')
                except Exception as e:
                    logger.warning(f'Error parsing JSON payload: {e}')
            
            # Captura form data
            if request.form:
                form_data = dict(request.form)
                for key, value in form_data.items():
                    if value and len(str(value)) <= 1000:  # Limita tamanho
                        span.set_tag(f'http.form.{key}', str(value))
            
            # Captura query parameters
            if request.args:
                for key, value in request.args.items():
                    if value and len(str(value)) <= 1000:
                        span.set_tag(f'http.query.{key}', str(value))
                        
        except Exception as e:
            logger.error(f'Error adding request payload tags: {e}')
    
    def _add_response_tags(self, span, response):
        """Adiciona informações da resposta."""
        try:
            # Status code
            span.set_tag('http.status_code', str(response.status_code))
            
            # Tamanho da resposta
            if hasattr(response, 'content_length') and response.content_length:
                span.set_tag('http.response.size', str(response.content_length))
            
            # Tempo de resposta
            if hasattr(g, 'request_start_time'):
                response_time = (time.time() - g.request_start_time) * 1000
                span.set_tag('http.response.time_ms', f'{response_time:.2f}')
            
            # Content-Type da resposta
            if response.content_type:
                span.set_tag('http.response.content_type', response.content_type)
                
        except Exception as e:
            logger.error(f'Error adding response tags: {e}')
    
    def _add_response_payload_tags(self, span, response):
        """Adiciona payload da resposta como span tags."""
        try:
            # Só adiciona payload para respostas JSON
            if (response.content_type and 
                'application/json' in response.content_type and 
                response.status_code < 400):  # Só para respostas de sucesso
                
                # Obtém dados da resposta
                response_data = response.get_json()
                if response_data:
                    self._add_payload_tags(response_data, span, 'http.response.payload')
                    
        except Exception as e:
            logger.error(f'Error adding response payload tags: {e}')
    
    def _add_route_specific_tags(self, span):
        """Adiciona tags específicas da rota."""
        try:
            # Nome da rota/endpoint
            if request.endpoint:
                span.set_tag('flask.route.name', request.endpoint)
            
            # Parâmetros da rota
            if hasattr(request, 'view_args') and request.view_args:
                for key, value in request.view_args.items():
                    if isinstance(value, (str, int, float)):
                        span.set_tag(f'flask.route.param.{key}', str(value))
                        
        except Exception as e:
            logger.error(f'Error adding route specific tags: {e}')
    
    def _add_payload_tags(self, data: Dict[str, Any], span, prefix: str):
        """Adiciona tags de payload de forma recursiva."""
        try:
            for key, value in data.items():
                if isinstance(value, (str, int, float, bool)):
                    # Valores escalares
                    tag_value = str(value)
                    if len(tag_value) <= 1000:  # Limita tamanho
                        span.set_tag(f'{prefix}.{key}', tag_value)
                elif isinstance(value, list) and len(value) <= 10:
                    # Arrays pequenos
                    span.set_tag(f'{prefix}.{key}', json.dumps(value))
                elif isinstance(value, dict):
                    # Objetos aninhados (primeiro nível apenas)
                    for nested_key, nested_value in value.items():
                        if isinstance(nested_value, (str, int, float, bool)):
                            tag_value = str(nested_value)
                            if len(tag_value) <= 1000:
                                span.set_tag(f'{prefix}.{key}.{nested_key}', tag_value)
                                
        except Exception as e:
            logger.error(f'Error adding payload tags: {e}')
    
    def _is_text_content(self, content_type: str) -> bool:
        """Verifica se o content-type é texto."""
        text_types = [
            'text/',
            'application/json',
            'application/x-www-form-urlencoded',
            'application/xml',
            'application/javascript',
        ]
        
        return any(content_type.startswith(t) for t in text_types)
