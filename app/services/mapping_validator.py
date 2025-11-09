"""
Mapping validator - validates YAML mappings against actual databases
Performs multi-level validation:
1. YAML structure validation (Pydantic)
2. Database schema verification
3. Test query execution
"""
import yaml
import sqlite3
from pathlib import Path
from typing import Dict, List, Any
from datetime import date

from app.models.mapping_schema import ClientMapping, MappingValidationResult
from app.core.logging import get_logger

logger = get_logger(__name__)


class MappingValidator:
    """
    Validates pre-computed YAML mappings against actual databases

    Validation levels:
    1. YAML structure (Pydantic schema)
    2. Database existence and table verification
    3. Field existence verification
    4. Data quality checks
    5. Referential integrity checks
    """

    def __init__(self, mappings_dir: str = "data/mappings"):
        """
        Initialize validator

        Args:
            mappings_dir: Directory containing YAML mapping files
        """
        self.mappings_dir = Path(mappings_dir)
        self.loaded_mappings: Dict[str, ClientMapping] = {}

    def load_mapping(self, client_id: str) -> ClientMapping:
        """
        Load and validate YAML mapping file

        Args:
            client_id: Client identifier

        Returns:
            Validated ClientMapping object

        Raises:
            FileNotFoundError: If mapping file doesn't exist
            ValueError: If YAML is invalid
        """
        mapping_file = self.mappings_dir / f"{client_id}.yaml"

        if not mapping_file.exists():
            raise FileNotFoundError(f"Mapping file not found: {mapping_file}")

        logger.info(f"Loading mapping from {mapping_file}")

        # Load YAML
        with open(mapping_file, 'r') as f:
            yaml_data = yaml.safe_load(f)

        # Validate with Pydantic
        try:
            mapping = ClientMapping(**yaml_data)
            self.loaded_mappings[client_id] = mapping
            logger.info(f"Successfully loaded and validated mapping for {client_id}")
            return mapping
        except Exception as e:
            logger.error(f"Validation error in {mapping_file}: {e}")
            raise ValueError(f"Invalid mapping file: {e}")

    def validate_against_database(
        self,
        client_id: str,
        mapping: ClientMapping = None
    ) -> MappingValidationResult:
        """
        Validate mapping against actual database

        Args:
            client_id: Client identifier
            mapping: Pre-loaded mapping (optional, will load if not provided)

        Returns:
            Validation result with errors and warnings
        """
        if mapping is None:
            mapping = self.load_mapping(client_id)

        result = MappingValidationResult(
            is_valid=True,
            client_id=client_id
        )

        # Connect to database
        try:
            db_path = mapping.metadata.database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Cannot connect to database: {e}")
            return result

        # Level 1: Verify required tables exist
        result.tables_verified = self._verify_tables(
            cursor, mapping.validation.required_tables, result
        )

        # Level 2: Verify required fields exist
        result.fields_verified = self._verify_fields(
            cursor, mapping.validation.required_fields, result
        )

        # Level 3: Verify foreign key relationships
        if mapping.validation.referential_integrity:
            self._verify_referential_integrity(
                cursor, mapping.validation.referential_integrity, result
            )

        # Level 4: Run data quality checks
        if mapping.validation.data_quality_checks:
            self._verify_data_quality(
                cursor, mapping.validation.data_quality_checks, result
            )

        # Level 5: Verify field mappings reference valid tables/columns
        self._verify_field_mappings(
            cursor, mapping.canonical_mappings, mapping.tables, result
        )

        conn.close()

        logger.info(
            f"Validation complete for {client_id}: "
            f"valid={result.is_valid}, errors={len(result.errors)}, "
            f"warnings={len(result.warnings)}"
        )

        return result

    def _verify_tables(
        self,
        cursor: sqlite3.Cursor,
        required_tables: List[str],
        result: MappingValidationResult
    ) -> List[str]:
        """Verify all required tables exist"""
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        existing_tables = {row[0] for row in cursor.fetchall()}

        verified = []
        for table in required_tables:
            if table in existing_tables:
                verified.append(table)
            else:
                result.is_valid = False
                result.errors.append(f"Required table '{table}' does not exist")

        return verified

    def _verify_fields(
        self,
        cursor: sqlite3.Cursor,
        required_fields: Dict[str, List[str]],
        result: MappingValidationResult
    ) -> List[str]:
        """Verify all required fields exist in tables"""
        verified = []

        for table, fields in required_fields.items():
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                existing_columns = {row[1] for row in cursor.fetchall()}

                for field in fields:
                    if field in existing_columns:
                        verified.append(f"{table}.{field}")
                    else:
                        result.is_valid = False
                        result.errors.append(
                            f"Required field '{field}' does not exist in table '{table}'"
                        )
            except Exception as e:
                result.errors.append(f"Cannot inspect table '{table}': {e}")

        return verified

    def _verify_referential_integrity(
        self,
        cursor: sqlite3.Cursor,
        constraints: List[str],
        result: MappingValidationResult
    ):
        """Verify foreign key relationships"""
        for constraint in constraints:
            # Parse constraint like "contract_headers.account_id -> contract_accounts.account_id"
            if '->' not in constraint:
                result.warnings.append(f"Invalid constraint format: {constraint}")
                continue

            parts = constraint.split('->')
            if len(parts) != 2:
                result.warnings.append(f"Invalid constraint format: {constraint}")
                continue

            source = parts[0].strip()
            target = parts[1].strip()

            # Check if orphaned records exist
            source_table, source_field = source.split('.')
            target_table, target_field = target.split('.')

            try:
                query = f"""
                    SELECT COUNT(*)
                    FROM {source_table}
                    WHERE {source_field} NOT IN (SELECT {target_field} FROM {target_table})
                """
                cursor.execute(query)
                orphan_count = cursor.fetchone()[0]

                if orphan_count > 0:
                    result.warnings.append(
                        f"Referential integrity warning: {orphan_count} orphaned records "
                        f"in {source_table}.{source_field}"
                    )
            except Exception as e:
                result.warnings.append(
                    f"Could not verify constraint '{constraint}': {e}"
                )

    def _verify_data_quality(
        self,
        cursor: sqlite3.Cursor,
        checks: List[str],
        result: MappingValidationResult
    ):
        """Run data quality checks"""
        for check in checks:
            # These are descriptive checks - log as warnings if we can't verify
            result.warnings.append(f"Data quality check (manual verification needed): {check}")

    def _verify_field_mappings(
        self,
        cursor: sqlite3.Cursor,
        canonical_mappings: Dict[str, Dict[str, Any]],
        tables: Dict[str, Any],
        result: MappingValidationResult
    ):
        """Verify that field mappings reference valid tables and columns"""
        for entity, fields in canonical_mappings.items():
            for field_name, field_mapping in fields.items():
                # Skip unavailable fields
                if field_mapping.type == 'unavailable':
                    continue

                # Verify source field exists (for direct and join types)
                if field_mapping.source and '.' in field_mapping.source:
                    table, column = field_mapping.source.split('.')

                    # Check table exists
                    if table not in tables:
                        result.warnings.append(
                            f"Field {entity}.{field_name} references unknown table: {table}"
                        )
                        continue

                    # Check column exists
                    try:
                        cursor.execute(f"PRAGMA table_info({table})")
                        existing_columns = {row[1] for row in cursor.fetchall()}

                        if column not in existing_columns:
                            result.warnings.append(
                                f"Field {entity}.{field_name} references non-existent column: {table}.{column}"
                            )
                    except Exception as e:
                        result.warnings.append(
                            f"Cannot verify field {entity}.{field_name}: {e}"
                        )


def validate_all_mappings(mappings_dir: str = "data/mappings") -> Dict[str, MappingValidationResult]:
    """
    Validate all YAML mapping files in directory

    Args:
        mappings_dir: Directory containing mapping files

    Returns:
        Dictionary mapping client_id to validation results
    """
    validator = MappingValidator(mappings_dir)
    results = {}

    # Find all YAML files
    mapping_files = Path(mappings_dir).glob("*.yaml")

    for mapping_file in mapping_files:
        client_id = mapping_file.stem  # filename without extension

        try:
            mapping = validator.load_mapping(client_id)
            result = validator.validate_against_database(client_id, mapping)
            results[client_id] = result

            # Log summary
            status = "✓ VALID" if result.is_valid else "✗ INVALID"
            logger.info(
                f"{status} - {client_id}: "
                f"{len(result.errors)} errors, {len(result.warnings)} warnings"
            )

        except Exception as e:
            logger.error(f"Failed to validate {client_id}: {e}")
            results[client_id] = MappingValidationResult(
                is_valid=False,
                client_id=client_id,
                errors=[str(e)]
            )

    return results
