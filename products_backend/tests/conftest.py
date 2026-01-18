"""
Test Configuration and Fixtures
"""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import Company, Category, Product
from app.enums import ProductStatus, UnitType, CategoryType

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override database dependency for tests"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client"""
    yield TestClient(app)


@pytest.fixture
def sample_company(db_session: Session) -> Company:
    """Create a sample company"""
    company = Company(
        name="Test Company",
        code="TEST001",
        email="test@company.com",
        phone="+1234567890",
        address="123 Test Street",
        is_active=True
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def sample_category(db_session: Session) -> Category:
    """Create a sample category"""
    category = Category(
        name="Test Category",
        code="CAT001",
        category_type=CategoryType.ELECTRONICS,
        description="Test category description",
        is_active=True
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def sample_product(db_session: Session, sample_company: Company, sample_category: Category) -> Product:
    """Create a sample product"""
    product = Product(
        name="Test Product",
        sku="SKU001",
        barcode="1234567890123",
        description="Test product description",
        cost_price=10.00,
        selling_price=15.00,
        quantity=100,
        min_stock_level=10,
        unit=UnitType.PIECE,
        status=ProductStatus.ACTIVE,
        brand="Test Brand",
        company_id=sample_company.id,
        category_id=sample_category.id
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def sample_csv_content() -> str:
    """Sample CSV content for import testing"""
    return """name,sku,barcode,description,cost_price,selling_price,quantity,min_stock_level,unit,status,brand
Product A,SKU-A001,1111111111111,Product A desc,10.50,15.99,100,20,PIECE,ACTIVE,BrandA
Product B,SKU-B002,2222222222222,Product B desc,20.00,29.99,50,10,KG,ACTIVE,BrandB
Product C,SKU-C003,,Product C desc,5.00,8.99,200,30,LITER,ACTIVE,BrandC"""
