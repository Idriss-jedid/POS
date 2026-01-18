# Products Management API

A professional **FastAPI** backend for product inventory management with support for companies/suppliers, categories, and CSV bulk import.

## 🏗️ Architecture

```
products_backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection and session
│   ├── enums/               # Enumeration types
│   │   ├── __init__.py
│   │   ├── product_status.py
│   │   ├── category_type.py
│   │   └── unit_type.py
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── category.py
│   │   └── product.py
│   ├── schemas/             # Pydantic schemas (DTOs)
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── category.py
│   │   ├── product.py
│   │   └── response.py
│   ├── crud/                # CRUD operations (Data Access Layer)
│   │   ├── __init__.py
│   │   ├── company.py
│   │   ├── category.py
│   │   └── product.py
│   └── routers/             # API route handlers
│       ├── __init__.py
│       ├── company.py
│       ├── category.py
│       └── product.py
├── tests/                   # Test suite
│   ├── conftest.py          # Test fixtures
│   ├── unit/                # Unit tests
│   │   ├── test_company_crud.py
│   │   ├── test_category_crud.py
│   │   └── test_product_crud.py
│   └── integration/         # Integration tests
│       ├── test_company_api.py
│       ├── test_category_api.py
│       └── test_product_api.py
├── requirements.txt
├── pytest.ini
└── sample_products.csv      # Sample CSV for testing import
```

## 🚀 Features

### Companies/Suppliers
- Manage product suppliers
- Track contact information
- Active/inactive status
- Products linked to companies

### Categories
- Organize products by type
- 10+ predefined category types
- Custom descriptions
- Product count tracking

### Products
- Full CRUD operations
- SKU and barcode management
- Cost and selling price tracking
- Stock quantity management
- Low stock alerts
- CSV bulk import

## 📊 Database Schema

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Companies  │     │  Products   │     │ Categories  │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ id          │◄────│ company_id  │     │ id          │
│ name        │     │ category_id │────►│ name        │
│ code        │     │ name        │     │ code        │
│ email       │     │ sku         │     │ category_type│
│ phone       │     │ barcode     │     │ description │
│ address     │     │ description │     │ is_active   │
│ website     │     │ cost_price  │     │ created_at  │
│ contact_person│   │ selling_price│    │ updated_at  │
│ is_active   │     │ quantity    │     └─────────────┘
│ created_at  │     │ min_stock_level│
│ updated_at  │     │ unit        │
└─────────────┘     │ status      │
                    │ brand       │
                    │ created_at  │
                    │ updated_at  │
                    └─────────────┘
```

## 🔧 Installation

1. **Clone and navigate to the project**
```bash
cd products_backend
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure database**

Create a PostgreSQL database named `products_db` and update `app/config.py` if needed:
```python
DATABASE_URL = "postgresql://postgres:minirag2222@localhost:5432/products_db"
```

5. **Run the server**
```bash
uvicorn app.main:app --reload --port 8001
```

## 📡 API Endpoints

### Root
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |

### Companies
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/companies/` | Create company |
| GET | `/companies/` | List companies (paginated) |
| GET | `/companies/{id}` | Get company by ID |
| PUT | `/companies/{id}` | Update company |
| PATCH | `/companies/{id}/toggle-active` | Toggle active status |
| DELETE | `/companies/{id}` | Delete company |

### Categories
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/categories/` | Create category |
| GET | `/categories/` | List categories (paginated) |
| GET | `/categories/types` | Get category types |
| GET | `/categories/{id}` | Get category by ID |
| PUT | `/categories/{id}` | Update category |
| PATCH | `/categories/{id}/toggle-active` | Toggle active status |
| DELETE | `/categories/{id}` | Delete category |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/products/` | Create product |
| GET | `/products/` | List products (paginated, filterable) |
| GET | `/products/status-options` | Get product statuses |
| GET | `/products/unit-options` | Get unit types |
| GET | `/products/statistics` | Get product stats |
| GET | `/products/{id}` | Get product by ID |
| PUT | `/products/{id}` | Update product |
| PATCH | `/products/{id}/quantity` | Update stock quantity |
| DELETE | `/products/{id}` | Delete product |
| POST | `/products/import-csv` | Bulk import from CSV |
| GET | `/products/export/csv-template` | Get CSV template |

## 📤 CSV Import

### CSV Format
```csv
name,sku,barcode,description,cost_price,selling_price,quantity,min_stock_level,unit,status,brand
Product A,SKU001,1234567890123,Description,10.50,15.99,100,20,PIECE,ACTIVE,BrandX
```

### Required Fields
- `name`: Product name
- `sku`: Unique product SKU

### Optional Fields
- `barcode`: Product barcode
- `description`: Product description
- `cost_price`: Cost price (default: 0)
- `selling_price`: Selling price (default: 0)
- `quantity`: Initial quantity (default: 0)
- `min_stock_level`: Low stock alert level (default: 10)
- `unit`: PIECE, KG, GRAM, LITER, ML, METER, CM, BOX, PACK, DOZEN, SET
- `status`: ACTIVE, INACTIVE, DISCONTINUED, OUT_OF_STOCK, PENDING
- `brand`: Brand name

### Import via cURL
```bash
curl -X POST "http://localhost:8000/products/import-csv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_products.csv" \
  -F "company_id=1" \
  -F "category_id=1" \
  -F "skip_duplicates=true"
```

## 🧪 Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/unit/test_product_crud.py -v
```

### Run integration tests only
```bash
pytest tests/integration/ -v
```

## 📋 Enums

### ProductStatus
| Value | Description |
|-------|-------------|
| ACTIVE | Available for sale |
| INACTIVE | Temporarily unavailable |
| DISCONTINUED | No longer sold |
| OUT_OF_STOCK | Zero quantity |
| PENDING | Awaiting approval |

### CategoryType
| Value | Description |
|-------|-------------|
| ELECTRONICS | Electronic devices |
| CLOTHING | Apparel |
| FOOD_BEVERAGE | Food & drinks |
| HEALTH_BEAUTY | Health & beauty |
| HOME_GARDEN | Home & garden |
| SPORTS_OUTDOORS | Sports equipment |
| TOYS_GAMES | Toys & games |
| AUTOMOTIVE | Auto parts |
| BOOKS_MEDIA | Books & media |
| OFFICE_SUPPLIES | Office supplies |
| OTHER | Miscellaneous |

### UnitType
| Value | Description |
|-------|-------------|
| PIECE | Individual item |
| KG | Kilogram |
| GRAM | Gram |
| LITER | Liter |
| ML | Milliliter |
| METER | Meter |
| CM | Centimeter |
| BOX | Box |
| PACK | Pack |
| DOZEN | Dozen (12) |
| SET | Set |

## 🔒 Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Paginated Response
```json
{
  "success": true,
  "message": "Items retrieved",
  "data": [ ... ],
  "total": 100,
  "page": 1,
  "per_page": 50,
  "total_pages": 2
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## 🛠️ Development

### Tech Stack
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and serialization
- **PostgreSQL** - Database
- **pytest** - Testing framework

### Code Style
- Type hints everywhere
- Docstrings for all public methods
- PEP 8 compliant
- Separation of concerns (routers, crud, models, schemas)

## 📝 License

MIT License
