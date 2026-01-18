from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import company_crud
from app.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyOut,
    CompanyWithProductCount,
    CompanyWithProducts,
    DataResponse,
    ListResponse,
    PaginatedResponse,
)

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/", response_model=DataResponse[CompanyOut], status_code=status.HTTP_201_CREATED)
def create_company(company_data: CompanyCreate, db: Session = Depends(get_db)):
    """Create a new company/supplier"""
    # Check if code already exists
    existing = company_crud.get_by_code(db, company_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with code '{company_data.code}' already exists"
        )
    
    # Check if name already exists
    existing_name = company_crud.get_by_name(db, company_data.name)
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with name '{company_data.name}' already exists"
        )
    
    company = company_crud.create(db, company_data)
    return DataResponse(
        success=True,
        message="Company created successfully",
        data=company
    )


@router.get("/", response_model=PaginatedResponse[CompanyWithProductCount])
def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all companies with pagination and filters"""
    companies = company_crud.get_all(
        db, 
        skip=skip, 
        limit=limit, 
        is_active=is_active, 
        search=search
    )
    total = company_crud.count(db, is_active=is_active, search=search)
    
    return PaginatedResponse(
        success=True,
        message="Companies retrieved successfully",
        data=companies,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        total_pages=(total + limit - 1) // limit
    )


@router.get("/{company_id}", response_model=DataResponse[CompanyWithProductCount])
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get a company by ID"""
    company = company_crud.get_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )
    
    return DataResponse(
        success=True,
        message="Company retrieved successfully",
        data=company
    )


@router.put("/{company_id}", response_model=DataResponse[CompanyOut])
def update_company(
    company_id: int, 
    company_data: CompanyUpdate, 
    db: Session = Depends(get_db)
):
    """Update a company"""
    company = company_crud.update(db, company_id, company_data)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )
    
    return DataResponse(
        success=True,
        message="Company updated successfully",
        data=company
    )


@router.patch("/{company_id}/toggle-active", response_model=DataResponse[CompanyOut])
def toggle_company_active(company_id: int, db: Session = Depends(get_db)):
    """Toggle company active status"""
    company = company_crud.toggle_active(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )
    
    status_text = "activated" if company.is_active else "deactivated"
    return DataResponse(
        success=True,
        message=f"Company {status_text} successfully",
        data=company
    )


@router.get("/{company_id}/products", response_model=DataResponse[CompanyWithProducts])
def get_company_with_products(company_id: int, db: Session = Depends(get_db)):
    """Get a company with all its products (JOIN relationship)"""
    company = company_crud.get_by_id(db, company_id, with_products=True)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )
    
    return DataResponse(
        success=True,
        message=f"Company with {len(company.products)} products retrieved successfully",
        data=company
    )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """Delete a company (only if no products are linked)"""
    company = company_crud.get_by_id(db, company_id, with_products=True)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )
    
    if company.products:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete company with {len(company.products)} linked products. Deactivate it instead."
        )
    
    company_crud.delete(db, company_id)
    return None
