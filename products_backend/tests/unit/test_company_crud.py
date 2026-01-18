"""
Unit Tests for Company CRUD Operations
"""
import pytest
from sqlalchemy.orm import Session

from app.crud import company_crud
from app.schemas import CompanyCreate, CompanyUpdate
from app.models import Company


class TestCompanyCRUD:
    """Test cases for CompanyCRUD class"""
    
    def test_create_company(self, db_session: Session):
        """Test creating a new company"""
        company_data = CompanyCreate(
            name="New Company",
            code="NEW001",
            email="new@company.com",
            phone="+1234567890"
        )
        
        company = company_crud.create(db_session, company_data)
        
        assert company.id is not None
        assert company.name == "New Company"
        assert company.code == "NEW001"
        assert company.email == "new@company.com"
        assert company.is_active is True
    
    def test_get_company_by_id(self, db_session: Session, sample_company: Company):
        """Test getting company by ID"""
        company = company_crud.get_by_id(db_session, sample_company.id)
        
        assert company is not None
        assert company.id == sample_company.id
        assert company.name == sample_company.name
    
    def test_get_company_by_id_not_found(self, db_session: Session):
        """Test getting non-existent company"""
        company = company_crud.get_by_id(db_session, 99999)
        assert company is None
    
    def test_get_company_by_code(self, db_session: Session, sample_company: Company):
        """Test getting company by code"""
        company = company_crud.get_by_code(db_session, sample_company.code)
        
        assert company is not None
        assert company.code == sample_company.code
    
    def test_get_company_by_name(self, db_session: Session, sample_company: Company):
        """Test getting company by name"""
        company = company_crud.get_by_name(db_session, sample_company.name)
        
        assert company is not None
        assert company.name == sample_company.name
    
    def test_get_all_companies(self, db_session: Session, sample_company: Company):
        """Test getting all companies"""
        # Create another company
        another = Company(name="Another Co", code="ANO001", is_active=True)
        db_session.add(another)
        db_session.commit()
        
        companies = company_crud.get_all(db_session)
        
        assert len(companies) == 2
    
    def test_get_all_companies_with_filter(self, db_session: Session, sample_company: Company):
        """Test getting companies with active filter"""
        # Create inactive company
        inactive = Company(name="Inactive Co", code="INA001", is_active=False)
        db_session.add(inactive)
        db_session.commit()
        
        active_companies = company_crud.get_all(db_session, is_active=True)
        inactive_companies = company_crud.get_all(db_session, is_active=False)
        
        assert len(active_companies) == 1
        assert len(inactive_companies) == 1
    
    def test_get_all_companies_with_search(self, db_session: Session, sample_company: Company):
        """Test getting companies with search"""
        companies = company_crud.get_all(db_session, search="Test")
        
        assert len(companies) == 1
        assert companies[0].name == "Test Company"
    
    def test_count_companies(self, db_session: Session, sample_company: Company):
        """Test counting companies"""
        count = company_crud.count(db_session)
        assert count == 1
    
    def test_update_company(self, db_session: Session, sample_company: Company):
        """Test updating a company"""
        update_data = CompanyUpdate(name="Updated Company Name")
        
        updated = company_crud.update(db_session, sample_company.id, update_data)
        
        assert updated is not None
        assert updated.name == "Updated Company Name"
        assert updated.code == sample_company.code  # Unchanged
    
    def test_update_company_not_found(self, db_session: Session):
        """Test updating non-existent company"""
        update_data = CompanyUpdate(name="New Name")
        updated = company_crud.update(db_session, 99999, update_data)
        
        assert updated is None
    
    def test_delete_company(self, db_session: Session, sample_company: Company):
        """Test deleting a company"""
        result = company_crud.delete(db_session, sample_company.id)
        
        assert result is True
        assert company_crud.get_by_id(db_session, sample_company.id) is None
    
    def test_delete_company_not_found(self, db_session: Session):
        """Test deleting non-existent company"""
        result = company_crud.delete(db_session, 99999)
        assert result is False
    
    def test_toggle_active(self, db_session: Session, sample_company: Company):
        """Test toggling company active status"""
        assert sample_company.is_active is True
        
        # Toggle off
        toggled = company_crud.toggle_active(db_session, sample_company.id)
        assert toggled.is_active is False
        
        # Toggle on
        toggled = company_crud.toggle_active(db_session, sample_company.id)
        assert toggled.is_active is True
