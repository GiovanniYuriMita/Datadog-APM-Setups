# 📚 Referência Completa de Campos de Contexto

Todos os campos disponíveis nos logs JSON, organizados por categoria.

---

## 🏷️ Campos Padrão Datadog APM

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `dd.service` | string | Nome do serviço | `chofs-api` |
| `dd.env` | string | Ambiente | `chofs`, `production` |
| `dd.version` | string | Versão da aplicação | `20241217-1149` |
| `dd.trace_id` | string | ID do trace APM | `68f14c8400000000019e5d5e762b65f6` |
| `dd.span_id` | string | ID do span atual | `6463498129710942941` |

**Uso:** Correlação automática entre logs e APM traces

---

## 🎯 Campos de Operação

| Campo | Tipo | Descrição | Valores Possíveis |
|-------|------|-----------|-------------------|
| `operation` | string | Tipo de operação | `transaction.create`, `user.fetch`, `product.list` |
| `transaction_stage` | string | Etapa da transação | `initiated`, `validation`, `inventory_check`, `payment_processing`, `completed` |
| `status` | string | Status da operação | `success`, `error` |

**Query:** `@operation:transaction.create @transaction_stage:completed`

---

## 🔐 Campos de Segurança (SEM PII!)

| Campo | Tipo | Descrição | Exemplo | ⚠️ PII? |
|-------|------|-----------|---------|---------|
| `user_id_hash` | string | Hash do user ID | `a1b2c3d4e5f6g7h8` | ❌ Não |
| `session.id` | string | Session ID (truncado) | `session_17291046` | ❌ Não |

**✅ NUNCA logue:** `user_id`, `email`, `cpf`, `phone`, `address`, `ip_address`

---

## 💳 Campos de Pagamento (SEM dados sensíveis!)

| Campo | Tipo | Descrição | Valores Possíveis |
|-------|------|-----------|-------------------|
| `payment.method` | string | Método de pagamento | `credit_card`, `pix`, `invoice`, `debit_card` |
| `payment.amount` | float | Valor total | `59.98` |
| `payment.currency` | string | Moeda | `BRL`, `USD`, `EUR` |
| `payment.requires_3ds` | boolean | Requer autenticação 3D Secure | `true`, `false` |
| `payment.installments` | integer | Número de parcelas | `1`, `3`, `12` |

**Query:** `@payment.method:pix @payment.amount:>1000`

**✅ NUNCA logue:** `card_number`, `cvv`, `bank_account`, `pix_key`

---

## 📍 Campos de Geolocalização (SEM IP!)

| Campo | Tipo | Descrição | Valores |
|-------|------|-----------|---------|
| `geo.country` | string | Código do país | `BR`, `US`, `MX` |
| `geo.city` | string | Cidade | `São Paulo`, `New York` |
| `geo.region` | string | Estado/Região | `SP`, `NY`, `CA` |

**Query:** `@geo.country:BR @geo.city:"São Paulo"`

**✅ NUNCA logue:** `ip_address` completo (PII em GDPR/LGPD)

**Nota:** Use biblioteca GeoIP em produção (MaxMind, IP2Location)

---

## 📱 Campos de Device

| Campo | Tipo | Descrição | Valores |
|-------|------|-----------|---------|
| `device.type` | string | Tipo de device | `desktop`, `mobile`, `tablet` |
| `device.os` | string | Sistema operacional | `windows`, `macos`, `ios`, `android`, `linux` |
| `device.browser` | string | Navegador | `chrome`, `safari`, `firefox`, `edge` |

**Query:** `@device.type:mobile @device.os:ios`

**Uso:** Identificar bugs específicos de plataforma

---

## 💼 Campos de Negócio (User Metrics)

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `user.account_type` | string | Tipo de conta | `basic`, `premium`, `enterprise` |
| `user.total_transactions` | integer | Total de transações históricas | `42` |
| `user.lifetime_value` | float | Valor total gasto | `5420.50` |
| `user.is_vip` | boolean | Se é cliente VIP (LTV > 10k) | `true`, `false` |
| `user.account_age_days` | integer | Idade da conta em dias | `274` |

**Query:** `@user.is_vip:true @operation:transaction.create`

**Uso:** Segmentação, priorização de suporte, personalização

---

## 📦 Campos de Inventário

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `inventory.product_sku` | string | SKU do produto | `LAP-2024-001` |
| `inventory.category` | string | Categoria | `electronics`, `accessories` |
| `inventory.stock_before` | integer | Estoque antes da transação | `100` |
| `inventory.stock_after` | integer | Estoque após a transação | `98` |
| `inventory.needs_restock` | boolean | Precisa reposição | `true`, `false` |
| `inventory.restock_threshold` | integer | Threshold de reposição | `20` |
| `inventory.vendor` | string | Fornecedor | `Dell`, `Logitech` |

**Query:** `@inventory.needs_restock:true`

**Uso:** Gestão de estoque, alertas de reposição

---

## ⚠️ Campos de Risco (Fraud Detection)

| Campo | Tipo | Descrição | Range |
|-------|------|-----------|-------|
| `risk.score` | integer | Score de risco | `0-100` |
| `risk.level` | string | Nível de risco | `low`, `medium`, `high` |
| `risk.requires_review` | boolean | Requer revisão manual | `true`, `false` |

**Query:** `@risk.level:high @risk.requires_review:true`

**Uso:** Fraud detection, compliance, revisão manual

**✅ NUNCA logue:** `risk_factors` específicos (fraudadores aprenderiam o sistema)

---

