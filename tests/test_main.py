"""
Test suite for Multi-Tenant Schema Translator (Refactored)
Tests updated to work with new modular architecture
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.models.schemas import SchemaRepository
from app.services import SchemaMapper, QueryExecutor, LLMService
from app.api.dependencies import get_mapper, get_executor, get_llm

# Create test client (positional argument, not keyword)
client = TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints"""

    def test_root_endpoint(self):
        """Test the root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Multi-Tenant Schema Translator API" in data["message"]
        assert "endpoints" in data

    def test_get_customers(self):
        """Test retrieving list of customer schemas"""
        response = client.get("/customers")
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        assert len(data["customers"]) == 4

        # Check customer_a structure
        customer_a = next(
            (c for c in data["customers"] if c["customer_id"] == "customer_a"),
            None
        )
        assert customer_a is not None
        assert customer_a["database"] == "customer_a_db"
        assert "contracts" in customer_a["tables"]

    def test_get_specific_schema(self):
        """Test retrieving a specific customer's schema"""
        response = client.get("/schema/customer_a")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "customer_a"
        assert "schema" in data
        assert "contracts" in data["schema"]
        assert "canonical_mapping_hint" in data

    def test_invalid_customer_schema(self):
        """Test error handling for invalid customer"""
        response = client.get("/schema/invalid_customer")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestQueryEndpoint:
    """Test query endpoint with dependency injection"""

    def test_query_with_mocked_services(self):
        """Test query endpoint with mocked services"""

        # Create mock mapper
        mock_mapper = MagicMock(spec=SchemaMapper)
        mock_mapper.get_mapping = AsyncMock(return_value={
            "sql_query": "SELECT * FROM contracts WHERE status = 'Active'",
            "mappings": {"status": "status"},
            "calculations": {},
            "explanation": "Querying active contracts"
        })

        # Create mock executor
        mock_executor = MagicMock(spec=QueryExecutor)
        mock_executor.execute_query.return_value = [
            {
                "contract_id": 1,
                "contract_name": "Test Contract",
                "status": "Active"
            }
        ]

        # Override dependencies
        app.dependency_overrides[get_mapper] = lambda: mock_mapper
        app.dependency_overrides[get_executor] = lambda: mock_executor

        try:
            # Make request
            response = client.post("/query", json={
                "question": "Show me all active contracts",
                "customer_id": "customer_a"
            })

            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "customer_schemas_used" in data
            assert "customer_a" in data["customer_schemas_used"]

        finally:
            # Clean up overrides
            app.dependency_overrides.clear()

    def test_query_all_customers(self):
        """Test querying across all customers"""

        # Create mock mapper
        mock_mapper = MagicMock(spec=SchemaMapper)
        mock_mapper.get_mapping = AsyncMock(return_value={
            "sql_query": "SELECT * FROM contracts",
            "mappings": {},
            "calculations": {},
            "explanation": "Querying all contracts"
        })

        # Create mock executor
        mock_executor = MagicMock(spec=QueryExecutor)
        mock_executor.execute_query.return_value = [
            {"contract_id": 1, "contract_name": "Test"}
        ]

        # Override dependencies
        app.dependency_overrides[get_mapper] = lambda: mock_mapper
        app.dependency_overrides[get_executor] = lambda: mock_executor

        try:
            response = client.post("/query", json={
                "question": "Show me all contracts",
                "customer_id": None
            })

            assert response.status_code == 200
            data = response.json()
            # Should query all 4 customers
            assert len(data["customer_schemas_used"]) == 4

        finally:
            app.dependency_overrides.clear()


