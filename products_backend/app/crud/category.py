from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate
from app.enums import CategoryType


class CategoryCRUD:
    """CRUD operations for Category model"""
    
    @staticmethod
    def create(db: Session, category_data: CategoryCreate) -> Category:
        """Create a new category"""
        db_category = Category(**category_data.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def get_by_id(db: Session, category_id: int, with_products: bool = False) -> Optional[Category]:
        """Get category by ID, optionally with products loaded"""
        query = db.query(Category)
        if with_products:
            query = query.options(joinedload(Category.products))
        return query.filter(Category.id == category_id).first()
    
    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Category]:
        """Get category by code"""
        return db.query(Category).filter(Category.code == code).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Category]:
        """Get category by name"""
        return db.query(Category).filter(Category.name == name).first()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        category_type: Optional[CategoryType] = None,
        search: Optional[str] = None,
        with_products: bool = False
    ) -> List[Category]:
        """Get all categories with optional filters"""
        query = db.query(Category)
        
        if with_products:
            query = query.options(joinedload(Category.products))
        
        if is_active is not None:
            query = query.filter(Category.is_active == is_active)
        
        if category_type is not None:
            query = query.filter(Category.category_type == category_type)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Category.name.ilike(search_filter)) |
                (Category.code.ilike(search_filter))
            )
        
        return query.order_by(Category.name).offset(skip).limit(limit).all()
    
    @staticmethod
    def count(
        db: Session,
        is_active: Optional[bool] = None,
        category_type: Optional[CategoryType] = None,
        search: Optional[str] = None
    ) -> int:
        """Count categories with optional filters"""
        query = db.query(func.count(Category.id))
        
        if is_active is not None:
            query = query.filter(Category.is_active == is_active)
        
        if category_type is not None:
            query = query.filter(Category.category_type == category_type)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Category.name.ilike(search_filter)) |
                (Category.code.ilike(search_filter))
            )
        
        return query.scalar()
    
    @staticmethod
    def update(db: Session, category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
        """Update a category"""
        db_category = CategoryCRUD.get_by_id(db, category_id)
        if not db_category:
            return None
        
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def delete(db: Session, category_id: int) -> bool:
        """Delete a category"""
        db_category = CategoryCRUD.get_by_id(db, category_id)
        if not db_category:
            return False
        
        db.delete(db_category)
        db.commit()
        return True
    
    @staticmethod
    def toggle_active(db: Session, category_id: int) -> Optional[Category]:
        """Toggle category active status"""
        db_category = CategoryCRUD.get_by_id(db, category_id)
        if not db_category:
            return None
        
        db_category.is_active = not db_category.is_active
        db.commit()
        db.refresh(db_category)
        return db_category


# Singleton instance
category_crud = CategoryCRUD()
