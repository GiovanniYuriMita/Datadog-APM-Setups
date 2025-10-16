# 🌟 Exemplo de Log com Contexto Rico

## 📊 Log Completo de Transação (JSON)

```json
{
  "timestamp": "2025-10-16T19:50:28.925Z",
  "severity": "INFO",
  "logger": "app.routes.transactions",
  "message": "Transaction completed successfully",
  
  "dd.service": "chofs-api",
  "dd.env": "chofs",
  "dd.version": "20241217-1149",
  "dd.trace_id": "68f14c8400000000019e5d5e762b65f6",
  "dd.span_id": "6463498129710942941",
  
  "operation": "transaction.create",
  "transaction_id": "txn_1729104628925_5432",
  "transaction_stage": "completed",
  "status": "success",
  
  "_comment_produto": "Informações do produto",
  "product_id": "prod_002",
  "product_name": "Mouse",
  "quantity": 2,
  "total_amount": 59.98,
  
  "_comment_usuario": "Informações do usuário (SEM PII!)",
  "user_id_hash": "a1b2c3d4e5f6g7h8",
  "user.account_type": "premium",
  "user.total_transactions": 43,
  "user.lifetime_value": 5480.48,
  "user.is_vip": false,
  "user.account_age_days": 274,
  
  "_comment_pagamento": "Contexto de pagamento (SEM dados sensíveis!)",
  "payment.method": "credit_card",
  "payment.amount": 59.98,
  "payment.currency": "BRL",
  "payment.requires_3ds": false,
  "payment.installments": 1,
  
  "_comment_inventario": "Métricas de inventário",
  "inventory.product_sku": "MOU-2024-002",
  "inventory.category": "accessories",
  "inventory.stock_before": 100,
  "inventory.stock_after": 98,
  "inventory.needs_restock": false,
  "inventory.restock_threshold": 20,
  "inventory.vendor": "Logitech",
  
  "_comment_risco": "Análise de risco (fraud detection)",
  "risk.score": 0,
  "risk.level": "low",
  "risk.requires_review": false,
  
  "_comment_geo": "Geolocalização (SEM IP completo!)",
  "geo.country": "BR",
  "geo.city": "São Paulo",
  "geo.region": "SP",
  
  "_comment_device": "Informações de device",
  "device.type": "desktop",
  "device.os": "macos",
  "device.browser": "chrome",
  
  "_comment_session": "Tracking de sessão",
  "session.id": "session_17291046",
  "session.referrer": "direct",
  
  "_comment_performance": "Métricas de performance",
  "performance.duration_ms": 12.45,
  "performance.is_slow": false,
  "performance.is_timeout_risk": false,
  
  "_comment_inventario_pos": "Estado pós-transação",
  "remaining_balance": 940.02,
  "remaining_stock": 98
}
```

---

## 🎯 Casos de Uso por Categoria

### 1. Troubleshooting

**Problema:** "Transação falhou às 14:30, preciso saber por quê"

**Query:**
```
@operation:transaction.create 
@timestamp:"2025-10-16T14:30:*" 
@status:error
```

**Contexto disponível:**
- ✅ Em qual stage falhou (`transaction_stage`)
- ✅ Por quê (`failure_reason`, `error.message`)
- ✅ De onde (`geo.city`, `geo.country`)
- ✅ Qual device (`device.type`, `device.os`)
- ✅ Quanto tempo levou (`performance.duration_ms`)

### 2. Fraud Detection

**Problema:** "Detectar padrões de fraude"

**Query:**
```
@operation:transaction.create 
@risk.level:high 
@risk.requires_review:true
```

**Contexto disponível:**
- ✅ Risk score calculado
- ✅ Geolocalização incomum
- ✅ Padrões de device
- ✅ Velocidade de transações
- ✅ Account age

### 3. Business Intelligence

**Problema:** "Qual o perfil de quem compra laptops?"

**Query:**
```
@product_id:prod_001 
@status:success
```

**Agregue por:**
- `@user.account_type` - Tipo de conta
- `@geo.country` - País
- `@payment.method` - Método de pagamento
- `@user.is_vip` - Se é VIP

### 4. Inventory Management

**Problema:** "Produtos precisando restock"

**Query:**
```
@inventory.needs_restock:true
```

**Contexto disponível:**
- ✅ SKU do produto
- ✅ Vendor
- ✅ Threshold de restock
- ✅ Estoque atual

### 5. Performance Monitoring

