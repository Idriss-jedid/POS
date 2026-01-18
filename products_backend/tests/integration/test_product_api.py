"""
Integration Tests for Product API Endpoints
"""
import pytest
import io
from fastapi.testclient import TestClient


class TestProductEndpoints:
    """Integration tests for /products endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient):
        """Setup company and category for product tests"""
        # Create company
        company_response = client.post(
            "/companies/",
            json={"name": "Test Company", "code": "TESTCO"}
        )
        self.company_id = company_response.json()["data"]["id"]
        
        # Create category
        category_response = client.post(
            "/categories/",
            json={
                "name": "Test Category",
                "code": "TESTCAT",
                "category_type": "ELECTRONICS"
            }
        )
        self.category_id = category_response.json()["data"]["id"]
    
    def test_create_product(self, client: TestClient):
        """Test POST /products"""
        response = client.post(
            "/products/",
            json={
                "name": "Test Product",
                "sku": "SKU001",
                "barcode": "1234567890123",
                "description": "Test description",
                "cost_price": 10.00,
                "selling_price": 15.99,
                "quantity": 100,
                "min_stock_level": 10,
                "unit": "PIECE",
                "status": "ACTIVE",
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Product"
        assert data["data"]["sku"] == "SKU001"
    
    def test_create_product_duplicate_sku(self, client: TestClient):
        """Test creating product with duplicate SKU"""
        # Create first product
        client.post(
            "/products/",
            json={
                "name": "Product 1",
                "sku": "DUPSKU",
                "cost_price": 10.00,
                "selling_price": 15.00,
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        
        # Try duplicate
        response = client.post(
            "/products/",
            json={
                "name": "Product 2",
                "sku": "DUPSKU",
                "cost_price": 10.00,
                "selling_price": 15.00,
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        
        assert response.status_code == 409
    
    def test_get_products(self, client: TestClient):
        """Test GET /products"""
        # Create products
        for i in range(3):
            client.post(
                "/products/",
                json={
                    "name": f"Product {i}",
                    "sku": f"SKU{i:03d}",
                    "cost_price": 10.00,
                    "selling_price": 15.00,
                    "company_id": self.company_id,
                    "category_id": self.category_id
                }
            )
        
        response = client.get("/products/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
    
    def test_get_products_by_company(self, client: TestClient):
        """Test GET /products filtered by company"""
        # Create product
        client.post(
            "/products/",
            json={
                "name": "Company Product",
                "sku": "COMPROD",
                "cost_price": 10.00,
                "selling_price": 15.00,
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        
        response = client.get(f"/products/?company_id={self.company_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
    
    def test_get_products_by_category(self, client: TestClient):
        """Test GET /products filtered by category"""
        client.post(
            "/products/",
            json={
                "name": "Category Product",
                "sku": "CATPROD",
                "cost_price": 10.00,
                "selling_price": 15.00,
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        
        response = client.get(f"/products/?category_id={self.category_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
    
    def test_get_products_search(self, client: TestClient):
        """Test GET /products with search"""
        client.post(
            "/products/",
            json={
                "name": "Apple iPhone",
                "sku": "IPHONE",
                "cost_price": 500.00,
                "selling_price": 699.00,
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        client.post(
            "/products/",
            json={
                "name": "Samsung Galaxy",
                "sku": "GALAXY",
                "cost_price": 400.00,
                "selling_price": 599.00,
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        
        response = client.get("/products/?search=iPhone")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Apple iPhone"
    
    def test_get_product_status_options(self, client: TestClient):
        """Test GET /products/status-options"""
        response = client.get("/products/status-options")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        statuses = [s["value"] for s in data["data"]]
        assert "ACTIVE" in statuses
        assert "OUT_OF_STOCK" in statuses
    
    def test_get_product_unit_options(self, client: TestClient):
        """Test GET /products/unit-options"""
        response = client.get("/products/unit-options")
        
        assert response.status_code == 200
        data = response.json()
        units = [u["value"] for u in data["data"]]
        assert "PIECE" in units
        assert "KG" in units
    
    def test_get_product_statistics(self, client: TestClient):
        """Test GET /products/statistics"""
        # Create some products
        client.post(
            "/products/",
            json={
                "name": "Product",
                "sku": "STAT001",
                "cost_price": 10.00,
                "selling_price": 15.00,
                "quantity": 100,
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        
        response = client.get("/products/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_products" in data["data"]
        assert "active_products" in data["data"]
        assert "out_of_stock" in data["data"]
    
    def test_get_product_by_id(self, client: TestClient):
        """Test GET /products/{id}"""
        create_response = client.post(
            "/products/",
            json={
                "name": "Single Product",
                "sku": "SINGLE001",
                "cost_price": 10.00,
                "selling_price": 15.00,
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        product_id = create_response.json()["data"]["id"]
        
        response = client.get(f"/products/{product_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == product_id
        # Should include relations
        assert "company" in data["data"]
        assert "category" in data["data"]
    
    def test_update_product(self, client: TestClient):
        """Test PUT /products/{id}"""
        create_response = client.post(
            "/products/",
            json={
                "name": "Original",
                "sku": "UPDATE001",
                "cost_price": 10.00,
                "selling_price": 15.00,
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        product_id = create_response.json()["data"]["id"]
        
        response = client.put(
            f"/products/{product_id}",
            json={"name": "Updated Name", "selling_price": 20.00}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Updated Name"
        assert data["data"]["selling_price"] == 20.00
    
    def test_update_product_quantity(self, client: TestClient):
        """Test PATCH /products/{id}/quantity"""
        create_response = client.post(
            "/products/",
            json={
                "name": "Stock Product",
                "sku": "STOCK001",
                "cost_price": 10.00,
                "selling_price": 15.00,
                "quantity": 100,
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        product_id = create_response.json()["data"]["id"]
        
        # Add stock
        response = client.patch(f"/products/{product_id}/quantity?quantity_change=50")
        
        assert response.status_code == 200
        assert response.json()["data"]["quantity"] == 150
        
        # Remove stock
        response = client.patch(f"/products/{product_id}/quantity?quantity_change=-30")
        assert response.json()["data"]["quantity"] == 120
    
    def test_delete_product(self, client: TestClient):
        """Test DELETE /products/{id}"""
        create_response = client.post(
            "/products/",
            json={
                "name": "To Delete",
                "sku": "DEL001",
                "cost_price": 10.00,
                "selling_price": 15.00,
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        product_id = create_response.json()["data"]["id"]
        
        response = client.delete(f"/products/{product_id}")
        
        assert response.status_code == 204
    
    def test_get_csv_template(self, client: TestClient):
        """Test GET /products/export/csv-template"""
        response = client.get("/products/export/csv-template")
        
        assert response.status_code == 200
        data = response.json()
        assert "columns" in data["data"]
        assert "sample_csv" in data["data"]
    
    def test_import_csv(self, client: TestClient):
        """Test POST /products/import-csv"""
        csv_content = """name,sku,barcode,description,cost_price,selling_price,quantity,min_stock_level,unit,status,brand
