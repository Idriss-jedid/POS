"""
Integration Tests for Category API Endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestCategoryEndpoints:
    """Integration tests for /categories endpoints"""
    
    def test_create_category(self, client: TestClient):
        """Test POST /categories"""
        response = client.post(
            "/categories/",
            json={
                "name": "Electronics",
                "code": "ELEC001",
                "category_type": "ELECTRONICS",
                "description": "Electronic products"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Electronics"
        assert data["data"]["category_type"] == "ELECTRONICS"
    
    def test_create_category_duplicate_code(self, client: TestClient):
        """Test creating category with duplicate code"""
        client.post(
            "/categories/",
            json={"name": "Cat 1", "code": "DUP001", "category_type": "OTHER"}
        )
        
        response = client.post(
            "/categories/",
            json={"name": "Cat 2", "code": "DUP001", "category_type": "OTHER"}
        )
        
        assert response.status_code == 409
    
    def test_get_categories(self, client: TestClient):
        """Test GET /categories"""
        client.post(
            "/categories/",
            json={"name": "Category A", "code": "CATA", "category_type": "ELECTRONICS"}
        )
        client.post(
            "/categories/",
            json={"name": "Category B", "code": "CATB", "category_type": "FOOD_BEVERAGE"}
        )
        
        response = client.get("/categories/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
    
    def test_get_categories_by_type(self, client: TestClient):
        """Test GET /categories with category_type filter"""
        client.post(
            "/categories/",
            json={"name": "Electronics", "code": "ELEC", "category_type": "ELECTRONICS"}
        )
        client.post(
            "/categories/",
            json={"name": "Food", "code": "FOOD", "category_type": "FOOD_BEVERAGE"}
        )
        
        response = client.get("/categories/?category_type=ELECTRONICS")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["category_type"] == "ELECTRONICS"
    
    def test_get_category_types(self, client: TestClient):
        """Test GET /categories/types"""
        response = client.get("/categories/types")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
        # Check that ELECTRONICS is in the types
        types = [t["value"] for t in data["data"]]
        assert "ELECTRONICS" in types
    
    def test_get_category_by_id(self, client: TestClient):
        """Test GET /categories/{id}"""
        create_response = client.post(
            "/categories/",
            json={"name": "Test Category", "code": "TEST001", "category_type": "OTHER"}
        )
        category_id = create_response.json()["data"]["id"]
        
        response = client.get(f"/categories/{category_id}")
        
        assert response.status_code == 200
        assert response.json()["data"]["id"] == category_id
    
    def test_update_category(self, client: TestClient):
        """Test PUT /categories/{id}"""
        create_response = client.post(
            "/categories/",
            json={"name": "Original", "code": "ORIG001", "category_type": "OTHER"}
        )
        category_id = create_response.json()["data"]["id"]
        
        response = client.put(
            f"/categories/{category_id}",
            json={"name": "Updated Category", "description": "New description"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Updated Category"
        assert data["data"]["description"] == "New description"
    
    def test_toggle_category_active(self, client: TestClient):
        """Test PATCH /categories/{id}/toggle-active"""
        create_response = client.post(
            "/categories/",
            json={"name": "Active Cat", "code": "ACT001", "category_type": "OTHER"}
        )
        category_id = create_response.json()["data"]["id"]
        
        response = client.patch(f"/categories/{category_id}/toggle-active")
        
        assert response.status_code == 200
        assert response.json()["data"]["is_active"] is False
    
    def test_delete_category(self, client: TestClient):
        """Test DELETE /categories/{id}"""
        create_response = client.post(
            "/categories/",
            json={"name": "To Delete", "code": "DEL001", "category_type": "OTHER"}
        )
        category_id = create_response.json()["data"]["id"]
        
        response = client.delete(f"/categories/{category_id}")
        
        assert response.status_code == 204
