# Estrutura do Projeto - Guia de Demonstração

Este documento explica a organização modular do código e qual arquivo demonstra cada conceito de logging.

## 📁 Estrutura de Diretórios

```
app/
├── app.py                      # Arquivo principal (orquestrador)
├── config.py                   # Configurações centralizadas
├── logging_config.py           # Setup de logging com Datadog
│
├── utils/                      # Utilitários reutilizáveis
│   ├── __init__.py
│   ├── security.py             # ⭐ Proteção de PII
│   └── decorators.py           # ⭐ Request logging automático
│
├── models/                     # Camada de dados
│   ├── __init__.py
│   └── data.py                 # Mock data (users, products, transactions)
│
└── routes/                     # Endpoints da API
    ├── __init__.py
    ├── home.py                 # Endpoint raiz (documentação)
    ├── health.py               # ⭐ DEBUG logging
    ├── users.py                # ⭐ PII protection
    ├── products.py             # Logging básico
    ├── transactions.py         # ⭐⭐⭐ MAIS IMPORTANTE!
    ├── analytics.py            # Logging de queries
    └── errors.py               # ⭐ Error handling
```

---

## 🎯 Arquivos por Conceito de Logging

### 1. **Proteção de PII** 🔒

**Arquivo:** `utils/security.py`

Demonstra:
- ✅ Mascaramento de dados sensíveis (emails, telefones)
- ✅ Hashing de identificadores de usuários
- ✅ Como nunca expor PII em logs

**Funções principais:**
```python
mask_sensitive_data(value, visible_chars=4)
hash_user_identifier(user_id)
```

**Uso em:** `routes/users.py`

---

### 2. **Request Tracking Automático** 📊

**Arquivo:** `utils/decorators.py`

Demonstra:
- ✅ Logging automático de todas as requisições
- ✅ Cálculo de duração (performance)
- ✅ Geração de request_id para rastreamento
- ✅ Error handling transparente

**Decorator:**
```python
@log_request_context()
def my_endpoint():
    pass
```

**Logs gerados automaticamente:**
1. Request iniciado (INFO)
2. Request completado + duração (INFO)
3. Request falhou + erro (ERROR)

---

### 3. **Health Checks** 🏥

**Arquivo:** `routes/health.py`

Demonstra:
- ✅ Uso de nível DEBUG para health checks
- ✅ Como evitar poluição de logs

**Conceito chave:**
```python
# ❌ RUIM: logger.info("Health check")  # Polui logs!
# ✅ BOM: logger.debug("Health check")  # Só quando necessário
```

---

### 4. **Transaction Stages (Auditoria)** 💰

**Arquivo:** `routes/transactions.py` ⭐⭐⭐

**ESTE É O ARQUIVO MAIS IMPORTANTE PARA DEMONSTRAÇÃO!**

Demonstra:
- ✅ Logging de cada etapa de uma transação
- ✅ Validações com contexto específico
- ✅ Auditoria completa de operações críticas
- ✅ Diferenciação entre erros esperados (WARNING) e inesperados (ERROR)

**Stages logados:**
1. Validação de entrada
2. Transação iniciada
3. Validação de usuário
4. Validação de produto
5. Verificação de estoque
6. Verificação de saldo
7. Processamento
8. Transação completada

**Exemplo de log:**
```python
logger.info(
    "Transaction initiated",
    extra={
        'operation': 'transaction.create',
        'transaction_stage': 'initiated',
        'user_id_hash': '...',  # Hash, não ID real!
        'product_id': 'prod_001',
        'quantity': 2
    }
)
```

---

### 5. **Error Handling e Categorização** ⚠️

**Arquivo:** `routes/errors.py`

Demonstra:
- ✅ Diferentes tipos de erros e como logar cada um
- ✅ Quando usar WARNING vs ERROR
- ✅ Quando incluir stack trace (exc_info=True)
- ✅ Categorização de erros

**Tipos demonstrados:**

#### Erro de Validação (Erro de Negócio)
```python
except ValueError as e:
    logger.warning(  # WARNING, não ERROR!
        f"Validation error: {str(e)}",
        extra={
            'error_type': 'validation_error',
            'error_category': 'business_logic'
        }
        # Sem exc_info=True (erro esperado)
    )
```

#### Erro Técnico/Inesperado
```python
except Exception as e:
    logger.error(
        f"Unexpected error: {str(e)}",
        extra={
            'error_type': type(e).__name__,
            'error_category': 'unexpected'
        },
        exc_info=True  # Inclui stack trace!
    )
```

---

### 6. **PII Protection em Ação** 👤

**Arquivo:** `routes/users.py`

Demonstra:
- ✅ Hashing de user_id em logs
- ✅ Mascaramento de email
- ✅ Uso de booleanos ao invés de valores sensíveis

