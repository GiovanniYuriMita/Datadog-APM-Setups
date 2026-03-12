"""
API Routes package

Organiza os endpoints por domínio/funcionalidade.
"""

from .health import health_bp
from .users import users_bp
from .products import products_bp
from .transactions import transactions_bp
from .analytics import analytics_bp
from .errors import errors_bp
from .home import home_bp
from .dynamic_demo import dynamic_demo_bp

__all__ = [
    'health_bp',
    'users_bp',
    'products_bp',
    'transactions_bp',
    'analytics_bp',
    'errors_bp',
    'home_bp',
    'dynamic_demo_bp',
]

