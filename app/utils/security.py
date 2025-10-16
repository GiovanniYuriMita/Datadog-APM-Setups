"""
Security Utilities for PII Protection

Este módulo demonstra como proteger dados sensíveis em logs.

Best Practices:
- NUNCA logue PII sem tratamento de dados sensíveis
- Use mascaramento para dados que precisam ser parcialmente visíveis
- Use hashing para IDs que precisam ser rastreáveis mas não identificáveis
"""

import hashlib


def mask_sensitive_data(value, visible_chars=4):
    """
    Mascara dados sensíveis mostrando apenas os primeiros caracteres.
    
    Best Practice: Use para emails, números de telefone, etc.
    
    Exemplos:
        >>> mask_sensitive_data("john.doe@example.com", 4)
        "john********************"
        
        >>> mask_sensitive_data("4111111111111111", 4)  # Cartão de crédito
        "4111************"
    
    Args:
        value: String a ser mascarada
        visible_chars: Número de caracteres visíveis no início
    
    Returns:
        String mascarada
    """
    if not value:
        return "***MASKED***"
    
    if len(value) <= visible_chars:
        return "*" * len(value)
    
    return value[:visible_chars] + "*" * (len(value) - visible_chars)


def hash_user_identifier(user_id):
    """
    Cria hash consistente de identificadores de usuário.
    
    Best Practice: Use para rastrear usuários em logs sem expor identidade real.
    
    Por que usar hash ao invés de mascaramento?
    - Permite rastrear todas as ações do mesmo usuário
    - Não expõe informação pessoal
    - É determinístico (mesmo user_id sempre gera mesmo hash)
    
    Exemplo de log:
        ✅ BOM: user_id_hash=a1b2c3d4e5f6g7h8
        ❌ RUIM: user_id=john.doe@example.com
    
    Args:
        user_id: ID do usuário (pode ser email, CPF, etc)
    
    Returns:
        Hash SHA256 truncado (16 caracteres)
    """
    return hashlib.sha256(str(user_id).encode()).hexdigest()[:16]

