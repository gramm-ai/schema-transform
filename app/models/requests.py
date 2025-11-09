"""
Request models for API endpoints
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class QueryRequest(BaseModel):
    """Request model for contract queries"""

    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language question about contracts"
    )
    client_ids: Optional[List[str]] = Field(
        None,
        description="Specific client IDs to query, or None to query all clients"
    )

    @field_validator('question')
    @classmethod
    def validate_question(cls, v):
        """Validate question doesn't contain SQL injection attempts"""
        # Block common SQL injection patterns
        dangerous_patterns = [
            '--', ';--', '/*', '*/', 'xp_', 'sp_', 'exec',
            'execute', 'drop table', 'drop database', 'truncate',
            'delete from', 'insert into', 'update set',
            '<script', 'javascript:', 'onerror='
        ]

        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError(
                    f"Question contains potentially dangerous pattern: '{pattern}'. "
                    "Please rephrase your question."
                )

        return v.strip()

    @field_validator('client_ids')
    @classmethod
    def validate_client_ids(cls, v):
        """Validate client IDs are alphanumeric"""
        if v is None:
            return v

        valid_pattern = r'^[a-z0-9_]+$'
        import re

        for client_id in v:
            if not re.match(valid_pattern, client_id):
                raise ValueError(
                    f"Invalid client ID: '{client_id}'. "
                    "Must contain only lowercase letters, numbers, and underscores."
                )

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Show me all active contracts",
                "client_ids": ["client_a", "client_b"]
            }
        }
