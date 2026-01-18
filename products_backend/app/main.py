from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import company_router, category_router, product_router
from .database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Products Management API",
    description="""
    Professional CRUD API for Products Management with:
    - **Companies/Suppliers**: Manage product suppliers
    - **Categories**: Organize products by categories
    - **Products**: Full CRUD with CSV bulk import
    - **Stock Management**: Track inventory levels
    """,
    version="2.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(company_router)
app.include_router(category_router)
app.include_router(product_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to Products Management API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "companies": "/companies",
            "categories": "/categories",
            "products": "/products",
            "csv_import": "/products/import-csv",
            "csv_template": "/products/export/csv-template",
        },
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "version": "2.0.0"}
