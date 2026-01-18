from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import category_crud
from app.schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryOut,
    CategoryWithProductCount,
    CategoryWithProducts,
    DataResponse,
    ListResponse,
    PaginatedResponse,
)
from app.enums import CategoryType

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=DataResponse[CategoryOut], status_code=status.HTTP_201_CREATED)
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new product category"""
    # Check if code already exists
    existing = category_crud.get_by_code(db, category_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with code '{category_data.code}' already exists"
        )
    
    # Check if name already exists
    existing_name = category_crud.get_by_name(db, category_data.name)
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with name '{category_data.name}' already exists"
        )
    
    category = category_crud.create(db, category_data)
    return DataResponse(
        success=True,
        message="Category created successfully",
        data=category
    )


@router.get("/", response_model=PaginatedResponse[CategoryWithProductCount])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = None,
    category_type: Optional[CategoryType] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all categories with pagination and filters"""
    categories = category_crud.get_all(
        db, 
        skip=skip, 
        limit=limit, 
        is_active=is_active, 
        category_type=category_type,
        search=search
    )
    total = category_crud.count(db, is_active=is_active, category_type=category_type, search=search)
    
    return PaginatedResponse(
        success=True,
        message="Categories retrieved successfully",
        data=categories,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        total_pages=(total + limit - 1) // limit
    )


@router.get("/types", response_model=ListResponse[dict])
def get_category_types():
    """Get all available category types"""
    types = [{"value": t.value, "name": t.name} for t in CategoryType]
    return ListResponse(
        success=True,
        message="Category types retrieved successfully",
        data=types
    )


@router.get("/{category_id}", response_model=DataResponse[CategoryWithProductCount])
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a category by ID"""
    category = category_crud.get_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    return DataResponse(
        success=True,
        message="Category retrieved successfully",
        data=category
    )


@router.put("/{category_id}", response_model=DataResponse[CategoryOut])
def update_category(
    category_id: int, 
    category_data: CategoryUpdate, 
    db: Session = Depends(get_db)
):
    """Update a category"""
    category = category_crud.update(db, category_id, category_data)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    return DataResponse(
        success=True,
        message="Category updated successfully",
        data=category
    )


@router.patch("/{category_id}/toggle-active", response_model=DataResponse[CategoryOut])
def toggle_category_active(category_id: int, db: Session = Depends(get_db)):
    """Toggle category active status"""
    category = category_crud.toggle_active(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    status_text = "activated" if category.is_active else "deactivated"
    return DataResponse(
        success=True,
        message=f"Category {status_text} successfully",
        data=category
    )


@router.get("/{category_id}/products", response_model=DataResponse[CategoryWithProducts])
def get_category_with_products(category_id: int, db: Session = Depends(get_db)):
    """Get a category with all its products (JOIN relationship)"""
    category = category_crud.get_by_id(db, category_id, with_products=True)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    return DataResponse(
        success=True,
        message=f"Category with {len(category.products)} products retrieved successfully",
        data=category
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category (only if no products are linked)"""
    category = category_crud.get_by_id(db, category_id, with_products=True)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    if category.products:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete category with {len(category.products)} linked products. Deactivate it instead."
        )
    
    category_crud.delete(db, category_id)
    return None
