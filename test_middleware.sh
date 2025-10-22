#!/bin/bash

# Script para testar continuamente as rotas do middleware do Datadog
# Este script testa os endpoints de demonstração do middleware

# Configurações
BASE_URL="http://localhost:8080"
INTERVAL=5  # Intervalo entre testes em segundos
LOG_FILE="middleware_test.log"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log com timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Função para testar endpoint
test_endpoint() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local description="$4"
    
    log "${BLUE}Testing: $description${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint")
    fi
    
    # Separa response body e status code
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        log "${GREEN}✓ $description - Status: $http_code${NC}"
    else
        log "${RED}✗ $description - Status: $http_code${NC}"
    fi
    
    # Log da resposta (truncada se muito longa)
    if [ ${#response_body} -gt 200 ]; then
        log "Response: ${response_body:0:200}..."
    else
        log "Response: $response_body"
    fi
    
    echo "---"
}

# Função para testar JSON payload
test_json_payload() {
    local test_data='{
        "user_id": 12345,
        "name": "João Silva",
        "email": "joao@example.com",
        "items": [
            {"id": 1, "name": "Produto A", "price": 29.99},
            {"id": 2, "name": "Produto B", "price": 49.99}
        ],
        "metadata": {
            "source": "web",
            "version": "1.0"
        }
    }'
    
    test_endpoint "POST" "/middleware-demo/json-payload" "$test_data" "JSON Payload Demo"
}

# Função para testar form data
test_form_data() {
    local form_data='name=Maria%20Santos&email=maria@example.com&message=Teste%20de%20form%20data&id=67890'
    
    log "${BLUE}Testing: Form Data Demo${NC}"
    
    response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "$form_data" \
        "$BASE_URL/middleware-demo/form-data")
    
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        log "${GREEN}✓ Form Data Demo - Status: $http_code${NC}"
    else
        log "${RED}✗ Form Data Demo - Status: $http_code${NC}"
    fi
    
    log "Response: $response_body"
    echo "---"
}

# Função para testar query parameters
test_query_params() {
    test_endpoint "GET" "/middleware-demo/query-params?user_id=123&category=electronics&limit=10&page=1" "" "Query Parameters Demo"
}

# Função para testar large payload
test_large_payload() {
    # Cria um payload grande (mais de 4096 caracteres)
    local large_data='{"message": "'
    for i in {1..100}; do
        large_data+="Este é um teste de payload grande para verificar o truncamento do middleware. "
    done
    large_data+='", "user_id": 999, "timestamp": "2024-01-01T00:00:00Z"}'
    
    test_endpoint "POST" "/middleware-demo/large-payload" "$large_data" "Large Payload Demo"
}

# Função para testar error response
test_error_response() {
    local error_data='{"error": "Test error", "code": "TEST_ERROR"}'
    test_endpoint "POST" "/middleware-demo/error-response" "$error_data" "Error Response Demo"
}

# Função para testar health check
test_health() {
    test_endpoint "GET" "/health" "" "Health Check"
}

# Função principal
main() {
    log "${YELLOW}=== Iniciando testes do middleware do Datadog ===${NC}"
    log "Base URL: $BASE_URL"
    log "Intervalo: ${INTERVAL}s"
    log "Log file: $LOG_FILE"
    echo ""
    
    # Verifica se a API está rodando
    log "${BLUE}Verificando se a API está rodando...${NC}"
    if ! curl -s "$BASE_URL/health" > /dev/null 2>&1; then
        log "${RED}❌ API não está rodando em $BASE_URL${NC}"
        log "Execute: source venv/bin/activate && cd app && python3 app.py"
        exit 1
    fi
    log "${GREEN}✓ API está rodando${NC}"
    echo ""
    
    # Loop de testes
    test_count=0
    while true; do
        test_count=$((test_count + 1))
        log "${YELLOW}=== Teste #$test_count ===${NC}"
        
        # Executa todos os testes
        test_health
        test_json_payload
        test_form_data
        test_query_params
        test_large_payload
        test_error_response
        
        log "${GREEN}✓ Ciclo de testes #$test_count concluído${NC}"
        log "Próximo teste em ${INTERVAL}s..."
        echo ""
        
        sleep "$INTERVAL"
    done
}

# Função para mostrar ajuda
show_help() {
    echo "Script para testar middleware do Datadog"
    echo ""
    echo "Uso: $0 [opções]"
    echo ""
    echo "Opções:"
    echo "  -u, --url URL        URL base da API (padrão: http://localhost:5000)"
    echo "  -i, --interval SEC   Intervalo entre testes em segundos (padrão: 5)"
    echo "  -l, --log FILE       Arquivo de log (padrão: middleware_test.log)"
    echo "  -h, --help           Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0                           # Testa com configurações padrão"
    echo "  $0 -u http://localhost:3000  # Testa em porta diferente"
    echo "  $0 -i 10                     # Testa a cada 10 segundos"
}

# Parse de argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            BASE_URL="$2"
            shift 2
            ;;
        -i|--interval)
            INTERVAL="$2"
            shift 2
            ;;
        -l|--log)
            LOG_FILE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Opção desconhecida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Executa função principal
main
