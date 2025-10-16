"""
Context Enrichment Utilities

Funções para adicionar contexto rico aos logs sem expor PII.

Best Practices:
- Adicione contexto de negócio relevante
- Infira informações úteis (geolocalização, device type)
- Nunca exponha dados sensíveis
- Use para troubleshooting E analytics
"""

import random
from datetime import datetime
from flask import request


def extract_device_info():
    """
    Extrai informações de device/browser do User-Agent.
    
    Best Practice: Informações de device ajudam a:
    - Identificar problemas específicos de plataforma
    - Entender distribuição de usuários
    - Troubleshooting de bugs mobile vs desktop
    
    Returns:
        dict: Informações de device (sem PII)
    """
    user_agent = request.headers.get('User-Agent', '').lower()
    
    # Detectar tipo de device
    if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
        device_type = 'mobile'
    elif 'tablet' in user_agent or 'ipad' in user_agent:
        device_type = 'tablet'
    else:
        device_type = 'desktop'
    
    # Detectar OS
    if 'windows' in user_agent:
        os = 'windows'
    elif 'mac' in user_agent or 'darwin' in user_agent:
        os = 'macos'
    elif 'linux' in user_agent:
        os = 'linux'
    elif 'android' in user_agent:
        os = 'android'
    elif 'ios' in user_agent or 'iphone' in user_agent or 'ipad' in user_agent:
        os = 'ios'
    else:
        os = 'unknown'
    
    # Detectar browser
    if 'chrome' in user_agent and 'edg' not in user_agent:
        browser = 'chrome'
    elif 'safari' in user_agent and 'chrome' not in user_agent:
        browser = 'safari'
    elif 'firefox' in user_agent:
        browser = 'firefox'
    elif 'edg' in user_agent:
        browser = 'edge'
    else:
        browser = 'other'
    
    return {
        'device.type': device_type,
        'device.os': os,
        'device.browser': browser
    }


def extract_geo_info():
    """
    Extrai informações de geolocalização (simulado para demo).
    
    Best Practice: Geolocalização ajuda a:
    - Identificar problemas regionais
    - Compliance (GDPR, LGPD)
    - Análise de mercado
    - Fraud detection
    
    IMPORTANTE: Em produção, use serviço de GeoIP real
    (MaxMind, IP2Location, CloudFlare, etc)
    
    Returns:
        dict: Informações geo (cidade/país, não IP completo!)
    """
    # Em produção, use: geoip2.database.Reader ou API
    # Aqui simulamos baseado no IP
    
    ip = request.remote_addr
    
    # Simulação simples para demo
    # Em produção, consulte database GeoIP
    if ip.startswith('192.168') or ip.startswith('127.0'):
        # IP local - assumir localização padrão
        country = 'BR'
        city = 'São Paulo'
        region = 'SP'
    else:
        # Simulação aleatória para demo
        locations = [
            {'country': 'BR', 'city': 'São Paulo', 'region': 'SP'},
            {'country': 'BR', 'city': 'Rio de Janeiro', 'region': 'RJ'},
            {'country': 'US', 'city': 'New York', 'region': 'NY'},
            {'country': 'US', 'city': 'San Francisco', 'region': 'CA'},
        ]
        location = random.choice(locations)
        country = location['country']
        city = location['city']
        region = location['region']
    
    return {
        'geo.country': country,
        'geo.city': city,
        'geo.region': region
        # ⚠️ IMPORTANTE: NÃO logue IP completo! 
        # IP é considerado PII em muitas jurisdições (GDPR, LGPD)
    }


def extract_session_info():
    """
    Extrai informações de sessão.
    
    Best Practice: Session tracking ajuda a:
    - Agrupar ações do mesmo usuário
    - Identificar padrões de uso
    - Troubleshooting de fluxos específicos
    
    Returns:
        dict: Informações de sessão (sem PII)
    """
    # Em produção, isso viria de cookies/tokens
    session_id = request.headers.get('X-Session-ID', f"session_{int(datetime.now().timestamp())}")
    
    return {
        'session.id': session_id[:16],  # Truncado para não expor hash completo
        'session.referrer': request.referrer if request.referrer else 'direct'
    }


