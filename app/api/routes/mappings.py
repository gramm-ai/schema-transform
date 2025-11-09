"""
API Routes for Schema Mapping Generation
Provides endpoints for on-demand mapping generation and validation
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import yaml
from pathlib import Path
from datetime import datetime

from app.services.mapping_generator import MappingGenerator
from app.services.mapping_validator import MappingValidator
from app.services.llm_service import LLMService
from app.models.schemas import CANONICAL_SCHEMA, CLIENT_SCHEMAS
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/mappings", tags=["mappings"])


class GenerateMappingRequest(BaseModel):
    """Request model for mapping generation"""
    client_id: str
    description: Optional[str] = None
    save_yaml: bool = True
    run_validation: bool = True


class GenerateMappingResponse(BaseModel):
    """Response model for mapping generation"""
    success: bool
    client_id: str
    compatibility_score: int = Field(..., description="Compatibility score (0-100)")
    yaml_path: Optional[str] = None
    diagram_mermaid_path: Optional[str] = None
    diagram_svg_path: Optional[str] = None
    validation_status: Optional[str] = None
    error_count: int = 0
    warning_count: int = 0
    generated_at: str


@router.post("/generate", response_model=GenerateMappingResponse)
async def generate_mapping(request: GenerateMappingRequest):
    """
    Generate schema mapping for a client database

    This endpoint:
    1. Introspects the client's database schema
    2. Uses LLM to generate semantic mappings
    3. Validates the generated mapping
    4. Saves YAML mapping file (optional)
    5. Returns Markdown report

    Args:
        request: GenerateMappingRequest with client_id and options

    Returns:
        GenerateMappingResponse with report and status
    """
    try:
        logger.info(f"Starting mapping generation for {request.client_id}")

        # Validate client exists
        if request.client_id not in CLIENT_SCHEMAS:
            raise HTTPException(
                status_code=404,
                detail=f"Client '{request.client_id}' not found. Available clients: {list(CLIENT_SCHEMAS.keys())}"
            )

        # Get database path
        client_schema = CLIENT_SCHEMAS[request.client_id]
        connection_info = client_schema.get('connection', {})
        database_path = connection_info.get('database')

        if not database_path:
            raise HTTPException(
                status_code=400,
                detail=f"No database path configured for client '{request.client_id}'"
            )

        # Check database exists
        if not Path(database_path).exists():
            raise HTTPException(
                status_code=404,
                detail=f"Database file not found: {database_path}"
            )

        # Initialize generator
        llm_service = LLMService()
        generator = MappingGenerator(llm_service=llm_service)

        # Generate mapping
        logger.info(f"Generating mapping for {request.client_id}...")
        mapping, generation_log = await generator.generate_mapping(
            client_id=request.client_id,
            database_path=database_path,
            canonical_schema=CANONICAL_SCHEMA,
            description=request.description or f"Auto-generated mapping for {request.client_id}"
        )

        logger.info(f"Mapping generated successfully for {request.client_id}")

        # Validate mapping (optional)
        validation_result = None
        if request.run_validation:
            logger.info(f"Validating mapping for {request.client_id}...")
            validator = MappingValidator()
            validation_result = validator.validate_against_database(
                client_id=request.client_id,
                mapping=mapping
            )
            logger.info(
                f"Validation complete: valid={validation_result.is_valid}, "
                f"errors={len(validation_result.errors)}, "
                f"warnings={len(validation_result.warnings)}"
            )

        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create directories
        mappings_dir = Path("data/mappings")
        mappings_dir.mkdir(parents=True, exist_ok=True)

        diagrams_dir = Path("logs/mapping/diagrams")
        diagrams_dir.mkdir(parents=True, exist_ok=True)

        # Save YAML file (optional)
        yaml_path = None
        diagram_mermaid_path = None
        diagram_svg_path = None

        if request.save_yaml:
            yaml_path = str(mappings_dir / f"{request.client_id}.yaml")

            # Convert mapping to dict for YAML serialization
            mapping_dict = mapping.dict(exclude_none=False)

            # Write YAML with comments
            with open(yaml_path, 'w') as f:
                f.write(f"# Schema Mapping: {request.client_id} → Canonical\n")
                f.write(f"# Auto-generated with LLM assistance\n")
                f.write(f"# Generated: {timestamp}\n")
                f.write(f"# Last updated: {mapping.metadata.last_validated}\n\n")
                yaml.dump(mapping_dict, f, default_flow_style=False, sort_keys=False)

            logger.info(f"YAML mapping saved to {yaml_path}")

        # Diagram generation disabled (no longer required)
        # diagram_mermaid_path and diagram_svg_path remain None

        # Calculate compatibility score
        total_fields = 0
        available_fields = 0
        for entity, fields in mapping.canonical_mappings.items():
            for field_name, field_mapping in fields.items():
                total_fields += 1
                if field_mapping.type != "unavailable":
                    available_fields += 1
        compatibility_score = int((available_fields / total_fields) * 100) if total_fields > 0 else 0

        # Build response
        response = GenerateMappingResponse(
            success=True,
            client_id=request.client_id,
            compatibility_score=compatibility_score,
            yaml_path=yaml_path,
            diagram_mermaid_path=diagram_mermaid_path,
            diagram_svg_path=diagram_svg_path,
            validation_status="valid" if (validation_result and validation_result.is_valid) else "invalid" if validation_result else "not_run",
            error_count=len(validation_result.errors) if validation_result else 0,
            warning_count=len(validation_result.warnings) if validation_result else 0,
            generated_at=timestamp
        )

        logger.info(f"Mapping generation complete for {request.client_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate mapping for {request.client_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Mapping generation failed: {str(e)}"
        )


@router.get("/status/{client_id}")
async def get_mapping_status(client_id: str):
    """
    Check if a mapping exists for a client and when it was last updated

    Args:
        client_id: Client identifier

    Returns:
        Mapping status information
    """
    try:
        mappings_dir = Path("data/mappings")
        yaml_path = mappings_dir / f"{client_id}.yaml"

        if not yaml_path.exists():
            return {
                "exists": False,
                "client_id": client_id,
                "yaml_path": None,
                "last_updated": None
            }

        # Load mapping to get metadata
        validator = MappingValidator(mappings_dir=str(mappings_dir))
        mapping = validator.load_mapping(client_id)

        return {
            "exists": True,
            "client_id": client_id,
            "yaml_path": str(yaml_path),
            "last_updated": mapping.metadata.last_validated,
            "schema_complexity": mapping.metadata.schema_complexity,
            "description": mapping.metadata.description
        }

    except Exception as e:
        logger.error(f"Failed to get mapping status for {client_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check mapping status: {str(e)}"
        )


@router.get("/list")
async def list_mappings():
    """
    List all available mappings

    Returns:
        List of mapping files with metadata
    """
    try:
        mappings_dir = Path("data/mappings")

        if not mappings_dir.exists():
            return {"mappings": []}

        validator = MappingValidator(mappings_dir=str(mappings_dir))
        mapping_files = list(mappings_dir.glob("*.yaml"))

        mappings = []
        for mapping_file in mapping_files:
            client_id = mapping_file.stem

            try:
                mapping = validator.load_mapping(client_id)
                mappings.append({
                    "client_id": client_id,
                    "yaml_path": str(mapping_file),
                    "last_updated": mapping.metadata.last_validated,
                    "schema_complexity": mapping.metadata.schema_complexity,
                    "description": mapping.metadata.description
                })
            except Exception as e:
                logger.warning(f"Failed to load mapping {client_id}: {e}")
                mappings.append({
                    "client_id": client_id,
                    "yaml_path": str(mapping_file),
                    "error": str(e)
                })

        return {"mappings": mappings}

    except Exception as e:
        logger.error(f"Failed to list mappings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list mappings: {str(e)}"
        )
