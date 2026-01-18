"""
Integration Tests for Company API Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Company


class TestCompanyEndpoints:
    """Integration tests for /companies endpoints"""
    
    def test_create_company(self, client: TestClient):
        """Test POST /companies"""
        response = client.post(
            "/companies/",
            json={
                "name": "Test Company",
                "code": "TEST001",
                "email": "test@company.com",
                "phone": "+1234567890",
                "address": "123 Test Street"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Company"
        assert data["data"]["code"] == "TEST001"
        assert data["data"]["is_active"] is True
    
    def test_create_company_duplicate_code(self, client: TestClient):
        """Test creating company with duplicate code"""
        # Create first company
        client.post(
            "/companies/",
            json={"name": "Company 1", "code": "DUP001"}
        )
        
        # Try to create with same code
        response = client.post(
            "/companies/",
            json={"name": "Company 2", "code": "DUP001"}
        )
        
        assert response.status_code == 409
    
    def test_get_companies(self, client: TestClient):
        """Test GET /companies"""
        # Create some companies
        client.post("/companies/", json={"name": "Company A", "code": "COMA"})
        client.post("/companies/", json={"name": "Company B", "code": "COMB"})
        
        response = client.get("/companies/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total"] == 2
        assert len(data["data"]) == 2
    
    def test_get_companies_pagination(self, client: TestClient):
        """Test pagination on GET /companies"""
        # Create multiple companies
        for i in range(5):
            client.post(
                "/companies/",
                json={"name": f"Company {i}", "code": f"COM{i:03d}"}
            )
        
        response = client.get("/companies/?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["total"] == 5
        assert data["per_page"] == 2
    
    def test_get_companies_search(self, client: TestClient):
        """Test search on GET /companies"""
        client.post("/companies/", json={"name": "Apple Inc", "code": "APPLE"})
        client.post("/companies/", json={"name": "Microsoft", "code": "MSFT"})
        
        response = client.get("/companies/?search=Apple")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Apple Inc"
    
    def test_get_company_by_id(self, client: TestClient):
        """Test GET /companies/{id}"""
        # Create company
        create_response = client.post(
            "/companies/",
            json={"name": "Test Company", "code": "TEST001"}
        )
        company_id = create_response.json()["data"]["id"]
        
        response = client.get(f"/companies/{company_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == company_id
    
    def test_get_company_not_found(self, client: TestClient):
        """Test GET /companies/{id} with non-existent ID"""
        response = client.get("/companies/99999")
        
        assert response.status_code == 404
    
    def test_update_company(self, client: TestClient):
        """Test PUT /companies/{id}"""
        # Create company
        create_response = client.post(
            "/companies/",
            json={"name": "Original Name", "code": "ORIG001"}
        )
        company_id = create_response.json()["data"]["id"]
        
        response = client.put(
            f"/companies/{company_id}",
            json={"name": "Updated Name", "email": "updated@email.com"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Updated Name"
        assert data["data"]["email"] == "updated@email.com"
    
    def test_toggle_company_active(self, client: TestClient):
        """Test PATCH /companies/{id}/toggle-active"""
        # Create company
        create_response = client.post(
            "/companies/",
            json={"name": "Active Company", "code": "ACT001"}
        )
        company_id = create_response.json()["data"]["id"]
        
        # Toggle off
        response = client.patch(f"/companies/{company_id}/toggle-active")
        
        assert response.status_code == 200
        assert response.json()["data"]["is_active"] is False
        
        # Toggle on
        response = client.patch(f"/companies/{company_id}/toggle-active")
        assert response.json()["data"]["is_active"] is True
    
    def test_delete_company(self, client: TestClient):
        """Test DELETE /companies/{id}"""
        # Create company
        create_response = client.post(
            "/companies/",
            json={"name": "To Delete", "code": "DEL001"}
        )
        company_id = create_response.json()["data"]["id"]
        
        response = client.delete(f"/companies/{company_id}")
        
        assert response.status_code == 204
        
        # Verify deleted
        get_response = client.get(f"/companies/{company_id}")
        assert get_response.status_code == 404
