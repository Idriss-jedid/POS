import csv
import io
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import product_crud, company_crud, category_crud
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductOut,
    ProductWithRelations,
    ProductCSVRow,
    CSVImportResult,
    DataResponse,
    ListResponse,
    PaginatedResponse,
)
from app.enums import ProductStatus, UnitType

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=DataResponse[ProductOut], status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    # Check if SKU already exists
    existing = product_crud.get_by_sku(db, product_data.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_data.sku}' already exists"
        )
    
    # Check if barcode already exists (if provided)
    if product_data.barcode:
        existing_barcode = product_crud.get_by_barcode(db, product_data.barcode)
        if existing_barcode:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with barcode '{product_data.barcode}' already exists"
            )
    
    # Verify company exists
    if product_data.company_id:
        company = company_crud.get_by_id(db, product_data.company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {product_data.company_id} not found"
            )
    
    # Verify category exists
    if product_data.category_id:
        category = category_crud.get_by_id(db, product_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {product_data.category_id} not found"
            )
    
    product = product_crud.create(db, product_data)
    return DataResponse(
        success=True,
        message="Product created successfully",
        data=product
    )


@router.get("/", response_model=PaginatedResponse[ProductWithRelations])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    company_id: Optional[int] = None,
    category_id: Optional[int] = None,
    status: Optional[ProductStatus] = None,
    search: Optional[str] = None,
    low_stock_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all products with pagination and filters"""
    products = product_crud.get_all(
        db, 
        skip=skip, 
        limit=limit, 
        company_id=company_id,
        category_id=category_id,
        status=status,
        search=search,
        low_stock_only=low_stock_only,
        with_relations=True
    )
    total = product_crud.count(
        db, 
        company_id=company_id,
        category_id=category_id,
        status=status,
        search=search,
        low_stock_only=low_stock_only
    )
    
    return PaginatedResponse(
        success=True,
        message="Products retrieved successfully",
        data=products,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        total_pages=(total + limit - 1) // limit
    )


@router.get("/status-options", response_model=ListResponse[dict])
def get_product_status_options():
    """Get all available product statuses"""
    statuses = [{"value": s.value, "name": s.name.replace("_", " ").title()} for s in ProductStatus]
    return ListResponse(
        success=True,
        message="Product statuses retrieved successfully",
        data=statuses
    )


@router.get("/unit-options", response_model=ListResponse[dict])
def get_product_unit_options():
    """Get all available unit types"""
    units = [{"value": u.value, "name": u.name.replace("_", " ").title()} for u in UnitType]
    return ListResponse(
        success=True,
        message="Unit types retrieved successfully",
        data=units
    )


@router.get("/statistics", response_model=DataResponse[dict])
def get_product_statistics(
    company_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get product statistics"""
    stats = product_crud.get_statistics(db, company_id=company_id)
    return DataResponse(
        success=True,
        message="Statistics retrieved successfully",
        data=stats
    )


