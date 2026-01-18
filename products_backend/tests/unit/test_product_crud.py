"""
Unit Tests for Product CRUD Operations
"""
import pytest
from sqlalchemy.orm import Session

from app.crud import product_crud
from app.schemas import ProductCreate, ProductUpdate, ProductCSVRow
from app.models import Product, Company, Category
from app.enums import ProductStatus, UnitType


class TestProductCRUD:
    """Test cases for ProductCRUD class"""
    
    def test_create_product(
        self, 
        db_session: Session, 
        sample_company: Company, 
        sample_category: Category
    ):
        """Test creating a new product"""
        product_data = ProductCreate(
            name="New Product",
            sku="NEWSKU001",
            barcode="9999999999999",
            description="New product description",
            cost_price=10.00,
            selling_price=19.99,
            quantity=50,
            min_stock_level=5,
            unit=UnitType.PIECE,
            status=ProductStatus.ACTIVE,
            company_id=sample_company.id,
            category_id=sample_category.id
        )
        
        product = product_crud.create(db_session, product_data)
        
        assert product.id is not None
        assert product.name == "New Product"
        assert product.sku == "NEWSKU001"
        assert product.cost_price == 10.00
        assert product.selling_price == 19.99
        assert product.company_id == sample_company.id
        assert product.category_id == sample_category.id
    
    def test_get_product_by_id(self, db_session: Session, sample_product: Product):
        """Test getting product by ID"""
        product = product_crud.get_by_id(db_session, sample_product.id)
        
        assert product is not None
        assert product.id == sample_product.id
    
    def test_get_product_by_id_with_relations(
        self, 
        db_session: Session, 
        sample_product: Product
    ):
        """Test getting product by ID with relations loaded"""
        product = product_crud.get_by_id(
            db_session, 
            sample_product.id, 
            with_relations=True
        )
        
        assert product is not None
        assert product.company is not None
        assert product.category is not None
    
    def test_get_product_by_sku(self, db_session: Session, sample_product: Product):
        """Test getting product by SKU"""
        product = product_crud.get_by_sku(db_session, sample_product.sku)
        
        assert product is not None
        assert product.sku == sample_product.sku
    
    def test_get_product_by_barcode(self, db_session: Session, sample_product: Product):
        """Test getting product by barcode"""
        product = product_crud.get_by_barcode(db_session, sample_product.barcode)
        
        assert product is not None
        assert product.barcode == sample_product.barcode
    
    def test_get_all_products(self, db_session: Session, sample_product: Product):
        """Test getting all products"""
        products = product_crud.get_all(db_session)
        
        assert len(products) == 1
        assert products[0].id == sample_product.id
    
    def test_get_products_by_company(
        self, 
        db_session: Session, 
        sample_product: Product,
        sample_company: Company
    ):
        """Test filtering products by company"""
        products = product_crud.get_all(
            db_session, 
            company_id=sample_company.id
        )
        
        assert len(products) == 1
    
    def test_get_products_by_category(
        self, 
        db_session: Session, 
        sample_product: Product,
        sample_category: Category
    ):
        """Test filtering products by category"""
        products = product_crud.get_all(
            db_session, 
            category_id=sample_category.id
        )
        
        assert len(products) == 1
    
    def test_get_products_by_status(self, db_session: Session, sample_product: Product):
        """Test filtering products by status"""
        active = product_crud.get_all(db_session, status=ProductStatus.ACTIVE)
        inactive = product_crud.get_all(db_session, status=ProductStatus.INACTIVE)
        
        assert len(active) == 1
        assert len(inactive) == 0
    
    def test_get_products_search(self, db_session: Session, sample_product: Product):
        """Test searching products"""
        products = product_crud.get_all(db_session, search="Test")
        
        assert len(products) == 1
    
    def test_get_low_stock_products(
        self, 
        db_session: Session, 
        sample_company: Company, 
        sample_category: Category
    ):
        """Test getting low stock products"""
        # Create low stock product
        low_stock = Product(
            name="Low Stock Product",
            sku="LOWSKU001",
            cost_price=5.00,
            selling_price=10.00,
            quantity=5,
            min_stock_level=10,  # quantity < min_stock_level
            company_id=sample_company.id,
            category_id=sample_category.id
        )
        db_session.add(low_stock)
        db_session.commit()
        
        products = product_crud.get_all(db_session, low_stock_only=True)
        
        assert len(products) == 1
        assert products[0].sku == "LOWSKU001"
    
    def test_count_products(self, db_session: Session, sample_product: Product):
        """Test counting products"""
        count = product_crud.count(db_session)
        assert count == 1
    
    def test_update_product(self, db_session: Session, sample_product: Product):
        """Test updating a product"""
        update_data = ProductUpdate(
            name="Updated Product Name",
            selling_price=20.00
        )
        
        updated = product_crud.update(db_session, sample_product.id, update_data)
        
        assert updated is not None
        assert updated.name == "Updated Product Name"
        assert updated.selling_price == 20.00
        assert updated.cost_price == sample_product.cost_price  # Unchanged
    
    def test_delete_product(self, db_session: Session, sample_product: Product):
        """Test deleting a product"""
        result = product_crud.delete(db_session, sample_product.id)
        
        assert result is True
        assert product_crud.get_by_id(db_session, sample_product.id) is None
    
    def test_update_quantity_add(self, db_session: Session, sample_product: Product):
        """Test adding to product quantity"""
        initial_qty = sample_product.quantity
        
        updated = product_crud.update_quantity(db_session, sample_product.id, 50)
        
        assert updated.quantity == initial_qty + 50
    
    def test_update_quantity_subtract(self, db_session: Session, sample_product: Product):
        """Test subtracting from product quantity"""
        initial_qty = sample_product.quantity
        
        updated = product_crud.update_quantity(db_session, sample_product.id, -20)
        
        assert updated.quantity == initial_qty - 20
    
    def test_update_quantity_auto_out_of_stock(
        self, 
        db_session: Session, 
        sample_product: Product
    ):
        """Test auto status change to OUT_OF_STOCK when quantity reaches 0"""
        # Subtract all quantity
        updated = product_crud.update_quantity(
            db_session, 
            sample_product.id, 
            -sample_product.quantity
        )
        
        assert updated.quantity == 0
        assert updated.status == ProductStatus.OUT_OF_STOCK
    
    def test_bulk_import(
        self, 
        db_session: Session, 
        sample_company: Company, 
        sample_category: Category
    ):
        """Test bulk importing products"""
        products = [
            ProductCSVRow(
                name="Bulk Product 1",
                sku="BULK001",
                cost_price=10.00,
                selling_price=15.00,
                quantity=100
            ),
            ProductCSVRow(
                name="Bulk Product 2",
                sku="BULK002",
                cost_price=20.00,
                selling_price=30.00,
                quantity=50
            ),
        ]
        
        result = product_crud.bulk_import(
            db_session,
            products=products,
            company_id=sample_company.id,
            category_id=sample_category.id
        )
        
        assert result.total_rows == 2
        assert result.successful == 2
        assert result.failed == 0
        assert len(result.created_product_ids) == 2
    
    def test_bulk_import_skip_duplicates(
        self, 
        db_session: Session, 
        sample_company: Company, 
        sample_category: Category,
        sample_product: Product
    ):
        """Test bulk import skipping duplicate SKUs"""
        products = [
            ProductCSVRow(
                name="Duplicate Product",
                sku=sample_product.sku,  # Duplicate SKU
                cost_price=10.00,
                selling_price=15.00,
                quantity=100
            ),
            ProductCSVRow(
                name="New Product",
                sku="NEWSKU002",
                cost_price=20.00,
                selling_price=30.00,
                quantity=50
            ),
        ]
        
        result = product_crud.bulk_import(
            db_session,
            products=products,
            company_id=sample_company.id,
            category_id=sample_category.id,
            skip_duplicates=True
        )
        
        assert result.total_rows == 2
        assert result.successful == 1
        assert result.skipped == 1
    
    def test_get_statistics(
        self, 
        db_session: Session, 
        sample_product: Product
    ):
        """Test getting product statistics"""
        stats = product_crud.get_statistics(db_session)
        
        assert stats["total_products"] == 1
        assert stats["active_products"] == 1
        assert stats["out_of_stock"] == 0


class TestProductProperties:
    """Test Product model properties"""
    
    def test_is_low_stock(self, sample_product: Product):
        """Test is_low_stock property"""
        sample_product.quantity = 5
        sample_product.min_stock_level = 10
        
        assert sample_product.is_low_stock is True
        
        sample_product.quantity = 15
        assert sample_product.is_low_stock is False
    
    def test_profit_margin(self, sample_product: Product):
        """Test profit_margin property"""
        sample_product.cost_price = 10.00
        sample_product.selling_price = 15.00
        
        # Profit = 5, Margin = (5/10) * 100 = 50%
        assert sample_product.profit_margin == 50.0
    
    def test_profit_margin_zero_cost(self, sample_product: Product):
        """Test profit_margin with zero cost price"""
        sample_product.cost_price = 0
        sample_product.selling_price = 15.00
        
        assert sample_product.profit_margin == 0.0
