"""
Pydantic models for validating pre-computed YAML mappings
Ensures mapping files are correctly structured and complete
"""
from typing import Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import date


class MappingMetadata(BaseModel):
    """Metadata about the mapping file"""
    client_id: str = Field(..., description="Client database identifier")
    database: str = Field(..., description="Path to database file")
    description: str = Field(..., description="Human-readable description of schema")
    schema_complexity: Literal["low", "medium", "high"] = Field(..., description="Complexity level")
    last_validated: str = Field(..., description="Date mapping was last validated (YYYY-MM-DD format)")


class FieldMapping(BaseModel):
    """Mapping for a single canonical field"""
    source: Optional[str] = Field(None, description="Source field/table (e.g., 'contracts.contract_id')")
    type: Literal["direct", "calculated", "join", "unavailable"] = Field(..., description="Type of mapping")
    formula: Optional[str] = Field(None, description="Calculation formula if type=calculated")
    source_fields: Optional[List[str]] = Field(None, description="Source fields used in calculation")
    requires_join: Optional[List[str]] = Field(None, description="Tables that must be joined")
    filter: Optional[str] = Field(None, description="Additional filter condition")
    value_mapping: Optional[Dict[Union[str, bool], Union[str, int]]] = Field(
        None, description="Value transformation map (e.g., boolean to integer)"
    )
    note: str = Field(..., description="Explanation of the mapping (LLM-generated or human-provided)")

    @validator('formula')
    def formula_required_for_calculated(cls, v, values):
        """Ensure formula is provided for calculated fields"""
        if values.get('type') == 'calculated' and not v:
            raise ValueError("Formula is required for calculated field types")
        return v

    @validator('source')
    def source_required_for_direct_and_join(cls, v, values):
        """Ensure source is provided for direct and join fields"""
        if values.get('type') in ['direct', 'join'] and not v:
            raise ValueError(f"Source is required for {values.get('type')} field types")
        return v


class TableInfo(BaseModel):
    """Information about a table in the client schema"""
    primary_key: Optional[str] = Field(None, description="Primary key column name")
    description: str = Field(..., description="What this table represents")
    foreign_keys: Optional[Dict[str, str]] = Field(None, description="Foreign key mappings")
    row_count_estimate: Optional[int] = Field(None, description="Approximate row count")


class JoinDefinition(BaseModel):
    """Definition of a join between tables"""
    name: str = Field(..., description="Descriptive name for this join")
    from_table: str = Field(..., description="Source table")
    to_table: str = Field(..., description="Target table")
    join_type: Literal["INNER", "LEFT", "RIGHT", "FULL"] = Field(..., description="SQL join type")
    on_condition: str = Field(..., description="Join condition (e.g., 'a.id = b.a_id')")
    note: str = Field(..., description="Explanation of why this join is needed")


class ValidationRules(BaseModel):
    """Validation rules for the mapping"""
    required_tables: List[str] = Field(..., description="Tables that must exist")
    required_fields: Dict[str, List[str]] = Field(..., description="Required fields per table")
    data_quality_checks: Optional[List[str]] = Field(None, description="Data quality assertions")
    referential_integrity: Optional[List[str]] = Field(None, description="Foreign key constraints to verify")


class ClientMapping(BaseModel):
    """Complete mapping configuration for a client database"""
    metadata: MappingMetadata
    canonical_mappings: Dict[str, Dict[str, FieldMapping]] = Field(
        ..., description="Mappings from canonical schema to client schema"
    )
    tables: Dict[str, TableInfo] = Field(..., description="Client table information")
    joins: List[JoinDefinition] = Field(default_factory=list, description="Join definitions")
    supported_queries: Optional[List[str]] = Field(None, description="Query patterns this client supports well")
    query_limitations: Optional[List[str]] = Field(None, description="Known limitations")
    validation: ValidationRules = Field(..., description="Validation rules")

    @validator('canonical_mappings')
    def validate_canonical_entities(cls, v):
        """Ensure at least 'contract' entity is mapped"""
        if 'contract' not in v:
            raise ValueError("'contract' entity must be present in canonical_mappings")
        return v


class MappingValidationResult(BaseModel):
    """Result of validating a mapping against actual database"""
    is_valid: bool
    client_id: str
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    validated_at: date = Field(default_factory=date.today)
    tables_verified: List[str] = Field(default_factory=list)
    fields_verified: List[str] = Field(default_factory=list)
