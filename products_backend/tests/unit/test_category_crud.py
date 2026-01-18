"""
Unit Tests for Category CRUD Operations
"""
import pytest
from sqlalchemy.orm import Session

from app.crud import category_crud
from app.schemas import CategoryCreate, CategoryUpdate
from app.models import Category
from app.enums import CategoryType


class TestCategoryCRUD:
    """Test cases for CategoryCRUD class"""
    
    def test_create_category(self, db_session: Session):
        """Test creating a new category"""
        category_data = CategoryCreate(
            name="Electronics",
            code="ELEC001",
            category_type=CategoryType.ELECTRONICS,
            description="Electronic products"
        )
        
        category = category_crud.create(db_session, category_data)
        
        assert category.id is not None
        assert category.name == "Electronics"
        assert category.code == "ELEC001"
        assert category.category_type == CategoryType.ELECTRONICS
        assert category.is_active is True
    
    def test_get_category_by_id(self, db_session: Session, sample_category: Category):
        """Test getting category by ID"""
        category = category_crud.get_by_id(db_session, sample_category.id)
        
        assert category is not None
        assert category.id == sample_category.id
    
    def test_get_category_by_code(self, db_session: Session, sample_category: Category):
        """Test getting category by code"""
        category = category_crud.get_by_code(db_session, sample_category.code)
        
        assert category is not None
        assert category.code == sample_category.code
    
    def test_get_category_by_name(self, db_session: Session, sample_category: Category):
        """Test getting category by name"""
        category = category_crud.get_by_name(db_session, sample_category.name)
        
        assert category is not None
        assert category.name == sample_category.name
    
    def test_get_all_categories(self, db_session: Session, sample_category: Category):
        """Test getting all categories"""
        # Create another category
        another = Category(
            name="Food", 
            code="FOOD001", 
            category_type=CategoryType.FOOD_BEVERAGE
        )
        db_session.add(another)
        db_session.commit()
        
        categories = category_crud.get_all(db_session)
        
        assert len(categories) == 2
    
    def test_get_all_categories_by_type(self, db_session: Session, sample_category: Category):
        """Test getting categories filtered by type"""
        # Create another category with different type
        food_cat = Category(
            name="Food Items", 
            code="FOOD001", 
            category_type=CategoryType.FOOD_BEVERAGE
        )
        db_session.add(food_cat)
        db_session.commit()
        
        electronics = category_crud.get_all(
            db_session, 
            category_type=CategoryType.ELECTRONICS
        )
        food = category_crud.get_all(
            db_session, 
            category_type=CategoryType.FOOD_BEVERAGE
        )
        
        assert len(electronics) == 1
        assert len(food) == 1
    
    def test_count_categories(self, db_session: Session, sample_category: Category):
        """Test counting categories"""
        count = category_crud.count(db_session)
        assert count == 1
    
    def test_update_category(self, db_session: Session, sample_category: Category):
        """Test updating a category"""
        update_data = CategoryUpdate(
            name="Updated Category",
            description="Updated description"
        )
        
        updated = category_crud.update(db_session, sample_category.id, update_data)
        
        assert updated is not None
        assert updated.name == "Updated Category"
        assert updated.description == "Updated description"
    
    def test_delete_category(self, db_session: Session, sample_category: Category):
        """Test deleting a category"""
        result = category_crud.delete(db_session, sample_category.id)
        
        assert result is True
        assert category_crud.get_by_id(db_session, sample_category.id) is None
    
    def test_toggle_category_active(self, db_session: Session, sample_category: Category):
        """Test toggling category active status"""
        assert sample_category.is_active is True
        
        toggled = category_crud.toggle_active(db_session, sample_category.id)
        assert toggled.is_active is False
