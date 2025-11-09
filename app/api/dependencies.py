"""
Dependency injection for FastAPI endpoints
Demonstrates dependency injection pattern for testability
"""
from app.services import (
    SchemaMapper,
    get_schema_mapper,
    QueryExecutor,
    get_query_executor,
    LLMService,
    get_llm_service
)
from app.models.schemas import SchemaRepository, get_schema_repository


def get_mapper() -> SchemaMapper:
    """
    Dependency: Get schema mapper instance

    This allows easy mocking in tests:
    app.dependency_overrides[get_mapper] = lambda: MockMapper()
    """
    return get_schema_mapper()


def get_executor() -> QueryExecutor:
    """
    Dependency: Get query executor instance
    """
    return get_query_executor()


def get_llm() -> LLMService:
    """
    Dependency: Get LLM service instance
    """
    return get_llm_service()


def get_repo() -> SchemaRepository:
    """
    Dependency: Get schema repository instance
    """
    return get_schema_repository()