**Exemplo:**
```python
logger.info(
    "User profile fetched",
    extra={
        'user_id_hash': hash_user_identifier(user_id),  # Hash
        'has_balance': user['balance'] > 0  # Boolean, não valor
    }
)
# ❌ NUNCA: 'email': user['email']
# ❌ NUNCA: 'balance': user['balance']
```

---

### 7. **Structured Logging** 📋

**Todos os arquivos demonstram**, mas especialmente:
- `routes/transactions.py`
- `routes/users.py`
- `routes/analytics.py`

**Conceito:**
```python
# ❌ RUIM: Logging não estruturado
logger.info(f"Transaction {txn_id} completed for user {user_id}")

# ✅ BOM: Logging estruturado
logger.info(
    "Transaction completed",
    extra={
        'operation': 'transaction.create',
        'transaction_id': txn_id,
        'user_id_hash': hash_user_identifier(user_id),
        'status': 'success'
    }
)
```

**Benefícios:**
- Fácil filtrar no Datadog: `operation:transaction.create status:success`
- Criação de dashboards e alertas
- Agregações e métricas

---

### 8. **Log-Trace Correlation** 🔗

**Arquivo:** `logging_config.py`

Demonstra:
- ✅ Configuração de formato para incluir trace_id e span_id
- ✅ Correlação automática entre logs e APM

**Formato:**
```python
LOG_FORMAT = (
    '%(asctime)s %(levelname)s [%(name)s] '
    '[dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
    '- %(message)s'
)
```

**Resultado no Datadog:**
- Clique em um log → vá para o trace
- Clique em um trace → veja os logs relacionados

---

### 9. **Custom Spans** 🎯

**Usado em:** Todos os endpoints em `routes/`

**Exemplo:**
```python
from ddtrace import tracer

with tracer.trace("transaction.create", service="chofs-api") as span:
    span.set_tag("user_id_hash", user_hash)
    span.set_tag("product_id", product_id)
    
    # Seu código aqui
    # Logs dentro deste bloco são automaticamente correlacionados
```

---

## 🎓 Roteiro de Demonstração Sugerido

Para demonstrar aos desenvolvedores, siga esta ordem:

### 1. Conceitos Básicos (15 min)
1. `logging_config.py` - Setup e correlação com APM
2. `utils/security.py` - Proteção de PII
3. `utils/decorators.py` - Request tracking automático

### 2. Exemplos Práticos (30 min)
4. `routes/health.py` - DEBUG logging
5. `routes/users.py` - PII protection em ação
6. **`routes/transactions.py`** ⭐ - Transaction stages (FOCO AQUI!)
7. `routes/errors.py` - Error handling e categorização

### 3. Demonstração Prática (15 min)
8. Executar `load_test.py`
9. Ver logs no Datadog
10. Ver traces no APM
11. Demonstrar correlação log-trace

---

## 📝 Pontos-Chave para Enfatizar

### ✅ O que fazer:
1. **Sempre use structured logging** (`extra={}`)
2. **Proteja PII** (hash, mask)
3. **Logue cada stage** de operações críticas
4. **Use níveis apropriados** (DEBUG, INFO, WARNING, ERROR)
5. **Inclua contexto** relevante
6. **Use exc_info=True** para erros inesperados

### ❌ O que NÃO fazer:
1. ❌ Logar PII em texto claro
2. ❌ Usar INFO para health checks (poluição)
3. ❌ Logs sem contexto ("Error occurred")
4. ❌ Usar ERROR para erros esperados (validação)
5. ❌ Esquecer de logar operações críticas
6. ❌ Concatenar strings ao invés de structured logging

---

## 🔍 Queries Úteis no Datadog

Após demonstrar, mostre estas queries:

```
# Todas as transações
operation:transaction.create

# Transações que falharam
operation:transaction.create status:error

# Transações por stage
operation:transaction.create transaction_stage:payment_validation

# Erros de estoque insuficiente
failure_reason:insufficient_stock

# Erros por tipo
error_type:ValueError

# Requisições lentas
@duration_ms:>1000
```

---

## 🚀 Quick Start para Demonstração

```bash
# 1. Inicie a aplicação
docker-compose up --build

# 2. Em outro terminal, gere carga
python load_test.py --rate 2

# 3. Abra Datadog e mostre:
#    - Logs com estrutura
#    - Correlação com traces
#    - Filtros e queries
```

---

## 💡 Mensagens-Chave

1. **Logs são a história do seu sistema** - conte uma boa história!
2. **Proteja sempre os dados dos usuários** - PII é responsabilidade
3. **Contexto é rei** - logs sem contexto são inúteis
4. **Estruture seus logs** - facilita análise e troubleshooting
5. **Correlacione com APM** - visibilidade completa

