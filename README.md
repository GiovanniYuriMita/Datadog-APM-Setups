# Datadog APM Logging Best Practices Demo 🚀

Uma aplicação demo completa demonstrando as **melhores práticas de logging** com integração ao Datadog APM. Este projeto foi criado para ensinar desenvolvedores como escrever logs significativos, contextuais e seguros.

## 📋 Características

- ✅ **API RESTful Flask** com múltiplos endpoints
- ✅ **Logging estruturado** com correlação APM/Trace
- ✅ **Proteção de PII** - mascaramento e hashing de dados sensíveis
- ✅ **Context-aware logging** - logs com contexto de negócio relevante
- ✅ **Error handling** exemplar com try/catch
- ✅ **Transaction tracking** com auditoria completa
- ✅ **Load testing scripts** (Python e Bash)
- ✅ **Documentação completa** de best practices

## 🎯 Objetivos de Aprendizado

Este projeto demonstra:

1. **Como correlacionar logs com traces do Datadog APM**
2. **Como proteger PII e dados sensíveis em logs**
3. **Como adicionar contexto de negócio aos logs**
4. **Quando usar cada nível de log (DEBUG, INFO, WARNING, ERROR)**
5. **Como fazer logging efetivo em try/catch blocks**
6. **Como rastrear transações e operações críticas**
7. **Como evitar anti-patterns comuns**

## 📁 Estrutura do Projeto

```
.
├── app/                            # Aplicação modular
│   ├── app.py                      # Arquivo principal (orquestrador)
│   ├── config.py                   # Configurações
│   ├── logging_config.py           # Setup de logging
│   ├── PROJECT_STRUCTURE.md        # 📖 Guia detalhado da estrutura
│   │
│   ├── utils/                      # Utilitários
│   │   ├── security.py             # ⭐ Proteção de PII
│   │   └── decorators.py           # ⭐ Request logging
│   │
│   ├── models/                     # Dados
│   │   └── data.py                 # Mock data
│   │
│   └── routes/                     # Endpoints (cada um demonstra conceitos específicos)
│       ├── home.py                 # Documentação
│       ├── health.py               # DEBUG logging
│       ├── users.py                # PII protection
│       ├── products.py             # Logging básico
│       ├── transactions.py         # ⭐⭐⭐ MAIS IMPORTANTE!
│       ├── analytics.py            # Query logging
│       └── errors.py               # Error handling
│
├── docker-compose.yaml             # Orquestração Docker
├── Dockerfile                      # Container da aplicação
├── load_test.py                    # Script de carga em Python
├── load_test.sh                    # Script de carga em Bash
├── requirements.txt                # Dependências Python
├── LOGGING_BEST_PRACTICES.md       # Documentação completa de best practices
├── LICENSE
└── README.md
```

**🎯 Arquivos Principais para Demonstração:**
1. `app/routes/transactions.py` - Logging de operações críticas, transaction stages
2. `app/routes/users.py` - Proteção de PII (hashing, masking)
3. `app/routes/errors.py` - Error handling e categorização
4. `app/utils/security.py` - Funções de proteção de dados
5. `app/utils/decorators.py` - Request tracking automático

📖 **Veja `app/PROJECT_STRUCTURE.md` para guia detalhado de cada arquivo!**

## 📚 Documentação Completa

Este projeto inclui documentação detalhada para diferentes finalidades:

| Documento | Propósito | Para Quem |
|-----------|-----------|-----------|
| **[DEMO_GUIDE.md](./DEMO_GUIDE.md)** | Roteiro completo de demonstração (1h) | Apresentadores |
| **[API_EXAMPLES.md](./API_EXAMPLES.md)** | Comandos curl prontos | Testadores |
| **[LOGGING_BEST_PRACTICES.md](./LOGGING_BEST_PRACTICES.md)** | Guia completo de conceitos | Desenvolvedores |
| **[app/PROJECT_STRUCTURE.md](./app/PROJECT_STRUCTURE.md)** | Guia detalhado de cada arquivo | Desenvolvedores |
| **[app/README.md](./app/README.md)** | Navegação do código fonte | Desenvolvedores |

💡 **Comece por:** [QUICK_START.md](./QUICK_START.md) para estar rodando em 5 minutos!

---

## 🚀 Quick Start

### Opção 1: Docker (Recomendado)

1. **Clone o repositório:**
```bash
git clone https://github.com/GiovanniYuriMita/Datadog-APM-Setups.git
cd python-datadog-apm
```

2. **Configure sua API Key do Datadog:**
Edite `docker-compose.yaml` e substitua `DD_API_KEY` pela sua chave.

3. **Inicie os containers:**
```bash
docker-compose up --build
```

4. **Acesse a API:**
```bash
curl http://localhost:8080
```

### Opção 2: Local (Sem Docker)

1. **Instale o Datadog Agent:**
https://app.datadoghq.com/account/settings/agent/latest?platform=overview

2. **Clone e instale dependências:**
```bash
git clone https://github.com/GiovanniYuriMita/Datadog-APM-Setups.git
cd python-datadog-apm
pip install -r requirements.txt
```

3. **Configure variáveis de ambiente:**
```bash
export DD_ENV=development
export DD_SERVICE=chofs-api
export DD_VERSION=1.0.0
export DD_LOGS_INJECTION=true
```

4. **Execute a aplicação:**
```bash
python app/app.py
```

## 🔌 API Endpoints

A API fornece os seguintes endpoints demonstrando diferentes cenários de logging:

