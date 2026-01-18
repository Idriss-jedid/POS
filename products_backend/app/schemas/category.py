from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, computed_field

from app.enums import CategoryType


class CategoryBase(BaseModel):
    """Base schema for Category"""
    name: str = Field(..., min_length=1, max_length=255, description="Category name")
    code: str = Field(..., min_length=1, max_length=50, description="Unique category code")
    category_type: CategoryType = Field(CategoryType.OTHER, description="Category type")
    description: Optional[str] = Field(None, description="Category description")


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    category_type: Optional[CategoryType] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryOut(CategoryBase):
    """Schema for category response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductSimpleForCategory(BaseModel):
    """Simple product schema for category details"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    sku: str
    barcode: Optional[str] = None
    selling_price: float
    cost_price: float
    quantity: int
    brand: Optional[str] = None


class CategoryWithProductCount(CategoryOut):
    """Category with product count - use when products are loaded"""
    products: List[ProductSimpleForCategory] = []
    
    @computed_field
    @property
    def product_count(self) -> int:
        """Compute product count from loaded products"""
        return len(self.products)


class CategoryWithProducts(CategoryOut):
    """Category with full product list"""
    products: List[ProductSimpleForCategory] = []
    
    @computed_field
    @property
    def product_count(self) -> int:
        return len(self.products)