@router.get("/{product_id}", response_model=DataResponse[ProductWithRelations])
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a product by ID"""
    product = product_crud.get_by_id(db, product_id, with_relations=True)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    return DataResponse(
        success=True,
        message="Product retrieved successfully",
        data=product
    )


@router.put("/{product_id}", response_model=DataResponse[ProductOut])
def update_product(
    product_id: int, 
    product_data: ProductUpdate, 
    db: Session = Depends(get_db)
):
    """Update a product"""
    product = product_crud.update(db, product_id, product_data)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    return DataResponse(
        success=True,
        message="Product updated successfully",
        data=product
    )


@router.patch("/{product_id}/quantity", response_model=DataResponse[ProductOut])
def update_product_quantity(
    product_id: int,
    quantity_change: int = Query(..., description="Positive to add, negative to subtract"),
    db: Session = Depends(get_db)
):
    """Update product quantity (add or subtract stock)"""
    product = product_crud.update_quantity(db, product_id, quantity_change)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    
    return DataResponse(
        success=True,
        message=f"Product quantity updated by {quantity_change}",
        data=product
    )


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    success = product_crud.delete(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return None


@router.post("/import-csv", response_model=DataResponse[CSVImportResult])
async def import_products_from_csv(
    file: UploadFile = File(..., description="CSV file containing products"),
    company_id: int = Form(..., description="Company/Supplier ID for all imported products"),
    skip_duplicates: bool = Form(True, description="Skip duplicate SKUs instead of failing"),
    db: Session = Depends(get_db)
):
    """
    Import products from a CSV file.
    
    The CSV should have these columns (header row required):
    - name (required): Product name
    - sku (required): Unique product SKU
    - category_id (required): Category ID for this product
    - barcode (optional): Product barcode
    - description (optional): Product description
    - cost_price (optional): Cost price (default: 0)
    - selling_price (optional): Selling price (default: 0)
    - quantity (optional): Initial quantity (default: 0)
    - min_stock_level (optional): Minimum stock alert level (default: 10)
    - unit (optional): Unit type (PIECE, KG, GRAM, etc., default: PIECE)
    - status (optional): Product status (ACTIVE, INACTIVE, etc., default: ACTIVE)
    - brand (optional): Brand name
    
    All imported products will be linked to the specified company. Each product can have its own category.
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    # Verify company exists
    company = company_crud.get_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )
    
    try:
        # Read CSV content
        content = await file.read()
        decoded_content = content.decode('utf-8-sig')  # Handle BOM
        csv_reader = csv.DictReader(io.StringIO(decoded_content))
        
        products: List[ProductCSVRow] = []
        row_errors: List[str] = []
        
        for idx, row in enumerate(csv_reader, start=2):  # Start at 2 (1 is header)
            try:
                # Clean and validate required fields
                name = row.get('name', '').strip()
                sku = row.get('sku', '').strip()
                category_id_str = row.get('category_id', '').strip()
                
                if not name:
                    row_errors.append(f"Row {idx}: Missing required field 'name'")
                    continue
                if not sku:
                    row_errors.append(f"Row {idx}: Missing required field 'sku'")
                    continue
                if not category_id_str:
                    row_errors.append(f"Row {idx}: Missing required field 'category_id'")
                    continue
                
                try:
                    category_id = int(category_id_str)
                except ValueError:
                    row_errors.append(f"Row {idx}: Invalid category_id '{category_id_str}'")
                    continue
                
                # Verify category exists
                category = category_crud.get_by_id(db, category_id)
                if not category:
                    row_errors.append(f"Row {idx}: Category with ID {category_id} not found")
                    continue
                
                # Parse optional numeric fields
                cost_price = float(row.get('cost_price', 0) or 0)
                selling_price = float(row.get('selling_price', 0) or 0)
                quantity = int(float(row.get('quantity', 0) or 0))
                min_stock_level = int(float(row.get('min_stock_level', 10) or 10))
                
                product_row = ProductCSVRow(
                    name=name,
                    sku=sku,
                    barcode=row.get('barcode', '').strip() or None,
                    description=row.get('description', '').strip() or None,
                    cost_price=cost_price,
                    selling_price=selling_price,
                    quantity=quantity,
                    min_stock_level=min_stock_level,
                    unit=row.get('unit', '').strip() or 'PIECE',
                    status=row.get('status', '').strip() or 'ACTIVE',
                    brand=row.get('brand', '').strip() or None,
                    category_id=category_id
                )
                products.append(product_row)
                
            except Exception as e:
                row_errors.append(f"Row {idx}: {str(e)}")
        
        if not products and row_errors:
            return DataResponse(
                success=False,
                message="No valid products found in CSV",
                data=CSVImportResult(
                    total_rows=0,
                    successful=0,
                    failed=len(row_errors),
                    skipped=0,
                    errors=row_errors,
                    created_product_ids=[]
                )
            )
        
        # Bulk import
        result = product_crud.bulk_import(
            db=db,
            products=products,
            company_id=company_id,
            skip_duplicates=skip_duplicates
        )
        
        # Add parsing errors to result
        result.errors = row_errors + result.errors
        result.failed += len(row_errors)
        result.total_rows += len(row_errors)
        
        return DataResponse(
            success=result.successful > 0,
            message=f"Imported {result.successful} products, {result.skipped} skipped, {result.failed} failed",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing CSV file: {str(e)}"
        )


@router.get("/export/csv-template", response_model=DataResponse[dict])
def get_csv_template():
    """Get the CSV template for product import"""
    template = {
        "columns": [
            {"name": "name", "required": True, "description": "Product name"},
            {"name": "sku", "required": True, "description": "Unique product SKU"},
            {"name": "barcode", "required": False, "description": "Product barcode (EAN/UPC)"},
            {"name": "description", "required": False, "description": "Product description"},
            {"name": "cost_price", "required": False, "description": "Cost price (default: 0)"},
            {"name": "selling_price", "required": False, "description": "Selling price (default: 0)"},
            {"name": "quantity", "required": False, "description": "Initial quantity (default: 0)"},
            {"name": "min_stock_level", "required": False, "description": "Min stock alert level (default: 10)"},
            {"name": "unit", "required": False, "description": "Unit type: PIECE, KG, GRAM, LITER, ML, METER, CM, BOX, PACK, DOZEN, SET (default: PIECE)"},
            {"name": "status", "required": False, "description": "Status: ACTIVE, INACTIVE, DISCONTINUED, OUT_OF_STOCK, PENDING (default: ACTIVE)"},
            {"name": "brand", "required": False, "description": "Brand name"},
        ],
        "sample_csv": "name,sku,barcode,description,cost_price,selling_price,quantity,min_stock_level,unit,status,brand\nProduct A,SKU001,123456789012,Description here,10.50,15.99,100,20,PIECE,ACTIVE,BrandX"
    }
    return DataResponse(
        success=True,
        message="CSV template retrieved successfully",
        data=template
    )