class TestSchemaRepository:
    """Test schema repository"""

    def test_get_schema(self):
        """Test retrieving a schema"""
        from app.models.schemas import get_schema_repository

        repo = get_schema_repository()
        schema = repo.get_schema("customer_a")

        assert "connection" in schema
        assert "tables" in schema
        assert "contracts" in schema["tables"]

    def test_get_canonical_schema(self):
        """Test retrieving canonical schema"""
        from app.models.schemas import get_schema_repository

        repo = get_schema_repository()
        canonical = repo.get_canonical_schema()

        assert "contract" in canonical
        assert "id" in canonical["contract"]
        assert "total_value" in canonical["contract"]

    def test_list_customers(self):
        """Test listing all customers"""
        from app.models.schemas import get_schema_repository

        repo = get_schema_repository()
        customers = repo.list_customers()

        assert len(customers) == 4
        assert "customer_a" in customers
        assert "customer_b" in customers

    def test_customer_not_found(self):
        """Test error when customer not found"""
        from app.models.schemas import get_schema_repository
        from app.core.exceptions import CustomerNotFoundError

        repo = get_schema_repository()

        with pytest.raises(CustomerNotFoundError) as exc_info:
            repo.get_schema("invalid_customer")

        assert "invalid_customer" in str(exc_info.value)


class TestResponseFormatter:
    """Test response formatter"""

    def test_format_response(self):
        """Test formatting of query results"""
        from app.services.response_formatter import ResponseFormatter

        results = [
            {
                "_customer_id": "customer_a",
                "contract_name": "Test Contract",
                "value": 100000
            },
            {
                "_customer_id": "customer_b",
                "title": "Another Contract",
                "annual_value": 50000
            }
        ]

        mappings = {
            "customer_a": {"explanation": "Using lifetime value"},
            "customer_b": {"explanation": "Using annual value"}
        }

        formatter = ResponseFormatter()
        response = formatter.format_query_response(
            "Show all contracts",
            results,
            mappings
        )

        assert "Found 2 contracts" in response
        assert "Customer A" in response
        assert "Customer B" in response
        assert "Using lifetime value" in response
        assert "Using annual value" in response

    def test_empty_results(self):
        """Test formatting when no results"""
        from app.services.response_formatter import ResponseFormatter

        formatter = ResponseFormatter()
        response = formatter.format_query_response(
            "Show contracts",
            [],
            {}
        )

        assert "No matching contracts found" in response


class TestLLMService:
    """Test LLM service error handling"""

    def test_parse_valid_json(self):
        """Test parsing valid JSON response"""
        from app.services.llm_service import LLMService

        service = LLMService()
        content = '{"sql_query": "SELECT * FROM contracts", "mappings": {}}'

        result = service.parse_json_response(content)

        assert "sql_query" in result
        assert result["sql_query"] == "SELECT * FROM contracts"

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON raises error"""
        from app.services.llm_service import LLMService
        from app.core.exceptions import LLMValidationError

        service = LLMService()
        content = "This is not JSON"

        with pytest.raises(LLMValidationError):
            service.parse_json_response(content)


class TestMockData:
    """Test mock data generation"""

    def test_mock_data_generation(self):
        """Test that mock data is returned for all customers"""
        from app.services.query_executor import QueryExecutor

        executor = QueryExecutor()

        for customer_id in ["customer_a", "customer_b", "customer_c", "customer_d"]:
            mock_data = executor._get_mock_data(customer_id, "SELECT * FROM test")
            assert len(mock_data) > 0
            assert isinstance(mock_data, list)
            assert isinstance(mock_data[0], dict)


class TestConfiguration:
    """Test configuration management"""

    def test_settings_loaded(self):
        """Test that settings are loaded correctly"""
        from app.core.config import get_settings

        settings = get_settings()

        assert settings.AZURE_OPENAI_DEPLOYMENT_NAME == "gpt-4"
        assert settings.LLM_TEMPERATURE == 0.3
        assert settings.MAX_RETRY_ATTEMPTS == 3

    def test_allowed_origins_parsing(self):
        """Test CORS origins parsing"""
        from app.core.config import get_settings

        settings = get_settings()
        origins = settings.get_allowed_origins()

        assert isinstance(origins, list)
        assert len(origins) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
