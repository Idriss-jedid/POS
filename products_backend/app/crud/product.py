from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models import Product, Company, Category
from app.schemas import ProductCreate, ProductUpdate, ProductCSVRow, CSVImportResult
from app.enums import ProductStatus, UnitType


class ProductCRUD:
    """CRUD operations for Product model"""
    
    @staticmethod
    def create(db: Session, product_data: ProductCreate) -> Product:
        """Create a new product"""
        db_product = Product(**product_data.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    def get_by_id(db: Session, product_id: int, with_relations: bool = False) -> Optional[Product]:
        """Get product by ID"""
        query = db.query(Product)
        if with_relations:
            query = query.options(joinedload(Product.company), joinedload(Product.category))
        return query.filter(Product.id == product_id).first()
    
    @staticmethod
    def get_by_sku(db: Session, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        return db.query(Product).filter(Product.sku == sku).first()
    
    @staticmethod
    def get_by_barcode(db: Session, barcode: str) -> Optional[Product]:
        """Get product by barcode"""
        return db.query(Product).filter(Product.barcode == barcode).first()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[int] = None,
        category_id: Optional[int] = None,
        status: Optional[ProductStatus] = None,
        search: Optional[str] = None,
        low_stock_only: bool = False,
        with_relations: bool = False
    ) -> List[Product]:
        """Get all products with optional filters"""
        query = db.query(Product)
        
        if with_relations:
            query = query.options(joinedload(Product.company), joinedload(Product.category))
        
        if company_id is not None:
            query = query.filter(Product.company_id == company_id)
        
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        
        if status is not None:
            query = query.filter(Product.status == status)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Product.name.ilike(search_filter)) |
                (Product.sku.ilike(search_filter)) |
                (Product.barcode.ilike(search_filter)) |
                (Product.brand.ilike(search_filter))
            )
        
        if low_stock_only:
            query = query.filter(Product.quantity <= Product.min_stock_level)
        
        return query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def count(
        db: Session,
        company_id: Optional[int] = None,
        category_id: Optional[int] = None,
        status: Optional[ProductStatus] = None,
        search: Optional[str] = None,
        low_stock_only: bool = False
    ) -> int:
        """Count products with optional filters"""
        query = db.query(func.count(Product.id))
        
        if company_id is not None:
            query = query.filter(Product.company_id == company_id)
        
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        
        if status is not None:
            query = query.filter(Product.status == status)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Product.name.ilike(search_filter)) |
                (Product.sku.ilike(search_filter)) |
                (Product.barcode.ilike(search_filter)) |
                (Product.brand.ilike(search_filter))
            )
        
        if low_stock_only:
            query = query.filter(Product.quantity <= Product.min_stock_level)
        
        return query.scalar()
    
    @staticmethod
    def update(db: Session, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update a product"""
        db_product = ProductCRUD.get_by_id(db, product_id)
        if not db_product:
            return None
        
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    def delete(db: Session, product_id: int) -> bool:
        """Delete a product"""
        db_product = ProductCRUD.get_by_id(db, product_id)
        if not db_product:
            return False
        
        db.delete(db_product)
        db.commit()
        return True
    
    @staticmethod
    def update_quantity(db: Session, product_id: int, quantity_change: int) -> Optional[Product]:
        """Update product quantity (add or subtract)"""
        db_product = ProductCRUD.get_by_id(db, product_id)
        if not db_product:
            return None
        
        new_quantity = db_product.quantity + quantity_change
        if new_quantity < 0:
            new_quantity = 0
        
        db_product.quantity = new_quantity
        
        # Auto-update status based on stock
        if new_quantity == 0:
            db_product.status = ProductStatus.OUT_OF_STOCK
        elif db_product.status == ProductStatus.OUT_OF_STOCK and new_quantity > 0:
            db_product.status = ProductStatus.ACTIVE
        
        db.commit()
        db.refresh(db_product)
        return db_product
    
    @staticmethod
    def bulk_import(
        db: Session,
        products: List[ProductCSVRow],
        company_id: int,
        skip_duplicates: bool = True
    ) -> CSVImportResult:
        """Bulk import products from CSV data. Each product has its own category_id."""
        result = CSVImportResult(
            total_rows=len(products),
            successful=0,
            failed=0,
            skipped=0,
            errors=[],
            created_product_ids=[]
        )
        
        # Verify company exists
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            result.errors.append(f"Company with ID {company_id} not found")
            result.failed = len(products)
            return result
        
        for idx, product_row in enumerate(products, start=1):
            try:
                # Check for duplicate SKU
                existing = ProductCRUD.get_by_sku(db, product_row.sku)
                if existing:
                    if skip_duplicates:
                        result.skipped += 1
                        result.errors.append(f"Row {idx}: SKU '{product_row.sku}' already exists - skipped")
                        continue
                    else:
                        result.failed += 1
                        result.errors.append(f"Row {idx}: SKU '{product_row.sku}' already exists")
                        continue
                
                # Parse unit and status enums
                try:
                    unit = UnitType(product_row.unit.upper()) if product_row.unit else UnitType.PIECE
                except ValueError:
                    unit = UnitType.PIECE
                
                try:
                    status = ProductStatus(product_row.status.upper()) if product_row.status else ProductStatus.ACTIVE
                except ValueError:
                    status = ProductStatus.ACTIVE
                
                # Create product with category_id from the row
                db_product = Product(
                    name=product_row.name,
                    sku=product_row.sku,
                    barcode=product_row.barcode,
                    description=product_row.description,
                    cost_price=product_row.cost_price,
                    selling_price=product_row.selling_price,
                    quantity=product_row.quantity,
                    min_stock_level=product_row.min_stock_level,
                    unit=unit,
                    status=status,
                    brand=product_row.brand,
                    company_id=company_id,
                    category_id=product_row.category_id
                )
                
                db.add(db_product)
                db.flush()  # Get the ID without committing
                result.created_product_ids.append(db_product.id)
                result.successful += 1
                
            except Exception as e:
                result.failed += 1
                result.errors.append(f"Row {idx}: {str(e)}")
        
        # Commit all successful products
        if result.successful > 0:
            db.commit()
        
        return result
    
    @staticmethod
    def get_statistics(db: Session, company_id: Optional[int] = None) -> dict:
        """Get product statistics"""
        base_query = db.query(Product)
        if company_id:
            base_query = base_query.filter(Product.company_id == company_id)
        
        total = base_query.count()
        active = base_query.filter(Product.status == ProductStatus.ACTIVE).count()
        out_of_stock = base_query.filter(Product.status == ProductStatus.OUT_OF_STOCK).count()
        low_stock = base_query.filter(Product.quantity <= Product.min_stock_level).count()
        
        # Total inventory value
        total_cost_value = db.query(func.sum(Product.cost_price * Product.quantity))
        total_sell_value = db.query(func.sum(Product.selling_price * Product.quantity))
        
        if company_id:
            total_cost_value = total_cost_value.filter(Product.company_id == company_id)
            total_sell_value = total_sell_value.filter(Product.company_id == company_id)
        
        return {
            "total_products": total,
            "active_products": active,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
            "total_cost_value": total_cost_value.scalar() or 0,
            "total_sell_value": total_sell_value.scalar() or 0
        }


# Singleton instance
product_crud = ProductCRUD()