Product A,SKU-IMP001,1111111111111,Product A desc,10.50,15.99,100,20,PIECE,ACTIVE,BrandA
Product B,SKU-IMP002,2222222222222,Product B desc,20.00,29.99,50,10,KG,ACTIVE,BrandB"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/products/import-csv",
            files={"file": ("products.csv", csv_file, "text/csv")},
            data={
                "company_id": self.company_id,
                "category_id": self.category_id,
                "skip_duplicates": "true"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["successful"] == 2
        assert data["data"]["failed"] == 0
    
    def test_import_csv_skip_duplicates(self, client: TestClient):
        """Test CSV import skipping duplicates"""
        # Create existing product
        client.post(
            "/products/",
            json={
                "name": "Existing",
                "sku": "EXIST001",
                "cost_price": 10.00,
                "selling_price": 15.00,
                "company_id": self.company_id,
                "category_id": self.category_id
            }
        )
        
        csv_content = """name,sku,cost_price,selling_price
Existing Product,EXIST001,10.00,15.00
New Product,NEW001,20.00,30.00"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post(
            "/products/import-csv",
            files={"file": ("products.csv", csv_file, "text/csv")},
            data={
                "company_id": self.company_id,
                "category_id": self.category_id,
                "skip_duplicates": "true"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["successful"] == 1
        assert data["data"]["skipped"] == 1


class TestProductEndpointsValidation:
    """Test validation for product endpoints"""
    
    def test_create_product_invalid_company(self, client: TestClient):
        """Test creating product with non-existent company"""
        response = client.post(
            "/products/",
            json={
                "name": "Test",
                "sku": "TEST001",
                "cost_price": 10.00,
                "selling_price": 15.00,
                "company_id": 99999,
                "category_id": 1
            }
        )
        
        assert response.status_code == 404
    
    def test_import_csv_invalid_file_type(self, client: TestClient):
        """Test importing non-CSV file"""
        txt_content = "This is not a CSV file"
        txt_file = io.BytesIO(txt_content.encode('utf-8'))
        
        response = client.post(
            "/products/import-csv",
            files={"file": ("products.txt", txt_file, "text/plain")},
            data={
                "company_id": 1,
                "category_id": 1
            }
        )
        
        assert response.status_code == 400
