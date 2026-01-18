from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models import Company
from app.schemas import CompanyCreate, CompanyUpdate


class CompanyCRUD:
    """CRUD operations for Company model"""
    
    @staticmethod
    def create(db: Session, company_data: CompanyCreate) -> Company:
        """Create a new company"""
        db_company = Company(**company_data.model_dump())
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company
    
    @staticmethod
    def get_by_id(db: Session, company_id: int, with_products: bool = False) -> Optional[Company]:
        """Get company by ID, optionally with products loaded"""
        query = db.query(Company)
        if with_products:
            query = query.options(joinedload(Company.products))
        return query.filter(Company.id == company_id).first()
    
    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Company]:
        """Get company by code"""
        return db.query(Company).filter(Company.code == code).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Company]:
        """Get company by name"""
        return db.query(Company).filter(Company.name == name).first()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        with_products: bool = False
    ) -> List[Company]:
        """Get all companies with optional filters"""
        query = db.query(Company)
        
        if with_products:
            query = query.options(joinedload(Company.products))
        
        if is_active is not None:
            query = query.filter(Company.is_active == is_active)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Company.name.ilike(search_filter)) |
                (Company.code.ilike(search_filter)) |
                (Company.email.ilike(search_filter))
            )
        
        return query.order_by(Company.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def count(
        db: Session,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> int:
        """Count companies with optional filters"""
        query = db.query(func.count(Company.id))
        
        if is_active is not None:
            query = query.filter(Company.is_active == is_active)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Company.name.ilike(search_filter)) |
                (Company.code.ilike(search_filter)) |
                (Company.email.ilike(search_filter))
            )
        
        return query.scalar()
    
    @staticmethod
    def update(db: Session, company_id: int, company_data: CompanyUpdate) -> Optional[Company]:
        """Update a company"""
        db_company = CompanyCRUD.get_by_id(db, company_id)
        if not db_company:
            return None
        
        update_data = company_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_company, field, value)
        
        db.commit()
        db.refresh(db_company)
        return db_company
    
    @staticmethod
    def delete(db: Session, company_id: int) -> bool:
        """Delete a company"""
        db_company = CompanyCRUD.get_by_id(db, company_id)
        if not db_company:
            return False
        
        db.delete(db_company)
        db.commit()
        return True
    
    @staticmethod
    def toggle_active(db: Session, company_id: int) -> Optional[Company]:
        """Toggle company active status"""
        db_company = CompanyCRUD.get_by_id(db, company_id)
        if not db_company:
            return None
        
        db_company.is_active = not db_company.is_active
        db.commit()
        db.refresh(db_company)
        return db_company


# Singleton instance
company_crud = CompanyCRUD()
