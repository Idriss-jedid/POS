from enum import Enum


class ProductStatus(str, Enum):
    """Product availability status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISCONTINUED = "DISCONTINUED"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    PENDING = "PENDING"
