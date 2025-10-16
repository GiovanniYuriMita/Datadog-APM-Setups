# Logging Best Practices - Datadog APM Demo

Este documento demonstra as melhores práticas de logging implementadas nesta aplicação, especialmente para integração com Datadog APM.

## 🎯 Objetivos

Esta demo foi criada para demonstrar aos desenvolvedores como escrever logs **significativos**, **contextuais** e **seguros** que:

1. ✅ Facilitam troubleshooting e debugging
2. ✅ Mantêm correlação com traces do APM
3. ✅ Protegem PII e dados sensíveis
4. ✅ Fornecem contexto de negócio relevante
5. ✅ Seguem estrutura consistente

---

## 📋 Princípios Fundamentais

### 1. **Correlação Log-Trace**

**Por que é importante:** Permite navegar dos logs para traces e vice-versa no Datadog.

**Implementação:**
```python
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s '
          'dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')
```

**Benefícios:**
- Identificação rápida de problemas
- Contexto completo de requisições
- Navegação fluida entre logs e APM

---

### 2. **Logging Estruturado (Structured Logging)**

**Por que é importante:** Logs estruturados são queryáveis, filtráveis e mais úteis para análise.

**✅ BOM - Com contexto estruturado:**
```python
logger.info(
    "Transaction completed successfully",
    extra={
        'operation': 'transaction.create',
        'transaction_id': transaction_id,
        'user_id_hash': hash_user_identifier(user_id),
        'product_id': product_id,
        'total_amount': total_amount,
        'transaction_stage': 'completed',
        'status': 'success'
    }
)
```

**❌ RUIM - Sem contexto estruturado:**
```python
logger.info(f"Transaction {transaction_id} completed")
```

**Benefícios:**
- Fácil criação de dashboards
- Filtros e agregações precisas
- Alertas baseados em valores específicos

---

### 3. **Proteção de PII e Dados Sensíveis**

**⚠️ CRÍTICO:** Nunca logue dados pessoais ou sensíveis em texto claro.

**Exemplos de dados que NUNCA devem ser logados:**
- ❌ Emails completos
- ❌ Números de cartão de crédito
- ❌ CPF/RG/SSN
- ❌ Senhas (obviamente!)
- ❌ Tokens de autenticação
- ❌ Endereços completos

**✅ BOM - Com mascaramento:**
```python
def mask_sensitive_data(value, visible_chars=4):
    """Mascara dados sensíveis"""
    if len(value) <= visible_chars:
        return "*" * len(value)
    return value[:visible_chars] + "*" * (len(value) - visible_chars)

def hash_user_identifier(user_id):
    """Hash consistente para tracking sem expor PII"""
    return hashlib.sha256(str(user_id).encode()).hexdigest()[:16]

# Uso
logger.info(
    "User profile fetched",
    extra={
        'user_id_hash': hash_user_identifier(user_id),  # ✅ Hash
        'has_balance': user['balance'] > 0  # ✅ Boolean ao invés de valor
    }
)
```

**❌ RUIM - Expondo PII:**
```python
logger.info(f"User {email} logged in")  # ❌ Email exposto!
logger.info(f"Processing payment for card {card_number}")  # ❌ Cartão exposto!
```

---

### 4. **Níveis de Log Apropriados**

Use o nível correto para cada situação:

| Nível | Quando Usar | Exemplo |
|-------|-------------|---------|
| **DEBUG** | Informações detalhadas para debugging | Health checks, valores internos |
| **INFO** | Eventos normais de negócio | Transação criada, usuário logado |
| **WARNING** | Situações inesperadas mas recuperáveis | Usuário não encontrado, estoque baixo |
| **ERROR** | Erros que precisam atenção | Falha de pagamento, timeout de API |
| **CRITICAL** | Falhas graves do sistema | Banco de dados inacessível |

**Exemplos:**

```python
# DEBUG - Para desenvolvimento, evitar em produção
logger.debug("Health check requested")

# INFO - Operações normais de negócio
logger.info(
    "Transaction completed successfully",
    extra={'transaction_id': txn_id, 'amount': amount}
)

# WARNING - Problemas esperados
logger.warning(
    "User not found",
    extra={'user_id_hash': user_hash, 'reason': 'user_not_in_database'}
)

# ERROR - Erros que precisam investigação
logger.error(
    "Payment gateway timeout",
    extra={'gateway': 'stripe', 'timeout_seconds': 30},
    exc_info=True  # Inclui stack trace
)
```

---

### 5. **Contexto de Negócio**

**Por que é importante:** Logs devem contar a história do que está acontecendo no negócio.

**✅ BOM - Com contexto de negócio:**
```python
logger.info(
    "Transaction failed - insufficient stock",
    extra={
        'operation': 'transaction.create',
        'product_id': product_id,
        'requested_quantity': 5,
        'available_stock': 2,
        'failure_reason': 'insufficient_stock',
        'transaction_stage': 'inventory_check'
    }
)
```

