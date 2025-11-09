"""
Response models for API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class TableJoinInfo(BaseModel):
    """Information about a table join"""
    table_name: str
    columns_used: List[str]
    join_type: Optional[str] = None  # "INNER", "LEFT", "RIGHT"
    join_condition: Optional[str] = None


class QueryOperationalInfo(BaseModel):
    """Operational information about query execution"""
    client_id: str
    database: str
    tables_used: List[str]
    joins: List[TableJoinInfo]
    total_columns: int
    execution_time_ms: Optional[float] = None
    rows_returned: int
    was_cached: bool = False


class QueryResponse(BaseModel):
    """Response model for contract queries"""

    answer: str = Field(
        ...,
        description="Natural language answer to the query"
    )
    sql_executed: Optional[str] = Field(
        None,
        description="SQL queries that were executed"
    )
    client_schemas_used: List[str] = Field(
        default_factory=list,
        description="List of client IDs queried"
    )
    semantic_mappings: Optional[Dict[str, Any]] = Field(
        None,
        description="Semantic mappings used for translation"
    )
    operational_info: Optional[List[QueryOperationalInfo]] = Field(
        None,
        description="Operational details about query execution"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Found 2 contracts across 1 client database...",
                "sql_executed": "client_a: SELECT * FROM contracts WHERE status = 'Active'",
                "client_schemas_used": ["client_a"],
                "semantic_mappings": {
                    "client_a": {
                        "explanation": "Querying active contracts"
                    }
                },
                "operational_info": [
                    {
                        "client_id": "client_a",
                        "database": "client_a.db",
                        "tables_used": ["contracts"],
                        "joins": [],
                        "total_columns": 5,
                        "execution_time_ms": 12.5,
                        "rows_returned": 2,
                        "was_cached": False
                    }
                ]
            }
        }
