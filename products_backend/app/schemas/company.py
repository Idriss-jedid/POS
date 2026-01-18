from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict, computed_field


class CompanyBase(BaseModel):
    """Base schema for Company"""
    name: str = Field(..., min_length=1, max_length=255, description="Company name")
    code: str = Field(..., min_length=1, max_length=50, description="Unique company code")
    email: Optional[EmailStr] = Field(None, description="Company email")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    address: Optional[str] = Field(None, description="Company address")
    website: Optional[str] = Field(None, max_length=255, description="Company website")
    contact_person: Optional[str] = Field(None, max_length=255, description="Contact person name")
    description: Optional[str] = Field(None, description="Company description")


class CompanyCreate(CompanyBase):
    """Schema for creating a company"""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    website: Optional[str] = Field(None, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyOut(CompanyBase):
    """Schema for company response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductSimpleForCompany(BaseModel):
    """Simple product schema for company details"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    sku: str
    barcode: Optional[str] = None
    selling_price: float
    cost_price: float
    quantity: int
    brand: Optional[str] = None


class CompanyWithProductCount(CompanyOut):
    """Company with product count - use when products are loaded"""
    products: List[ProductSimpleForCompany] = []
    
    @computed_field
    @property
    def product_count(self) -> int:
        """Compute product count from loaded products"""
        return len(self.products)


class CompanyWithProducts(CompanyOut):
    """Company with full product list"""
    products: List[ProductSimpleForCompany] = []
    
    @computed_field
    @property
    def product_count(self) -> int:
        return len(self.products)
