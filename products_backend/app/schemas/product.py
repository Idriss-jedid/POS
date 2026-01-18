from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.enums import ProductStatus, UnitType


class CompanySimple(BaseModel):
    """Simple company schema to avoid circular imports"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: str


class CategorySimple(BaseModel):
    """Simple category schema to avoid circular imports"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: str


class ProductBase(BaseModel):
    """Base schema for Product"""
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    barcode: Optional[str] = Field(None, max_length=100, description="Product barcode")
    description: Optional[str] = Field(None, description="Product description")
    
    cost_price: float = Field(0.0, ge=0, description="Purchase/cost price")
    selling_price: float = Field(0.0, ge=0, description="Selling/retail price")
    
    quantity: int = Field(0, ge=0, description="Current stock quantity")
    min_stock_level: int = Field(0, ge=0, description="Minimum stock level for reorder")
    max_stock_level: Optional[int] = Field(None, ge=0, description="Maximum stock level")
    
    unit: UnitType = Field(UnitType.PIECE, description="Unit of measurement")
    status: ProductStatus = Field(ProductStatus.ACTIVE, description="Product status")
    
    brand: Optional[str] = Field(None, max_length=100, description="Brand name")
    weight: Optional[float] = Field(None, ge=0, description="Weight in kg")
    dimensions: Optional[str] = Field(None, max_length=100, description="Dimensions (LxWxH)")
    image_url: Optional[str] = Field(None, max_length=500, description="Product image URL")
    notes: Optional[str] = Field(None, description="Additional notes")


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    company_id: int = Field(..., gt=0, description="Company/Supplier ID")
    category_id: int = Field(..., gt=0, description="Category ID")


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    
    cost_price: Optional[float] = Field(None, ge=0)
    selling_price: Optional[float] = Field(None, ge=0)
    
    quantity: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    
    unit: Optional[UnitType] = None
    status: Optional[ProductStatus] = None
    
    company_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    
    brand: Optional[str] = Field(None, max_length=100)
    weight: Optional[float] = Field(None, ge=0)
    dimensions: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


class ProductOut(ProductBase):
    """Schema for product response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    company_id: int
    category_id: int
    created_at: datetime
    updated_at: datetime


class ProductWithRelations(ProductOut):
    """Product with company and category details"""
    company: CompanySimple
    category: CategorySimple
    is_low_stock: bool = False
    profit_margin: float = 0.0


# CSV Import Schemas
class ProductCSVRow(BaseModel):
    """Schema for a single CSV row"""
    name: str
    sku: str
    barcode: Optional[str] = None
    description: Optional[str] = None
    cost_price: float = 0.0
    selling_price: float = 0.0
    quantity: int = 0
    min_stock_level: int = 0
    unit: Optional[str] = "PIECE"
    status: Optional[str] = "ACTIVE"
    brand: Optional[str] = None
    category_id: Optional[int] = None  # Category ID for this product


class CSVImportRequest(BaseModel):
    """Request schema for CSV import"""
    company_id: int = Field(..., gt=0, description="Company ID to associate products with")
    products: List[ProductCSVRow] = Field(..., description="List of products from CSV")
    skip_duplicates: bool = Field(True, description="Skip products with duplicate SKU")


class CSVImportResult(BaseModel):
    """Response schema for CSV import"""
    total_rows: int
    successful: int
    failed: int
    skipped: int
    errors: List[str] = []
    created_product_ids: List[int] = []
