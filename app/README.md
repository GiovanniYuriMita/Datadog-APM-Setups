# 📂 Diretório `/app` - Estrutura Modular

Esta pasta contém a aplicação Flask organizada de forma modular para facilitar a demonstração de logging best practices.

---

## 🗂️ Organização

```
app/
├── app.py                  ⭐ Arquivo principal - comece aqui!
├── config.py               Configurações centralizadas
├── logging_config.py       Setup de logging com Datadog APM
├── README.md               ← Você está aqui
├── PROJECT_STRUCTURE.md    📖 Guia completo de demonstração
│
├── utils/                  🔧 Utilitários reutilizáveis
│   ├── security.py         Proteção de PII (masking, hashing)
│   └── decorators.py       Request logging automático
│
├── models/                 💾 Camada de dados
│   └── data.py             Mock database (users, products, transactions)
│
└── routes/                 🛣️ Endpoints da API
    ├── home.py             Welcome endpoint
    ├── health.py           DEBUG logging
    ├── users.py            PII protection
    ├── products.py         Basic logging
    ├── transactions.py     ⭐⭐⭐ MAIS IMPORTANTE!
    ├── analytics.py        Query logging
    └── errors.py           Error handling
```

---

## 🎯 Ordem Recomendada de Leitura

### Para Entender a Aplicação:
1. `app.py` - Veja como tudo é orquestrado
2. `config.py` - Configurações
3. `logging_config.py` - Setup de logging
4. `models/data.py` - Dados mock

### Para Aprender Logging Best Practices:
1. **`utils/security.py`** - Como proteger PII
2. **`utils/decorators.py`** - Request tracking automático
3. **`routes/transactions.py`** - ⭐ FOCO PRINCIPAL! Transaction stages
4. **`routes/errors.py`** - Error handling e categorização
5. **`routes/users.py`** - PII em ação
6. **`routes/health.py`** - DEBUG logging

---

## 📖 Documentação Detalhada

- **`PROJECT_STRUCTURE.md`** - Guia completo de cada arquivo e conceito
- **`../DEMO_GUIDE.md`** - Roteiro de demonstração passo a passo
- **`../API_EXAMPLES.md`** - Comandos curl prontos para teste
- **`../LOGGING_BEST_PRACTICES.md`** - Documentação completa

---

## 🔑 Conceitos-Chave por Arquivo

### `utils/security.py` 🔒
**Conceito:** Proteção de PII

```python
# Masking - mostra parcialmente
mask_sensitive_data("john@example.com", 4)
# → "john***************"

# Hashing - rastreável mas não identificável
hash_user_identifier("user_12345")
# → "a1b2c3d4e5f6g7h8"
```

**Quando usar:**
- Masking: UIs, respostas de API
- Hashing: Logs, analytics

---

### `utils/decorators.py` 📊
**Conceito:** Request tracking automático

```python
@log_request_context()
def my_endpoint():
    return {"status": "ok"}
```

**Gera automaticamente:**
- Log de início (com metadata)
- Log de fim (com duração)
- Log de erro (com stack trace)

---

### `routes/health.py` 🏥
**Conceito:** Evitar poluição de logs

```python
# ❌ RUIM
logger.info("Health check")  # Chamado 100s de vezes/min!

# ✅ BOM
logger.debug("Health check")  # Só quando necessário
```

---

### `routes/users.py` 👤
**Conceito:** PII em ação

```python
logger.info(
    "User fetched",
    extra={
        'user_id_hash': hash_user_identifier(user_id),  # Hash!
        'has_balance': user['balance'] > 0  # Boolean, não valor
    }
)
# ❌ NUNCA logue: email, balance real, nome completo
```

---

### `routes/transactions.py` 💰
**Conceito:** Transaction stages (auditoria completa)

**⭐ ARQUIVO MAIS IMPORTANTE PARA DEMONSTRAÇÃO!**

**8 Stages Logados:**
1. Validação de entrada
2. Transação iniciada
3. Validação de usuário
4. Validação de produto
5. Verificação de estoque ← **Exemplo perfeito!**
6. Verificação de saldo
7. Processamento
8. Transação completada