| Endpoint | Método | Descrição | Demonstra |
|----------|--------|-----------|-----------|
| `/` | GET | Documentação da API | - |
| `/health` | GET | Health check | DEBUG logging |
| `/api/user/<user_id>` | GET | Buscar perfil de usuário | PII masking, hashing |
| `/api/products` | GET | Listar produtos | Logging de operações simples |
| `/api/transaction` | POST | Criar transação | Logging de negócio, stages, validações |
| `/api/analytics/transactions` | GET | Analytics de transações | Logging de queries |
| `/api/error/simulate` | GET | Simular erros | Error handling, categorização |

### Exemplos de Uso

**Buscar usuário:**
```bash
curl http://localhost:8080/api/user/user_001
```

**Listar produtos:**
```bash
curl http://localhost:8080/api/products
```

**Criar transação:**
```bash
curl -X POST http://localhost:8080/api/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "product_id": "prod_002",
    "quantity": 2
  }'
```

**Simular erro:**
```bash
curl "http://localhost:8080/api/error/simulate?type=division"
```

## 🔄 Load Testing

Use os scripts de load testing para gerar tráfego contínuo e visualizar logs/traces no Datadog.

### Script Python (Recomendado)

```bash
# Instalar dependência (se não estiver usando Docker)
pip install requests

# Executar com configuração padrão (1 req/sec)
python load_test.py

# Executar com taxa customizada
python load_test.py --rate 2.0

# Executar por tempo limitado
python load_test.py --rate 5 --duration 300  # 5 req/sec por 5 minutos

# Apontar para servidor remoto
python load_test.py --host api.example.com --port 8080 --rate 3
```

### Script Bash (Alternativa)

```bash
# Tornar executável
chmod +x load_test.sh

# Executar com configuração padrão
./load_test.sh

# Executar com taxa customizada
./load_test.sh localhost 8080 2  # 2 req/sec
```

### Cenários de Teste

Os scripts de load testing executam automaticamente diversos cenários:

- ✅ 35% - Transações bem-sucedidas
- ⚠️ 20% - Busca de usuários (alguns não existem)
- 📊 15% - Listagem de produtos
- 📈 10% - Analytics
- ❌ 10% - Transações inválidas (validação)
- 💥 5% - Simulação de erros
- 🏥 5% - Health checks

## 📚 Documentação de Best Practices

Consulte [LOGGING_BEST_PRACTICES.md](./LOGGING_BEST_PRACTICES.md) para documentação completa incluindo:

- ✅ Princípios fundamentais de logging
- ✅ Exemplos de código (bom vs. ruim)
- ✅ Proteção de PII
- ✅ Logging estruturado
- ✅ Error handling
- ✅ Transaction tracking
- ✅ Anti-patterns a evitar
- ✅ Queries úteis no Datadog
- ✅ Checklist para desenvolvedores

## 🔍 Visualizando no Datadog

Após executar a aplicação e o load testing:

1. **Acesse Logs no Datadog:**
   - Navegue para Logs → Search
   - Filtros úteis:
     - `service:chofs-api`
     - `operation:transaction.create`
     - `status:error`

2. **Acesse APM/Traces:**
   - Navegue para APM → Services → chofs-api
   - Clique em qualquer trace para ver detalhes
   - Note a correlação com logs

3. **Dashboards Sugeridos:**
   - Transaction success/failure rate
   - Errors by type
   - Response time percentiles
   - User operations (by hashed ID)

## 🎓 Principais Conceitos Demonstrados

### 1. Log-Trace Correlation
```python
FORMAT = ('... dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s ...')
```

### 2. PII Protection
```python
# Hash IDs sensíveis
user_id_hash = hashlib.sha256(str(user_id).encode()).hexdigest()[:16]

# Maskear emails
masked_email = email[:3] + "*" * (len(email) - 3)
```

### 3. Structured Logging
```python
logger.info(
    "Transaction completed",
    extra={
        'operation': 'transaction.create',
        'transaction_id': txn_id,
        'amount': amount,
        'status': 'success'
    }
)
```

### 4. Custom Spans
```python
with tracer.trace("transaction.create", service="chofs-api") as span:
    span.set_tag("user_id_hash", user_hash)
    # ... seu código ...
```

## 🛠️ Configuração do Datadog

As seguintes variáveis de ambiente são configuradas no `docker-compose.yaml`:

```yaml
DD_ENV=chofs                        # Ambiente
DD_SERVICE=chofs-api                # Nome do serviço
DD_VERSION=20241217-1149            # Versão
DD_LOGS_INJECTION=true              # Habilita correlação log-trace
DD_DYNAMIC_INSTRUMENTATION_ENABLED=true  # Dynamic instrumentation
```

## 📊 Dados de Teste

A aplicação inclui dados mock para demonstração:

**Usuários:**
- `user_001` - John Doe (balance: $1000)
- `user_002` - Jane Smith (balance: $2500)
- `user_003` - Bob Johnson (balance: $500)

**Produtos:**
- `prod_001` - Laptop ($999.99)
- `prod_002` - Mouse ($29.99)
- `prod_003` - Keyboard ($79.99)

## ⚠️ Notas Importantes

- ⚠️ **Não use este código em produção sem revisão** - é apenas demonstrativo
- ⚠️ **Substitua a DD_API_KEY** no docker-compose.yaml pela sua chave real
- ⚠️ Alguns endpoints simulam falhas aleatórias (10% de chance) para demonstrar error logging
- ⚠️ Os dados são armazenados em memória e são perdidos ao reiniciar

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📝 License

Este projeto está licenciado sob a MIT License. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

Este projeto usa as seguintes tecnologias open-source:

- [Python](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/)
- [Datadog Python Tracer](https://github.com/DataDog/dd-trace-py)
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 📞 Suporte

Para dúvidas ou sugestões:
- Abra uma [Issue](https://github.com/GiovanniYuriMita/Datadog-APM-Setups/issues)
- Consulte a [Documentação do Datadog](https://docs.datadoghq.com/)

**Happy logging! 🎉**