**❌ RUIM - Sem contexto:**
```python
logger.error("Stock validation failed")
```

**Perguntas que seus logs devem responder:**
- Qual operação estava sendo executada?
- Em que estágio falhou?
- Por que falhou?
- Quais valores estavam envolvidos?
- Qual foi o impacto?

---

### 6. **Logging em Try/Catch**

**✅ BOM - Com contexto completo:**
```python
try:
    result = process_payment(user_id, amount)
except PaymentGatewayError as e:
    logger.error(
        f"Payment gateway error: {str(e)}",
        extra={
            'operation': 'payment.process',
            'user_id_hash': hash_user_identifier(user_id),
            'amount': amount,
            'gateway': 'stripe',
            'error_type': type(e).__name__,
            'error_code': e.code if hasattr(e, 'code') else None
        },
        exc_info=True  # ✅ Inclui stack trace completo
    )
    # Raise ou handle apropriadamente
    raise
except Exception as e:
    logger.error(
        f"Unexpected error processing payment: {str(e)}",
        extra={
            'operation': 'payment.process',
            'user_id_hash': hash_user_identifier(user_id),
            'error_type': type(e).__name__
        },
        exc_info=True
    )
    raise
```

**❌ RUIM - Log genérico:**
```python
try:
    result = process_payment(user_id, amount)
except Exception as e:
    logger.error(f"Error: {e}")  # ❌ Sem contexto, sem stack trace
```

---

### 7. **Request Tracking**

**Por que é importante:** Rastrear cada requisição facilita debugging de problemas específicos.

**Implementação com decorator:**
```python
def log_request_context():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            request_id = request.headers.get('X-Request-ID', 
                                            f"req_{int(time.time() * 1000)}")
            
            logger.info(
                f"Request started: {request.method} {request.path}",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.path,
                    'remote_addr': request.remote_addr
                }
            )
            
            start_time = time.time()
            
            try:
                response = f(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
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
                
                logger.error(
                    f"Request failed: {request.method} {request.path}",
                    extra={
                        'request_id': request_id,
                        'duration_ms': round(duration_ms, 2),
                        'status': 'error',
                        'error_type': type(e).__name__
                    },
                    exc_info=True
                )
                raise
        
        return decorated_function
    return decorator
```

---

### 8. **Transaction Stages (Auditoria)**

**Por que é importante:** Para operações críticas (transações, pagamentos), logue cada estágio.

**Exemplo:**
```python
# Estágio 1: Iniciado
logger.info(
    "Transaction initiated",
    extra={
        'transaction_id': txn_id,
        'transaction_stage': 'initiated',
        'user_id_hash': user_hash,
        'product_id': product_id
    }
)

# Estágio 2: Validação
logger.info(
    "Validating user and product",
    extra={
        'transaction_id': txn_id,
        'transaction_stage': 'validation'
    }
)

# Estágio 3: Verificação de estoque
logger.info(
    "Checking inventory",
    extra={
        'transaction_id': txn_id,
        'transaction_stage': 'inventory_check',
        'requested_quantity': qty,
        'available_stock': stock
    }
)

# Estágio 4: Processamento de pagamento
logger.info(
    "Processing payment",
    extra={
        'transaction_id': txn_id,
        'transaction_stage': 'payment_processing',
        'amount': amount
    }
)

# Estágio 5: Concluído
logger.info(
    "Transaction completed",
    extra={
        'transaction_id': txn_id,
        'transaction_stage': 'completed',
        'status': 'success'
    }
)
```

---

### 9. **Custom Spans no Datadog APM**

**Por que é importante:** Combine logs com spans customizados para visibilidade completa.

**Implementação:**
```python
with tracer.trace("transaction.create", service="chofs-api") as span:
    # Adicione tags aos spans
    span.set_tag("user_id_hash", hash_user_identifier(user_id))
    span.set_tag("product_id", product_id)
    span.set_tag("transaction_stage", "processing")
    
    # Logue com o contexto do span
    logger.info(
        "Processing transaction",
        extra={
            'operation': 'transaction.create',
            'user_id_hash': hash_user_identifier(user_id)
        }
    )
    
    # Seu código aqui...
```

---

## 🚫 Anti-Patterns - O que NÃO fazer

### 1. Log Pollution (Poluição de Logs)
```python
# ❌ RUIM - Muito verboso
for item in items:
    logger.info(f"Processing item {item}")  # 1000s de logs!

# ✅ BOM - Log agregado
logger.info(f"Processing {len(items)} items", 
           extra={'item_count': len(items)})
```

