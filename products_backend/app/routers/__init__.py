from .company import router as company_router
from .category import router as category_router
from .product import router as product_router

__all__ = [
    "company_router",
    "category_router",
    "product_router",
]
