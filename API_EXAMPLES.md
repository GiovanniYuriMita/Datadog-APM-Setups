# 🔌 Exemplos de API - Comandos Prontos

Use estes comandos para testar rapidamente todos os endpoints da API.

---

## 🏠 Home / Documentação

```bash
curl http://localhost:8080/
```

**O que demonstra:** Endpoint de documentação básico

---

## 🏥 Health Check

```bash
curl http://localhost:8080/health
```

**O que demonstra:** 
- Uso de `logger.debug()` ao invés de `logger.info()`
- Como evitar poluição de logs com health checks frequentes

---

## 👤 User Endpoints

### Buscar Usuário (Sucesso)
```bash
curl http://localhost:8080/api/user/user_001
```

**O que demonstra:**
- Hashing de user_id: `user_id_hash`
- Mascaramento de email na resposta
- Logging com contexto estruturado
- Custom span no Datadog APM

### Buscar Usuário (Não Encontrado)
```bash
curl http://localhost:8080/api/user/user_999
```

**O que demonstra:**
- Uso de `logger.warning()` para casos esperados
- Log com `failure_reason`
- HTTP 404 response

---

## 📦 Product Endpoints

### Listar Produtos
```bash
curl http://localhost:8080/api/products
```

**O que demonstra:**
- Logging simples de operações de leitura
- Inclusão de contadores (`product_count`)
- Custom span com tags

---

## 💳 Transaction Endpoints

### Transação Bem-Sucedida
```bash
curl -X POST http://localhost:8080/api/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "product_id": "prod_002",
    "quantity": 1
  }'
```

**O que demonstra:**
- ⭐ **MAIS IMPORTANTE!** Transaction stages completos
- Logging de auditoria em cada etapa
- Hashing de user_id em logs
- Tags no APM span

### Transação - Campos Faltando
```bash
curl -X POST http://localhost:8080/api/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001"
  }'
```

**O que demonstra:**
- Validação de entrada
- Logging de `missing_fields`
- WARNING para erro de validação

### Transação - Usuário Não Encontrado
```bash
curl -X POST http://localhost:8080/api/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_999",
    "product_id": "prod_001",
    "quantity": 1
  }'
```

**O que demonstra:**
- Log no stage: `user_validation`
- `failure_reason: user_not_found`

### Transação - Produto Não Encontrado
```bash
curl -X POST http://localhost:8080/api/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "product_id": "prod_999",
    "quantity": 1
  }'
```

**O que demonstra:**
- Log no stage: `product_validation`
- `failure_reason: product_not_found`

### Transação - Estoque Insuficiente
```bash
curl -X POST http://localhost:8080/api/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "product_id": "prod_001",
    "quantity": 100
  }'
```

**O que demonstra:**
- ⭐ **ÓTIMO EXEMPLO!** Log com contexto completo
- Log no stage: `inventory_check`
- Inclui `requested_quantity` vs `available_stock`
- `failure_reason: insufficient_stock`

### Transação - Saldo Insuficiente
```bash
curl -X POST http://localhost:8080/api/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_003",
    "product_id": "prod_001",
    "quantity": 1
  }'
```

**O que demonstra:**
- Log no stage: `payment_validation`
- `failure_reason: insufficient_funds`
- NÃO loga o saldo do usuário (PII protection)

---

## 📊 Analytics Endpoints

### Ver Analytics de Transações
```bash
curl http://localhost:8080/api/analytics/transactions
```

**O que demonstra:**
- Logging de queries de analytics
- Inclusão de métricas calculadas
- Tags no span para métricas

---

## ⚠️ Error Simulation Endpoints

### Erro de Validação (ValueError)
```bash
curl "http://localhost:8080/api/error/simulate?type=validation"
```

**O que demonstra:**
- ⭐ Uso de `logger.warning()` para erros de validação
- `error_category: business_logic`
- SEM `exc_info=True` (não precisa stack trace)

### Erro Aritmético (ZeroDivisionError)
```bash
curl "http://localhost:8080/api/error/simulate?type=division"
```

**O que demonstra:**
- Uso de `logger.error()` para erros técnicos
- `error_category: arithmetic_error`
- COM `exc_info=True` (stack trace completo)

### Erro Genérico
```bash
curl "http://localhost:8080/api/error/simulate?type=generic"
```

**O que demonstra:**
- ⭐ Tratamento de erros inesperados
- `error_category: unexpected`
- Stack trace completo
- Máximo contexto possível

---

## 🔄 Sequência de Testes Completa

Execute todos os comandos em sequência para gerar logs variados:

```bash
#!/bin/bash

echo "1. Health Check"
curl http://localhost:8080/health
sleep 1

echo -e "\n2. Buscar usuário (sucesso)"
curl http://localhost:8080/api/user/user_001
sleep 1

echo -e "\n3. Buscar usuário (não encontrado)"
curl http://localhost:8080/api/user/user_999
sleep 1

echo -e "\n4. Listar produtos"
curl http://localhost:8080/api/products
sleep 1

echo -e "\n5. Transação bem-sucedida"
curl -X POST http://localhost:8080/api/transaction \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_002","product_id":"prod_002","quantity":2}'
sleep 1

echo -e "\n6. Transação - estoque insuficiente"
curl -X POST http://localhost:8080/api/transaction \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_001","product_id":"prod_001","quantity":100}'
sleep 1

echo -e "\n7. Erro de validação"
curl "http://localhost:8080/api/error/simulate?type=validation"
sleep 1

echo -e "\n8. Erro técnico"
curl "http://localhost:8080/api/error/simulate?type=division"
sleep 1

echo -e "\n9. Analytics"
curl http://localhost:8080/api/analytics/transactions

echo -e "\n\nTestes completos! Agora veja os logs no Datadog."
```

Salve como `test_sequence.sh` e execute:
```bash
chmod +x test_sequence.sh
./test_sequence.sh
```

---

## 📋 Queries do Datadog para Cada Cenário

Após executar os comandos, use estas queries no Datadog:

### Ver todos os logs de transações
```
service:chofs-api operation:transaction.create
```

### Ver apenas transações falhadas
```
service:chofs-api operation:transaction.create status:error
```

### Ver falhas por estoque insuficiente
```
service:chofs-api failure_reason:insufficient_stock
```

### Ver por stage específico
```
service:chofs-api transaction_stage:inventory_check
```

### Ver todos os tipos de erro
```
service:chofs-api error_type:* -error_type:null
```

### Ver erros de validação (WARNING)
```
service:chofs-api status:warn error_category:business_logic
```

### Ver erros técnicos (ERROR)
```
service:chofs-api status:error error_category:*
```

### Ver operações por usuário (hashed)
```
service:chofs-api user_id_hash:* -user_id_hash:null
```

### Ver requisições lentas (>500ms)
```
service:chofs-api @duration_ms:>500
```

---

## 🎯 Cenários para Demonstração

### Cenário 1: Troubleshooting de Transação Falhada
**Objetivo:** Demonstrar como logs ajudam a identificar exatamente onde e por que falhou

1. Execute transação com estoque insuficiente
2. No Datadog, filtre: `operation:transaction.create failure_reason:insufficient_stock`
3. Mostre:
   - Stage onde falhou (`inventory_check`)
   - Quantidade solicitada vs disponível
   - user_id_hash para rastrear
   - Correlação com trace no APM

### Cenário 2: Rastreamento de Usuário (sem expor PII)
**Objetivo:** Demonstrar como rastrear ações de um usuário sem expor identidade

1. Execute várias operações com `user_001`
2. No Datadog, pegue o `user_id_hash` de um log
3. Filtre: `user_id_hash:HASH_AQUI`
4. Mostre todas as operações daquele usuário
5. Enfatize: "Não sabemos quem é, mas sabemos o que fez"

### Cenário 3: Análise de Erros
**Objetivo:** Demonstrar categorização de erros

1. Execute vários tipos de erro
2. No Datadog, crie facets:
   - `error_category`
   - `error_type`
3. Mostre dashboard com:
   - Erros por categoria
   - Erros por tipo
   - Tendência de erros

---

## 💡 Dicas para Demonstração

### 1. Use jq para Pretty Print
```bash
curl http://localhost:8080/api/products | jq
```

### 2. Adicione Request ID Customizado
```bash
curl -H "X-Request-ID: DEMO-12345" http://localhost:8080/api/user/user_001
```

Depois filtre no Datadog: `request_id:DEMO-12345`

### 3. Execute Múltiplas Vezes
```bash
for i in {1..10}; do
  curl -X POST http://localhost:8080/api/transaction \
    -H "Content-Type: application/json" \
    -d '{"user_id":"user_001","product_id":"prod_002","quantity":1}'
  sleep 1
done
```

Gera volume de logs para mostrar agregações.

---

## 🎓 Exercício para Desenvolvedores

**Desafio:** Implemente logging similar em um endpoint do seu projeto

**Checklist:**
- [ ] Structured logging com `extra={}`
- [ ] PII protegido (hash ou mask)
- [ ] Transaction stages se aplicável
- [ ] Níveis de log apropriados
- [ ] Error handling com contexto
- [ ] Custom spans no APM

**Compartilhe o before/after com o time!**

---

## 📞 Troubleshooting

### API não está respondendo?
```bash
# Verifique se está rodando
docker-compose ps

# Veja os logs
docker-compose logs python-app

# Reinicie
docker-compose restart python-app
```

### Logs não aparecem no Datadog?
```bash
# Verifique API key
docker-compose exec datadog-agent agent status

# Verifique connectivity
docker-compose logs datadog-agent | grep -i error
```

---

**Happy testing! 🚀**