**Exemplo de log completo:**
```python
logger.warning(
    "Transaction failed - insufficient stock",
    extra={
        'operation': 'transaction.create',
        'transaction_stage': 'inventory_check',  # Onde?
        'requested_quantity': 10,  # O que pediu?
        'available_stock': 5,      # O que tinha?
        'failure_reason': 'insufficient_stock',  # Por quê?
        'user_id_hash': hash_user_identifier(user_id),  # Quem?
        'product_id': 'prod_001'   # Qual produto?
    }
)
```

**Query no Datadog:**
```
operation:transaction.create 
transaction_stage:inventory_check 
failure_reason:insufficient_stock
```

---

### `routes/errors.py` ⚠️
**Conceito:** Categorização de erros

**3 Tipos:**

#### 1. Validação (Erro de Negócio)
```python
except ValueError as e:
    logger.warning(  # WARNING!
        f"Validation error: {str(e)}",
        extra={'error_category': 'business_logic'}
    )
    # Sem exc_info (não precisa stack trace)
```

#### 2. Erro Técnico
```python
except ZeroDivisionError as e:
    logger.error(  # ERROR!
        "Division by zero",
        extra={'error_category': 'arithmetic_error'},
        exc_info=True  # Com stack trace!
    )
```

#### 3. Erro Inesperado
```python
except Exception as e:
    logger.error(
        f"Unexpected: {str(e)}",
        extra={'error_category': 'unexpected'},
        exc_info=True  # SEMPRE!
    )
```

---

## 🚀 Como Executar

```bash
# Opção 1: Docker (recomendado)
cd ..
docker-compose up --build

# Opção 2: Local
cd app
pip install -r ../requirements.txt
export DD_SERVICE=chofs-api
export DD_ENV=development
python app.py
```

---

## 🧪 Como Testar

```bash
# Teste rápido
cd ..
./test_api.sh

# Load testing
python load_test.py --rate 2

# Teste manual
curl http://localhost:8080/api/user/user_001
```

---

## 📊 Padrões de Log

### ✅ Structured Logging
```python
# BOM
logger.info(
    "Operation completed",
    extra={
        'operation': 'user.fetch',
        'user_id_hash': 'abc123',
        'duration_ms': 45.2
    }
)

# RUIM
logger.info(f"User abc123 fetched in 45.2ms")
```

### ✅ Níveis Apropriados
```python
logger.debug()    # Development, health checks
logger.info()     # Operações normais
logger.warning()  # Erros esperados (validação, not found)
logger.error()    # Erros inesperados
```

### ✅ Contexto Completo
Sempre inclua:
- `operation` - qual operação?
- `*_stage` - em qual etapa? (se aplicável)
- `failure_reason` - por que falhou? (se falhou)
- `error_type` - tipo de erro? (se erro)
- IDs relevantes (hasheados!)

---

## 🎓 Exercício

**Escolha um arquivo e tente entender:**

1. Que conceito de logging ele demonstra?
2. Por que os logs estão estruturados daquela forma?
3. O que você pode aplicar no seu código?

**Arquivos sugeridos para estudo:**
- Iniciante: `routes/health.py`, `routes/products.py`
- Intermediário: `routes/users.py`, `routes/errors.py`
- Avançado: `routes/transactions.py`

---

## 💡 Dicas

1. **Comece pelo `app.py`** para entender o fluxo geral
2. **Leia `routes/transactions.py`** para ver logging completo
3. **Execute `test_api.sh`** para gerar logs
4. **Veja logs no Datadog** para correlacionar
5. **Compare com seu código atual** - o que pode melhorar?

---

## 📞 Precisa de Ajuda?

- 📖 Leia: `PROJECT_STRUCTURE.md`
- 🎓 Siga: `../DEMO_GUIDE.md`
- 💻 Teste: `../API_EXAMPLES.md`
- 📚 Aprenda: `../LOGGING_BEST_PRACTICES.md`

---

**Happy logging! 🚀**