## ⚡ Campos de Performance

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `performance.duration_ms` | float | Duração em milissegundos | `12.45` |
| `performance.is_slow` | boolean | Operação lenta (> 1s) | `true`, `false` |
| `performance.is_timeout_risk` | boolean | Risco de timeout (> 5s) | `true`, `false` |

**Query:** `@performance.is_slow:true @operation:transaction.create`

**Uso:** SLO monitoring, otimização, capacity planning

---

## 🔍 Campos de Session

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `session.id` | string | ID da sessão (truncado) | `session_17291046` |
| `session.referrer` | string | De onde veio | `direct`, `google.com`, `/products` |

**Query:** `@session.id:session_17291046`

**Uso:** Rastrear jornada do usuário, funnel analysis

---

## 🚨 Campos de Erro (Padrão Datadog)

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `error.type` | string | Tipo/classe do erro | `ValueError`, `TimeoutError` |
| `error.message` | string | Mensagem do erro | `Invalid input parameters` |
| `error.stack` | string | Stack trace completo | `Traceback (most recent call last)...` |
| `error_category` | string | Categoria customizada | `business_logic`, `database`, `external_api` |

**Query:** `@error.type:TimeoutError @error_category:external_api`

**Uso:** Error tracking, troubleshooting, alertas

---

## 📦 Campos de Produto

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| `product_id` | string | ID do produto | `prod_001` |
| `product_name` | string | Nome do produto | `Laptop` |
| `quantity` | integer | Quantidade | `2` |
| `total_amount` | float | Valor total | `1999.98` |

---

## ✅ Campos de Resultado

| Campo | Tipo | Descrição | Valores |
|-------|------|-----------|---------|
| `failure_reason` | string | Razão da falha | `insufficient_stock`, `insufficient_funds`, `user_not_found` |
| `transaction_id` | string | ID da transação | `txn_1729104628925_5432` |
| `remaining_balance` | float | Saldo restante | `940.02` |
| `remaining_stock` | integer | Estoque restante | `98` |

---

## 🎯 Queries Úteis por Caso de Uso

### Troubleshooting
```
# Transação específica
@transaction_id:txn_1729104628925_5432

# Falhas em stage específico
@transaction_stage:payment_processing @status:error

# Erros de um tipo
@error.type:TimeoutError
```

### Business Intelligence
```
# VIPs comprando
@user.is_vip:true @status:success

# Compras por região
@geo.country:BR @status:success

# Métodos de pagamento preferidos
@payment.method:*
```

### Fraud Detection
```
# Transações de alto risco
@risk.level:high

# Requer revisão
@risk.requires_review:true
```

### Performance Monitoring
```
# Operações lentas
@performance.is_slow:true

# Por região
@performance.duration_ms:>1000 @geo.country:BR
```

### Inventory Management
```
# Produtos precisando restock
@inventory.needs_restock:true

# Por vendor
@inventory.vendor:Dell @inventory.stock_after:<10
```

### Regional Analysis
```
# Problemas no Brasil
@geo.country:BR @status:error

# Transações por cidade
@geo.city:"São Paulo" @status:success
```

### Device Issues
```
# Problemas mobile
@device.type:mobile @error.type:*

# iOS específico
@device.os:ios @status:error
```

### Customer Segmentation
```
# Enterprise customers
@user.account_type:enterprise

# New customers (< 30 dias)
@user.account_age_days:<30

# High LTV
@user.lifetime_value:>10000
```

---

## 📊 Dashboards Sugeridos

### 1. Visão Geral de Negócio
- Total de transações (count)
- Revenue total (`sum(@total_amount)`)
- Taxa de sucesso (`status:success` vs total)
- Top produtos (`top 10 @product_id`)

### 2. Performance Dashboard
- P50, P95, P99 de `@performance.duration_ms`
- Operações lentas por endpoint
- Timeout risks

### 3. Fraud Monitoring
- Distribuição de `@risk.level`
- Transações `@risk.requires_review:true`
- Por região (`@geo.country`)

### 4. Inventory Health
- Produtos `@inventory.needs_restock:true`
- Stock levels por categoria
- Por vendor

### 5. Regional Performance
- Transações por país
- Latência por região
- Métodos de pagamento por país

### 6. Customer Insights
- VIP transactions
- LTV distribution
- Account type breakdown
- New vs returning customers

---

## ⚡ Métricas Customizadas

Crie métricas a partir dos logs:

```
# Revenue por hora
sum(@total_amount) by @timestamp

# Conversão por país
count(@status:success) / count(*) by @geo.country

# Fraud rate
count(@risk.level:high) / count(@operation:transaction.create)

# Performance por device
avg(@performance.duration_ms) by @device.type

# Restock rate
count(@inventory.needs_restock:true) / count(@inventory.product_sku:*)
```

---

## ✅ Resumo

**~40 campos de contexto** disponíveis em cada log relevante:

- ✅ 5 campos Datadog APM (trace correlation)
- ✅ 8 campos de pagamento
- ✅ 3 campos de geo
- ✅ 3 campos de device
- ✅ 5 campos de business metrics
- ✅ 7 campos de inventário
- ✅ 3 campos de risco
- ✅ 3 campos de performance
- ✅ 2 campos de session
- ✅ 4+ campos de erro (quando aplicável)

**Tudo isso mantendo:**
- ✅ PII protegido
- ✅ Compliance (GDPR, LGPD)
- ✅ Dados sensíveis mascarados/hasheados
- ✅ Performance otimizada

---

**Contexto rico sem comprometer privacidade! 🎉**

