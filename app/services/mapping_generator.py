"""
LLM-Powered Mapping Generator
Generates YAML mappings by analyzing database schema and using LLM for semantic understanding
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

from app.services.llm_service import LLMService
from app.models.mapping_schema import ClientMapping, FieldMapping, TableInfo, JoinDefinition, ValidationRules, MappingMetadata
from app.core.logging import get_logger

logger = get_logger(__name__)


class MappingGenerator:
    """
    Generates pre-computed YAML mappings by analyzing database schema
    Uses LLM to understand semantic relationships and generate notes
    """

    def __init__(self, llm_service: LLMService = None):
        """
        Initialize mapping generator

        Args:
            llm_service: LLM service for semantic analysis (optional, creates new if not provided)
        """
        self.llm_service = llm_service or LLMService()

    async def generate_mapping(
        self,
        client_id: str,
        database_path: str,
        canonical_schema: Dict[str, Dict[str, str]],
        description: str = ""
    ) -> Tuple[ClientMapping, str]:
        """
        Generate complete mapping for a client database

        Args:
            client_id: Client identifier
            database_path: Path to SQLite database
            canonical_schema: The canonical schema to map to
            description: Human-readable description of client

        Returns:
            Tuple of (ClientMapping object, generation_log)
        """
        logger.info(f"Starting mapping generation for {client_id}")
        generation_log = []

        # Step 1: Introspect database schema
        generation_log.append("=== Step 1: Database Introspection ===")
        schema_info = self._introspect_database(database_path)
        generation_log.append(f"Found {len(schema_info['tables'])} tables")
        for table_name in schema_info['tables'].keys():
            generation_log.append(f"  - {table_name}")

        # Step 2: Discover join paths
        generation_log.append("\n=== Step 2: Join Path Discovery ===")
        join_paths = self._discover_joins(schema_info)
        generation_log.append(f"Found {len(join_paths)} join relationships")
        for join in join_paths:
            generation_log.append(f"  - {join['from_table']} → {join['to_table']}")

        # Step 3: Sample data for semantic understanding
        generation_log.append("\n=== Step 3: Data Sampling ===")
        data_samples = self._sample_data(database_path, schema_info)

        # Step 4: Generate field mappings using LLM
        generation_log.append("\n=== Step 4: LLM Semantic Mapping ===")
        field_mappings = await self._generate_field_mappings(
            canonical_schema,
            schema_info,
            data_samples,
            join_paths,
            generation_log
        )

        # Step 5: Detect schema complexity
        complexity = self._assess_complexity(schema_info, join_paths)
        generation_log.append(f"\n=== Schema Complexity: {complexity.upper()} ===")

        # Step 6: Build ClientMapping object
        metadata = MappingMetadata(
            client_id=client_id,
            database=database_path,
            description=description or f"Auto-generated mapping for {client_id}",
            schema_complexity=complexity,
            last_validated=datetime.now().strftime("%Y-%m-%d")
        )

        # Convert join paths to JoinDefinition objects
        joins = []
        for jp in join_paths:
            joins.append(JoinDefinition(
                name=jp['name'],
                from_table=jp['from_table'],
                to_table=jp['to_table'],
                join_type=jp['join_type'],
                on_condition=jp['on_condition'],
                note=jp['note']
            ))

        # Build table info
        tables = {}
        for table_name, table_data in schema_info['tables'].items():
            tables[table_name] = TableInfo(
                primary_key=table_data.get('primary_key'),
                description=f"Table with {len(table_data['columns'])} columns",
                foreign_keys=table_data.get('foreign_keys', {}),
                row_count_estimate=table_data.get('row_count', 0)
            )

        # Validation rules
        validation = ValidationRules(
            required_tables=list(schema_info['tables'].keys()),
            required_fields=self._extract_required_fields(schema_info),
            data_quality_checks=[],
            referential_integrity=self._build_integrity_checks(join_paths)
        )

        mapping = ClientMapping(
            metadata=metadata,
            canonical_mappings=field_mappings,
            tables=tables,
            joins=joins,
            validation=validation
        )

        generation_log.append("\n=== Mapping Generation Complete ===")

        return mapping, "\n".join(generation_log)

    def _introspect_database(self, database_path: str) -> Dict[str, Any]:
        """
        Extract complete schema information from SQLite database

        Returns:
            Dict with tables, columns, foreign keys, primary keys
        """
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        schema_info = {
            'tables': {},
            'database_path': database_path
        }

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            # Get column info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = []
            primary_key = None

            for row in cursor.fetchall():
                col_info = {
                    'name': row[1],
                    'type': row[2],
                    'notnull': bool(row[3]),
                    'default': row[4],
                    'pk': bool(row[5])
                }
                columns.append(col_info)

                if col_info['pk']:
                    primary_key = col_info['name']

            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            foreign_keys = {}
            for row in cursor.fetchall():
                fk_column = row[3]
                ref_table = row[2]
                ref_column = row[4]
                foreign_keys[fk_column] = f"{ref_table}.{ref_column}"

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]

            schema_info['tables'][table] = {
                'columns': columns,
                'primary_key': primary_key,
                'foreign_keys': foreign_keys,
                'row_count': row_count
            }

        conn.close()
        return schema_info

    def _discover_joins(self, schema_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Discover join relationships from foreign keys

        Returns:
            List of join definitions
        """
        joins = []

        for table_name, table_data in schema_info['tables'].items():
            for fk_column, ref_field in table_data['foreign_keys'].items():
                ref_table, ref_column = ref_field.split('.')

                # Determine join type (INNER vs LEFT)
                # Use LEFT if foreign key is nullable, INNER otherwise
                join_type = "INNER"
                for col in table_data['columns']:
                    if col['name'] == fk_column and not col['notnull']:
                        join_type = "LEFT"
                        break

                joins.append({
                    'name': f"{table_name}_to_{ref_table}",
                    'from_table': table_name,
                    'to_table': ref_table,
                    'join_type': join_type,
                    'on_condition': f"{table_name}.{fk_column} = {ref_table}.{ref_column}",
                    'note': f"Foreign key relationship from {table_name}.{fk_column} to {ref_table}.{ref_column}"
                })

        return joins

    def _sample_data(self, database_path: str, schema_info: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Sample data from each table for semantic understanding

        Returns:
            Dict mapping table name to list of sample rows
        """
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        samples = {}

        for table_name in schema_info['tables'].keys():
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()

            # Get column names
            column_names = [desc[0] for desc in cursor.description]

            # Convert to list of dicts
            samples[table_name] = [
                dict(zip(column_names, row)) for row in rows
            ]

        conn.close()
        return samples

    async def _generate_field_mappings(
        self,
        canonical_schema: Dict[str, Dict[str, str]],
        schema_info: Dict[str, Any],
        data_samples: Dict[str, List[Dict]],
        join_paths: List[Dict[str, str]],
        generation_log: List[str]
    ) -> Dict[str, Dict[str, FieldMapping]]:
        """
        Use LLM to generate field mappings with notes

        Returns:
            Nested dict: entity -> field_name -> FieldMapping
        """
        import asyncio
        
        mappings = {}

        # For now, focus on "contract" entity (main entity)
        canonical_fields = canonical_schema.get('contract', {})

        # Build context for LLM
        context = self._build_llm_context(schema_info, data_samples, join_paths)

        generation_log.append("Analyzing field mappings...")

        # Ask LLM to map each canonical field (process in parallel for better performance)
        contract_mappings = {}

        # Create tasks for parallel processing
        tasks = []
        field_names_list = []
        
        for field_name, field_description in canonical_fields.items():
            generation_log.append(f"  Mapping: {field_name}")
            tasks.append(
                self._map_field_with_llm(
                    field_name,
                    field_description,
                    context,
                    schema_info,
                    join_paths
                )
            )
            field_names_list.append(field_name)

        # Execute all mappings in parallel
        mapping_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, (field_name, result) in enumerate(zip(field_names_list, mapping_results)):
            if isinstance(result, Exception):
                logger.error(f"Failed to map {field_name}: {result}")
                mapping = FieldMapping(
                    source=None,
                    type="unavailable",
                    note=f"Auto-mapping failed: {str(result)}"
                )
            else:
                mapping = result
            contract_mappings[field_name] = mapping
            generation_log.append(f"    → {mapping.type}: {mapping.source or mapping.formula or 'N/A'}")

        mappings['contract'] = contract_mappings

        return mappings

    def _build_llm_context(
        self,
        schema_info: Dict[str, Any],
        data_samples: Dict[str, List[Dict]],
        join_paths: List[Dict[str, str]]
    ) -> str:
        """Build comprehensive context string for LLM"""

        lines = ["=== Database Schema ===\n"]

        for table_name, table_data in schema_info['tables'].items():
            lines.append(f"Table: {table_name}")
            lines.append(f"  Primary Key: {table_data['primary_key']}")
            lines.append(f"  Columns ({len(table_data['columns'])}):")

            for col in table_data['columns']:
                lines.append(f"    - {col['name']} ({col['type']}) {'NOT NULL' if col['notnull'] else 'NULLABLE'}")

            if table_data['foreign_keys']:
                lines.append("  Foreign Keys:")
                for fk, ref in table_data['foreign_keys'].items():
                    lines.append(f"    - {fk} → {ref}")

            # Sample data
            if table_name in data_samples and data_samples[table_name]:
                lines.append("  Sample Data (first row):")
                sample = data_samples[table_name][0]
                for key, value in sample.items():
                    lines.append(f"    - {key} = {repr(value)}")

            lines.append("")

        if join_paths:
            lines.append("=== Available Joins ===")
            for join in join_paths:
                lines.append(f"  {join['from_table']} → {join['to_table']} ({join['join_type']})")
                lines.append(f"    ON: {join['on_condition']}")
            lines.append("")

        return "\n".join(lines)

    async def _map_field_with_llm(
        self,
        field_name: str,
        field_description: str,
        context: str,
        schema_info: Dict[str, Any],
        join_paths: List[Dict[str, str]]
    ) -> FieldMapping:
        """
        Use LLM to map a single canonical field

        Returns:
            FieldMapping object with type, source, formula, note
        """

        prompt = f"""You are a database schema mapping expert. Your task is to map a canonical field to a client's database schema.

{context}

CANONICAL FIELD TO MAP:
- Field Name: {field_name}
- Description: {field_description}

TASK:
Analyze the client's schema and determine how to map this canonical field.

Output a JSON object with:
{{
    "type": "direct|calculated|join|unavailable",
    "source": "table.column (if direct/join, null otherwise)",
    "formula": "SQL expression (if calculated, null otherwise)",
    "source_fields": ["table.column", ...] (if calculated, null otherwise),
    "requires_join": ["table_name", ...] (if join needed, null otherwise),
    "note": "Brief explanation of the mapping logic"
}}

MAPPING TYPES:
- direct: 1:1 field mapping (e.g., contracts.customer_name → customer)
- calculated: Requires formula (e.g., total_value = ARR × term / 12)
- join: Requires joining another table
- unavailable: Field doesn't exist in this schema

IMPORTANT:
- Be concise in notes (1-2 sentences max)
- For calculated fields, provide exact SQL formula
- If a field is truly unavailable, explain why
- Consider data samples when determining mappings

Return ONLY the JSON object, no other text."""

        try:
            messages = [
                {"role": "system", "content": "You are a database schema mapping expert."},
                {"role": "user", "content": prompt}
            ]
            response = await self.llm_service.generate_completion(messages, temperature=0.1)

            # Parse JSON response using LLM service helper
            mapping_data = self.llm_service.parse_json_response(response)

            # Build FieldMapping object
            return FieldMapping(
                source=mapping_data.get('source'),
                type=mapping_data['type'],
                formula=mapping_data.get('formula'),
                source_fields=mapping_data.get('source_fields'),
                requires_join=mapping_data.get('requires_join'),
                note=mapping_data['note']
            )

        except Exception as e:
            logger.error(f"LLM mapping failed for {field_name}: {e}")
            # Fallback: mark as unavailable
            return FieldMapping(
                source=None,
                type="unavailable",
                note=f"Auto-mapping failed: {str(e)}"
            )

    def _assess_complexity(self, schema_info: Dict[str, Any], join_paths: List[Dict]) -> str:
        """
        Assess schema complexity: low, medium, high

        Based on:
        - Number of tables
        - Number of joins required
        - Presence of calculated fields
        """
        num_tables = len(schema_info['tables'])
        num_joins = len(join_paths)

        if num_tables == 1 and num_joins == 0:
            return "low"
        elif num_tables <= 2 and num_joins <= 1:
            return "medium"
        else:
            return "high"

    def _extract_required_fields(self, schema_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract required fields (non-nullable, non-PK) per table"""
        required = {}

        for table_name, table_data in schema_info['tables'].items():
            required_cols = []
            for col in table_data['columns']:
                # Consider NOT NULL columns (except auto-increment PKs)
                if col['notnull'] or col['pk']:
                    required_cols.append(col['name'])

            if required_cols:
                required[table_name] = required_cols

        return required

    def _build_integrity_checks(self, join_paths: List[Dict[str, str]]) -> List[str]:
        """Build referential integrity check strings"""
        checks = []

        for join in join_paths:
            # Extract FK relationship from on_condition
            # Format: "table1.col1 = table2.col2"
            parts = join['on_condition'].split('=')
            if len(parts) == 2:
                source = parts[0].strip()
                target = parts[1].strip()
                checks.append(f"{source} -> {target}")

        return checks