### 2. Logs Sem Contexto
```python
# ❌ RUIM
logger.error("Operation failed")

# ✅ BOM
logger.error(
    "Payment processing failed",
    extra={
        'operation': 'payment.process',
        'user_id_hash': user_hash,
        'error_code': 'GATEWAY_TIMEOUT'
    }
)
```

### 3. String Formatting Caro
```python
# ❌ RUIM - Concatenação cara executada sempre
logger.debug("Data: " + json.dumps(large_object))

# ✅ BOM - Lazy evaluation
logger.debug("Data: %s", large_object)
```

### 4. Informação Sensível
```python
# ❌ NUNCA FAÇA ISSO
logger.info(f"User {email} paid with card {card_number}")
logger.info(f"Password: {password}")
logger.info(f"API Key: {api_key}")

# ✅ BOM
logger.info(
    "Payment processed",
    extra={
        'user_id_hash': hash_user_identifier(user_id),
        'payment_method_type': 'credit_card',
        'last_4_digits': card_last_4
    }
)
```

---

## 📊 Exemplos Práticos do Código

### Exemplo 1: Buscar Usuário
```python
@app.route('/api/user/<user_id>', methods=['GET'])
@log_request_context()
def get_user(user_id):
    with tracer.trace("user.fetch", service="chofs-api") as span:
        span.set_tag("user_id_hash", hash_user_identifier(user_id))
        
        logger.info(
            "Fetching user profile",
            extra={
                'operation': 'user.fetch',
                'user_id_hash': hash_user_identifier(user_id),
                'requested_fields': 'all'
            }
        )
        
        if user_id not in MOCK_USERS:
            logger.warning(
                "User not found",
                extra={
                    'operation': 'user.fetch',
                    'user_id_hash': hash_user_identifier(user_id),
                    'reason': 'user_not_in_database'
                }
            )
            return jsonify({"error": "User not found"}), 404
        
        # ... resto do código
```

### Exemplo 2: Criar Transação
```python
@app.route('/api/transaction', methods=['POST'])
@log_request_context()
def create_transaction():
    with tracer.trace("transaction.create", service="chofs-api") as span:
        data = request.get_json()
        
        # Log de cada estágio
        logger.info(
            "Transaction initiated",
            extra={
                'operation': 'transaction.create',
                'transaction_stage': 'initiated'
            }
        )
        
        # Validação
        if product['stock'] < quantity:
            logger.warning(
                "Transaction failed - insufficient stock",
                extra={
                    'operation': 'transaction.create',
                    'product_id': product_id,
                    'requested_quantity': quantity,
                    'available_stock': product['stock'],
                    'failure_reason': 'insufficient_stock',
                    'transaction_stage': 'inventory_check'
                }
            )
            return jsonify({"error": "Insufficient stock"}), 400
        
        # ... processamento ...
        
        logger.info(
            "Transaction completed successfully",
            extra={
                'operation': 'transaction.create',
                'transaction_id': transaction_id,
                'total_amount': total_amount,
                'transaction_stage': 'completed',
                'status': 'success'
            }
        )
```

---

## 🎓 Checklist para Desenvolvedores

Antes de fazer commit, verifique:

- [ ] Todos os logs têm contexto estruturado (`extra={}`)
- [ ] Nenhum PII está sendo logado em texto claro
- [ ] Níveis de log estão apropriados (DEBUG, INFO, WARNING, ERROR)
- [ ] Exceções incluem `exc_info=True` quando apropriado
- [ ] Operações críticas de negócio são logadas
- [ ] IDs sensíveis são hasheados
- [ ] Logs incluem `operation` para identificar a operação
- [ ] Falhas incluem `failure_reason` ou `error_type`
- [ ] Transações incluem `transaction_stage`
- [ ] Não há log pollution (logs em loops, etc)

---

## 🔍 Queries Úteis no Datadog

Com logging estruturado, você pode fazer queries poderosas:

```
# Todas as transações falhadas por estoque insuficiente
operation:transaction.create failure_reason:insufficient_stock

# Erros de pagamento por usuário (hasheado)
operation:transaction.create status:error @user_id_hash:abc123

# Requisições lentas
@duration_ms:>1000

# Transações completadas com sucesso
operation:transaction.create transaction_stage:completed status:success

# Erros de validação
error_category:business_logic error_type:validation_error
```

---

## 📚 Recursos Adicionais

- [Datadog Log Management Best Practices](https://docs.datadoghq.com/logs/guide/)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
- [GDPR Compliance for Logging](https://gdpr.eu/)

---

## 💡 Conclusão

**Logs bem escritos são:**
- 📝 Estruturados e consistentes
- 🔒 Seguros (sem PII)
- 🎯 Contextuais e significativos
- 🔗 Correlacionados com traces
- 🎓 Educativos para toda a equipe

**Lembre-se:** Logs não são apenas para quando algo dá errado - eles contam a história do seu sistema!

