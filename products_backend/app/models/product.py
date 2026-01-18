from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.enums import ProductStatus, UnitType


class Product(Base):
    """
    Product model - main entity representing products in inventory.
    Each product belongs to a company (supplier) and a category.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), nullable=False, unique=True, index=True)  # Stock Keeping Unit
    barcode = Column(String(100), nullable=True, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Pricing
    cost_price = Column(Float, nullable=False, default=0.0)  # Purchase price
    selling_price = Column(Float, nullable=False, default=0.0)  # Retail price
    
    # Inventory
    quantity = Column(Integer, nullable=False, default=0)
    min_stock_level = Column(Integer, nullable=False, default=0)  # Reorder point
    max_stock_level = Column(Integer, nullable=True)
    
    # Unit & Status
    unit = Column(SQLEnum(UnitType), nullable=False, default=UnitType.PIECE)
    status = Column(SQLEnum(ProductStatus), nullable=False, default=ProductStatus.ACTIVE)
    
    # Foreign Keys
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    
    # Additional Info
    brand = Column(String(100), nullable=True)
    weight = Column(Float, nullable=True)  # In kg or appropriate unit
    dimensions = Column(String(100), nullable=True)  # Format: "LxWxH"
    image_url = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    company = relationship("Company", back_populates="products")
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"
    
    @property
    def is_low_stock(self) -> bool:
        """Check if product is below minimum stock level"""
        return self.quantity <= self.min_stock_level
    
    @property
    def profit_margin(self) -> float:
        """Calculate profit margin percentage"""
        if self.cost_price == 0:
            return 0.0
        return ((self.selling_price - self.cost_price) / self.cost_price) * 100
