"""
Demo routes para testar o middleware do Datadog

Este arquivo contém endpoints de exemplo para demonstrar como o middleware
captura payloads de requisição e resposta como span tags.
"""

from flask import Blueprint, request, jsonify
from logging_config import logger

# Cria blueprint
middleware_demo_bp = Blueprint('middleware_demo', __name__, url_prefix='/middleware-demo')


@middleware_demo_bp.route('/json-payload', methods=['POST'])
def json_payload_demo():
    """
    Endpoint para testar captura de payload JSON.
    
    O middleware deve capturar:
    - http.payload.* tags do request body
    - http.response.payload.* tags da resposta
    """
    try:
        # Log da operação
        logger.info("Processing JSON payload demo", extra={
            'endpoint': 'json_payload_demo',
            'method': request.method,
            'content_type': request.content_type
        })
        
        # Obtém dados do request
        data = request.get_json() or {}
        
        # Simula processamento
        result = {
            'status': 'success',
            'received_data': data,
            'processed_at': '2024-01-01T00:00:00Z',
            'items_count': len(data.get('items', [])) if isinstance(data.get('items'), list) else 0
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in JSON payload demo: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@middleware_demo_bp.route('/form-data', methods=['POST'])
def form_data_demo():
    """
    Endpoint para testar captura de form data.
    
    O middleware deve capturar:
    - http.form.* tags do form data
    - http.response.payload.* tags da resposta
    """
    try:
        # Log da operação
        logger.info("Processing form data demo", extra={
            'endpoint': 'form_data_demo',
            'method': request.method,
            'content_type': request.content_type
        })
        
        # Obtém form data
        form_data = dict(request.form)
        
        # Simula processamento
        result = {
            'status': 'success',
            'received_fields': list(form_data.keys()),
            'field_count': len(form_data),
            'processed_at': '2024-01-01T00:00:00Z'
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in form data demo: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@middleware_demo_bp.route('/query-params', methods=['GET'])
def query_params_demo():
    """
    Endpoint para testar captura de query parameters.
    
    O middleware deve capturar:
    - http.query.* tags dos query parameters
    - http.response.payload.* tags da resposta
    """
    try:
        # Log da operação
        logger.info("Processing query params demo", extra={
            'endpoint': 'query_params_demo',
            'method': request.method,
            'query_params': dict(request.args)
        })
        
        # Obtém query parameters
        query_params = dict(request.args)
        
        # Simula processamento
        result = {
            'status': 'success',
            'received_params': query_params,
            'param_count': len(query_params),
            'processed_at': '2024-01-01T00:00:00Z'
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in query params demo: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@middleware_demo_bp.route('/large-payload', methods=['POST'])
def large_payload_demo():
    """
    Endpoint para testar truncamento de payloads grandes.
    
    O middleware deve:
    - Truncar payloads grandes (>4096 chars)
    - Adicionar tag http.request.body_raw_truncated=true
    """
    try:
        # Log da operação
        logger.info("Processing large payload demo", extra={
            'endpoint': 'large_payload_demo',
            'method': request.method,
            'content_type': request.content_type
        })
        
        # Obtém dados do request
        data = request.get_json() or {}
        
        # Simula processamento
        result = {
            'status': 'success',
            'message': 'Large payload processed successfully',
            'data_size': len(str(data)),
            'processed_at': '2024-01-01T00:00:00Z'
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in large payload demo: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@middleware_demo_bp.route('/error-response', methods=['POST'])
def error_response_demo():
    """
    Endpoint para testar captura de respostas de erro.
    
    O middleware deve capturar:
    - http.status_code=400 ou 500
    - Não deve capturar payload de resposta para erros
    """
    try:
        # Log da operação
        logger.info("Processing error response demo", extra={
            'endpoint': 'error_response_demo',
            'method': request.method
        })
        
        # Simula erro
        return jsonify({
            'error': 'Simulated error for testing',
            'code': 'DEMO_ERROR',
            'message': 'This is a test error response'
        }), 400
        
    except Exception as e:
        logger.error(f"Error in error response demo: {e}")
        return jsonify({'error': 'Internal server error'}), 500