def calculate_risk_score(user, product, quantity):
    """
    Calcula score de risco de fraude (simulado).
    
    Best Practice: Risk scoring ajuda a:
    - Fraud detection
    - Compliance
    - Business intelligence
    - Troubleshooting de chargebacks
    
    IMPORTANTE: Não logue detalhes de por que o score é alto
    (isso seria informação sensível)
    
    Returns:
        dict: Métricas de risco
    """
    # Simulação simples
    risk_score = 0
    risk_factors = []
    
    # Valor alto
    total = product['price'] * quantity
    if total > 1000:
        risk_score += 20
        risk_factors.append('high_value')
    
    # Conta nova
    if user.get('total_transactions', 0) < 5:
        risk_score += 30
        risk_factors.append('new_account')
    
    # Velocidade (muitas transações rápidas)
    # Em produção, verificaria transações recentes
    if random.random() < 0.1:  # 10% chance para demo
        risk_score += 50
        risk_factors.append('high_velocity')
    
    risk_level = 'low' if risk_score < 30 else 'medium' if risk_score < 60 else 'high'
    
    return {
        'risk.score': risk_score,
        'risk.level': risk_level,
        'risk.requires_review': risk_score >= 60
        # ⚠️ NÃO logue risk_factors - seria informação sensível
        # Fraudadores poderiam aprender o sistema
    }


def extract_payment_context(user, amount):
    """
    Extrai contexto de pagamento (sem dados sensíveis).
    
    Best Practice: Contexto de pagamento ajuda a:
    - Troubleshooting de falhas de pagamento
    - Análise de métodos preferidos
    - Compliance e auditoria
    
    ⚠️ NUNCA logue:
    - Números de cartão
    - CVV
    - Dados bancários completos
    
    Returns:
        dict: Contexto de pagamento (seguro)
    """
    payment_method = user.get('preferred_payment', 'credit_card')
    
    # Informações seguras de contexto
    return {
        'payment.method': payment_method,
        'payment.amount': amount,
        'payment.currency': 'BRL',
        'payment.requires_3ds': amount > 500,  # 3D Secure para valores altos
        'payment.installments': 1 if amount < 200 else (3 if amount < 1000 else 12)
        # ✅ BOM: Metadata útil sem expor dados sensíveis
    }


def get_inventory_context(product, quantity):
    """
    Contexto de inventário para análise e alertas.
    
    Best Practice: Contexto de inventário ajuda a:
    - Identificar produtos em baixo estoque
    - Otimizar reposição
    - Análise de demanda
    
    Returns:
        dict: Métricas de inventário
    """
    remaining = product['stock'] - quantity
    threshold = product.get('restock_threshold', 10)
    
    return {
        'inventory.product_sku': product.get('sku', 'unknown'),
        'inventory.category': product.get('category', 'unknown'),
        'inventory.stock_before': product['stock'],
        'inventory.stock_after': remaining,
        'inventory.needs_restock': remaining <= threshold,
        'inventory.restock_threshold': threshold,
        'inventory.vendor': product.get('vendor', 'unknown')
    }


def get_business_metrics(user):
    """
    Métricas de negócio para análise.
    
    Best Practice: Business metrics ajudam a:
    - Identificar VIPs (high lifetime value)
    - Segmentação de usuários
    - Análise de comportamento
    - Personalização de experiência
    
    Returns:
        dict: Métricas de negócio
    """
    return {
        'user.account_type': user.get('account_type', 'basic'),
        'user.total_transactions': user.get('total_transactions', 0),
        'user.lifetime_value': user.get('lifetime_value', 0),
        'user.is_vip': user.get('lifetime_value', 0) > 10000,
        'user.account_age_days': (datetime.now() - datetime.fromisoformat(user.get('created_at', '2024-01-01'))).days
    }


def get_performance_context(start_time):
    """
    Contexto de performance para SLO tracking.
    
    Best Practice: Performance metrics ajudam a:
    - Identificar operações lentas
    - SLO monitoring
    - Capacity planning
    
    Returns:
        dict: Métricas de performance
    """
    import time
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'performance.duration_ms': round(duration_ms, 2),
        'performance.is_slow': duration_ms > 1000,
        'performance.is_timeout_risk': duration_ms > 5000
    }

