"""
Custom exception hierarchy for better error handling
Different exception types allow for different handling strategies
"""


class SchemaTranslatorError(Exception):
    """Base exception for all application errors"""
    pass


class CustomerNotFoundError(SchemaTranslatorError):
    """Raised when customer ID is not found in schema registry"""
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        super().__init__(f"Customer '{customer_id}' not found in schema registry")


class LLMGenerationError(SchemaTranslatorError):
    """
    Raised when LLM fails to generate valid response
    This is typically a transient error that should be retried
    """
    pass


class LLMValidationError(SchemaTranslatorError):
    """
    Raised when LLM response doesn't match expected format
    This indicates we need to fall back to rule-based approach
    """
    pass


class DatabaseConnectionError(SchemaTranslatorError):
    """
    Raised when database connection fails
    Should trigger fallback to mock data in demo mode
    """
    pass


class InvalidSQLError(SchemaTranslatorError):
    """
    Raised when generated SQL is invalid or unsafe
    Contains both the SQL and reason for rejection
    """
    def __init__(self, sql: str, reason: str):
        self.sql = sql
        self.reason = reason
        super().__init__(f"Invalid SQL: {reason}")


class QueryExecutionError(SchemaTranslatorError):
    """Raised when SQL query execution fails"""
    pass
