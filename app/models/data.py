"""
Mock Data for Demo

Dados de exemplo para demonstração.
Em produção, isso seria um banco de dados real.
"""

# In-memory "database" para demo
MOCK_USERS = {
    "user_001": {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "balance": 1000.00,
        "account_type": "premium",
        "created_at": "2024-01-15",
        "country": "BR",
        "city": "São Paulo",
        "preferred_payment": "credit_card",
        "total_transactions": 42,
        "lifetime_value": 5420.50
    },
    "user_002": {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "balance": 2500.00,
        "account_type": "enterprise",
        "created_at": "2023-06-20",
        "country": "US",
        "city": "New York",
        "preferred_payment": "invoice",
        "total_transactions": 128,
        "lifetime_value": 15890.25
    },
    "user_003": {
        "name": "Bob Johnson",
        "email": "bob.johnson@example.com",
        "balance": 500.00,
        "account_type": "basic",
        "created_at": "2024-10-01",
        "country": "BR",
        "city": "Rio de Janeiro",
        "preferred_payment": "pix",
        "total_transactions": 3,
        "lifetime_value": 150.00
    },
}

MOCK_PRODUCTS = {
    "prod_001": {
        "name": "Laptop",
        "price": 999.99,
        "stock": 10,
        "category": "electronics",
        "sku": "LAP-2024-001",
        "vendor": "Dell",
        "restock_threshold": 5,
        "avg_delivery_days": 3
    },
    "prod_002": {
        "name": "Mouse",
        "price": 29.99,
        "stock": 100,
        "category": "accessories",
        "sku": "MOU-2024-002",
        "vendor": "Logitech",
        "restock_threshold": 20,
        "avg_delivery_days": 1
    },
    "prod_003": {
        "name": "Keyboard",
        "price": 79.99,
        "stock": 50,
        "category": "accessories",
        "sku": "KEY-2024-003",
        "vendor": "Corsair",
        "restock_threshold": 15,
        "avg_delivery_days": 2
    },
}

# Lista de transações (seria uma tabela no banco de dados)
TRANSACTIONS = []