**Problema:** "Transações lentas"

**Query:**
```
@performance.is_slow:true
```

ou

```
@performance.duration_ms:>1000
```

**Correlacione com:**
- `@geo.country` - Problema regional?
- `@payment.method` - Gateway específico lento?
- `@product_id` - Produto específico?

### 6. Regional Analysis

**Problema:** "Problemas específicos do Brasil"

**Query:**
```
@geo.country:BR 
@status:error
```

**Análise:**
- Problemas de payment gateway regional
- Latência por região
- Produtos populares por região

### 7. Device Issues

**Problema:** "Bugs apenas no mobile"

**Query:**
```
@device.type:mobile 
@error.type:*
```

**Contexto:**
- `@device.os` - iOS vs Android
- `@device.browser` - Mobile Safari, Chrome Mobile

### 8. VIP Customer Monitoring

**Problema:** "Monitorar transações de VIPs"

**Query:**
```
@user.is_vip:true 
@operation:transaction.create
```

**Contexto:**
- `@user.lifetime_value` - Valor do cliente
- `@user.account_type` - Tipo de conta
- Prioridade de suporte

---

## 📋 Categorias de Contexto

### 🔐 Segurança (SEM PII!)
- `user_id_hash` - Hash do user ID
- `session.id` - Truncado
- Sem: email, nome, CPF, endereço

### 💳 Pagamento (SEM dados sensíveis!)
- `payment.method` - Tipo (credit_card, pix, invoice)
- `payment.currency` - Moeda
- `payment.installments` - Parcelamento
- `payment.requires_3ds` - Se precisa autenticação extra
- Sem: número de cartão, CVV, dados bancários

### 📍 Geolocalização (SEM IP!)
- `geo.country` - País (BR, US)
- `geo.city` - Cidade
- `geo.region` - Estado/Região
- Sem: IP completo (PII em GDPR/LGPD)

### 📱 Device
- `device.type` - desktop, mobile, tablet
- `device.os` - windows, macos, ios, android
- `device.browser` - chrome, safari, firefox

### 💼 Business Metrics
- `user.account_type` - basic, premium, enterprise
- `user.total_transactions` - Contagem histórica
- `user.lifetime_value` - Valor total do cliente
- `user.is_vip` - Boolean (LTV > threshold)
- `user.account_age_days` - Idade da conta

### 📦 Inventário
- `inventory.product_sku` - SKU do produto
- `inventory.category` - Categoria
- `inventory.stock_before/after` - Estoque
- `inventory.needs_restock` - Boolean
- `inventory.vendor` - Fornecedor

### ⚠️ Risco
- `risk.score` - 0-100
- `risk.level` - low, medium, high
- `risk.requires_review` - Boolean
- Sem: fatores específicos (informação sensível)

### ⚡ Performance
- `performance.duration_ms` - Duração da operação
- `performance.is_slow` - > 1000ms
- `performance.is_timeout_risk` - > 5000ms

### 🔍 Session
- `session.id` - Session tracking (truncado)
- `session.referrer` - De onde veio

---

## 🎓 Best Practices Demonstradas

### 1. Contexto Rico = Troubleshooting Rápido
Com um único log, você vê:
- ✅ O que aconteceu
- ✅ Por quê
- ✅ Onde (geo + stage)
- ✅ Quando (timestamp)
- ✅ Quem (user_id_hash)
- ✅ Como (device, método pagamento)
- ✅ Performance (duração)

### 2. Proteção de PII Mantida
Mesmo com contexto rico:
- ✅ User ID é hasheado
- ✅ IP não é logado
- ✅ Dados de pagamento protegidos
- ✅ Session ID truncado
- ✅ Compliance (GDPR, LGPD)

### 3. Analytics Poderoso
Faça análises complexas:
- Conversion rate por país
- Métodos de pagamento por tipo de conta
- Produtos por região
- Performance por device type

### 4. Alertas Inteligentes
Crie alertas específicos:
- VIPs com problemas
- Risk score alto
- Problemas regionais
- Performance degradada

---

## 🚀 Resultado

Um **único log** tem informação suficiente para:
- ✅ Troubleshooting completo
- ✅ Fraud detection
- ✅ Business intelligence
- ✅ Performance monitoring
- ✅ Regional analysis
- ✅ Customer segmentation

**Sem comprometer privacidade ou segurança!**

---

**Contexto Rico + PII Protection = Logging Perfeito! 🎉**

