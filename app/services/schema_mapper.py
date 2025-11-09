"""
Schema mapping service - orchestrates AI-powered schema translation
Demonstrates separation of concerns and dependency injection
"""
import json
import re
from typing import Dict, Any
from functools import lru_cache
import hashlib

from app.core.logging import get_logger
from app.core.exceptions import LLMValidationError, LLMGenerationError
from app.models.schemas import SchemaRepository, get_schema_repository
from app.services.llm_service import LLMService, get_llm_service

logger = get_logger(__name__)

# Simple async-compatible cache for LLM results
_llm_cache: Dict[str, str] = {}
_cache_stats = {"hits": 0, "misses": 0}


class SchemaMapper:
    """
    Orchestrates AI-powered schema mapping

    Responsibilities:
    - Build prompts for LLM
    - Validate LLM responses
    - Fallback to rule-based queries when LLM fails
    """

    def __init__(
        self,
        schema_repo: SchemaRepository = None,
        llm_service: LLMService = None
    ):
        """
        Initialize schema mapper

        Args:
            schema_repo: Schema repository (injected for testing)
            llm_service: LLM service (injected for testing)
        """
        self.schema_repo = schema_repo or get_schema_repository()
        self.llm_service = llm_service or get_llm_service()

    async def get_mapping(
        self,
        client_id: str,
        user_question: str
    ) -> Dict[str, Any]:
        """
        Get schema mapping for a user question

        Args:
            client_id: Customer identifier
            user_question: Natural language question

        Returns:
            Dictionary with sql_query, mappings, calculations, explanation

        Raises:
            CustomerNotFoundError: If customer not found
        """
        # Get schemas (will raise CustomerNotFoundError if not found)
        customer_schema = self.schema_repo.get_schema(client_id)
        canonical_schema = self.schema_repo.get_canonical_schema()

        # Try AI-powered mapping first
        try:
            return await self._get_ai_mapping(
                client_id,
                user_question,
                customer_schema,
                canonical_schema
            )
        except LLMValidationError as e:
            # LLM returned invalid response - expected failure mode
            logger.warning(
                f"LLM validation failed for {client_id}: {e}. "
                f"Falling back to rule-based query."
            )
            return self._get_rule_based_mapping(
                client_id,
                user_question,
                customer_schema
            )
        except LLMGenerationError as e:
            # LLM service error (timeout, rate limit, etc.)
            logger.error(
                f"LLM generation error for {client_id}: {e}. "
                f"Falling back to rule-based query."
            )
            return self._get_rule_based_mapping(
                client_id,
                user_question,
                customer_schema
            )
        except Exception as e:
            # Unexpected error - log with stack trace
            logger.error(
                f"Unexpected error in AI mapping for {client_id}: {e}",
                exc_info=True
            )
            # Still fallback to rule-based approach
            return self._get_rule_based_mapping(
                client_id,
                user_question,
                customer_schema
            )

    async def _get_cached_ai_mapping(
        self,
        client_id: str,
        user_question: str,
        customer_schema_json: str,
        canonical_schema_json: str
    ) -> str:
        """
        Cached LLM mapping generation (returns JSON string for caching)

        Args:
            client_id: Customer identifier
            user_question: User's question
            customer_schema_json: Customer schema as JSON string
            canonical_schema_json: Canonical schema as JSON string

        Returns:
            Mapping as JSON string
        """
        # Create cache key from inputs
        cache_key = hashlib.sha256(
            f"{client_id}:{user_question}:{customer_schema_json}:{canonical_schema_json}".encode()
        ).hexdigest()
        
        # Check cache first
        if cache_key in _llm_cache:
            _cache_stats["hits"] += 1
            logger.debug(f"Cache hit for {client_id}: {user_question[:50]}")
            return _llm_cache[cache_key]
        
        _cache_stats["misses"] += 1
        
        customer_schema = json.loads(customer_schema_json)
        canonical_schema = json.loads(canonical_schema_json)

        # Build prompt
        prompt = self._build_mapping_prompt(
            user_question,
            customer_schema,
            canonical_schema
        )

        # Call LLM (with automatic retry)
        messages = [
            {
                "role": "system",
                "content": "You are a SQL and schema mapping expert. "
                          "Always return valid JSON."
            },
            {"role": "user", "content": prompt}
        ]

        response_content = await self.llm_service.generate_completion(messages)

        # Parse and validate response
        mapping = self.llm_service.parse_json_response(response_content)

        # Validate required fields
        required_fields = ["sql_query", "mappings", "explanation"]
        missing = [f for f in required_fields if f not in mapping]
        if missing:
            raise LLMValidationError(
                f"LLM response missing required fields: {missing}"
            )

        # Ensure calculations field exists
        if "calculations" not in mapping:
            mapping["calculations"] = {}

        logger.info(
            f"Successfully generated AI mapping for {client_id}: "
            f"{mapping['explanation']}"
        )

        # Convert to JSON string and cache it
        mapping_json = json.dumps(mapping)
        _llm_cache[cache_key] = mapping_json
        
        # Return as JSON string for caching
        return mapping_json

    async def _get_ai_mapping(
        self,
        client_id: str,
        user_question: str,
        customer_schema: Dict[str, Any],
        canonical_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to generate schema mapping (with caching)

        Args:
            client_id: Customer identifier
            user_question: User's question
            customer_schema: Customer's schema
            canonical_schema: Canonical schema

        Returns:
            Mapping dictionary with SQL and explanations
        """
        # Convert schemas to JSON strings for cache key
        customer_schema_json = json.dumps(customer_schema, sort_keys=True)
        canonical_schema_json = json.dumps(canonical_schema, sort_keys=True)

        # Get cached result (or generate new one)
        logger.debug(f"Checking cache for {client_id}: {user_question[:50]}...")
        mapping_json = await self._get_cached_ai_mapping(
            client_id,
            user_question,
            customer_schema_json,
            canonical_schema_json
        )

        # Check cache info
        total = _cache_stats["hits"] + _cache_stats["misses"]
        if total > 0:
            hit_rate = _cache_stats["hits"] / total * 100
            logger.info(
                f"LLM cache stats - hits: {_cache_stats['hits']}, "
                f"misses: {_cache_stats['misses']}, "
                f"hit_rate: {hit_rate:.1f}%"
            )
        else:
            logger.info("LLM cache stats - first call")

        # Parse back to dictionary
        return json.loads(mapping_json)

    def _build_mapping_prompt(
        self,
        user_question: str,
        customer_schema: Dict[str, Any],
        canonical_schema: Dict[str, Any]
    ) -> str:
        """
        Build prompt for LLM to generate schema mapping

        Args:
            user_question: User's question
            customer_schema: Customer schema
            canonical_schema: Canonical schema

        Returns:
            Formatted prompt string
        """
        return f"""You are a database schema expert. A user wants to query a customer's database.

User Question: {user_question}

Canonical Schema (our standard):
{json.dumps(canonical_schema, indent=2)}

Customer Schema:
{json.dumps(customer_schema['tables'], indent=2)}

Semantic Context: {customer_schema.get('semantic_context', 'None provided')}

Based on the user's question, provide:
1. The SQL query to execute on the customer's actual schema
2. Semantic mappings explaining how customer fields map to canonical concepts
3. Any calculations needed (e.g., if customer stores annual value but user asks for total value)

Respond in JSON format:
{{
    "sql_query": "SELECT ... FROM ...",
    "mappings": {{
        "canonical_field": "customer_field",
        ...
    }},
    "calculations": {{
        "field": "calculation description",
        ...
    }},
    "explanation": "Brief explanation of the mapping"
}}
"""

    def _get_rule_based_mapping(
        self,
        client_id: str,
        user_question: str,
        customer_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback: Generate mapping using simple rules

        This demonstrates graceful degradation when AI fails.

        Args:
            client_id: Customer identifier
            user_question: User's question
            customer_schema: Customer schema

        Returns:
            Mapping dictionary with SQL
        """
        logger.info(f"Using rule-based mapping for {client_id}")

        question_lower = user_question.lower()
        tables = list(customer_schema['tables'].keys())
        if not tables:
            logger.error(f"No tables found in schema for {client_id}")
            return {
                "sql_query": "SELECT 1 WHERE 1=0",  # Empty result query
                "mappings": {},
                "calculations": {},
                "explanation": f"Rule-based fallback: No tables available for {client_id}"
            }
        
        main_table = tables[0]  # Use first table as main table
        
        # Determine database type
        db_type = customer_schema.get("connection", {}).get("type", "sqlite")
        is_sqlite = db_type == "sqlite"

        # Get available columns from the main table
        main_table_cols = customer_schema['tables'].get(main_table, {}).get('columns', {})
        col_names = list(main_table_cols.keys()) if main_table_cols else []

        # Build SELECT clause - try to identify relevant columns
        select_cols = []
        if "total" in question_lower and "value" in question_lower:
            # Aggregate query - look for value columns
            for col in col_names:
                if any(keyword in col.lower() for keyword in ['value', 'amount', 'price', 'cost']):
                    select_cols.append(col)
                    break
            if "region" in question_lower:
                for col in col_names:
                    if any(keyword in col.lower() for keyword in ['region', 'location', 'area']):
                        select_cols.append(col)
                        break
        elif "average" in question_lower or "annual" in question_lower:
            for col in col_names:
                if any(keyword in col.lower() for keyword in ['annual', 'revenue', 'value', 'amount']):
                    select_cols.append(col)
                    break
            if "customer" in question_lower:
                for col in col_names:
                    if any(keyword in col.lower() for keyword in ['customer', 'client', 'account']):
                        select_cols.append(col)
                        break
        elif "expire" in question_lower or "expir" in question_lower:
            for col in col_names:
                if any(keyword in col.lower() for keyword in ['expir', 'end', 'terminat']):
                    select_cols.append(col)
                    break

        if not select_cols:
            select_cols = ["*"]  # Fallback to all columns

        # Build SQL with proper syntax for database type
        if select_cols == ["*"]:
            if is_sqlite:
                sql_parts = [f"SELECT * FROM {main_table} LIMIT 100"]
            else:
                sql_parts = [f"SELECT TOP 100 * FROM {main_table}"]
        else:
            sql_parts = [f"SELECT {', '.join(select_cols)} FROM {main_table}"]
            if is_sqlite:
                sql_parts.append("LIMIT 100")
            else:
                # Insert TOP after SELECT
                sql_parts[0] = f"SELECT TOP 100 {', '.join(select_cols)} FROM {main_table}"

        # Add WHERE clause for common keywords
        where_clauses = []
        if "active" in question_lower:
            status_cols = [col for col in col_names if 'status' in col.lower() or 'state' in col.lower()]
            if status_cols:
                status_col = status_cols[0]
                where_clauses.append(f"{status_col} = 'Active'")
            else:
                where_clauses.append("status = 'Active'")
        
        if "expir" in question_lower or "expire" in question_lower:
            expir_cols = [col for col in col_names if 'expir' in col.lower() or 'end' in col.lower() or 'terminat' in col.lower()]
            if expir_cols:
                expir_col = expir_cols[0]
                if is_sqlite:
                    if "quarter" in question_lower and "2025" in question_lower:
                        where_clauses.append(f"strftime('%Y', {expir_col}) = '2025'")
                    else:
                        where_clauses.append(f"{expir_col} IS NOT NULL")
                else:
                    if "quarter" in question_lower and "2025" in question_lower:
                        where_clauses.append(f"YEAR({expir_col}) = 2025")
                    else:
                        where_clauses.append(f"{expir_col} IS NOT NULL")
        
        if "compare" in question_lower or "vs" in question_lower:
            # Group by status
            status_cols = [col for col in col_names if 'status' in col.lower()]
            if status_cols:
                status_col = status_cols[0]
                sql_parts.insert(-1 if is_sqlite else 1, f"GROUP BY {status_col}")

        if where_clauses:
            sql_parts.append(f"WHERE {' AND '.join(where_clauses)}")

        sql_query = " ".join(sql_parts)

        return {
            "sql_query": sql_query,
            "mappings": {},
            "calculations": {},
            "explanation": (
                f"Rule-based fallback query for {client_id}. "
                f"Generated simple query based on keywords."
            )
        }


@lru_cache()
def get_schema_mapper() -> SchemaMapper:
    """
    Get cached schema mapper instance

    Returns:
        SchemaMapper instance
    """
    return SchemaMapper()
