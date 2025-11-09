"""
Query endpoints - handles contract queries
Demonstrates clean API layer with dependency injection
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
import time
import re
import asyncio

from app.models.requests import QueryRequest
from app.models.responses import QueryResponse, QueryOperationalInfo, TableJoinInfo
from app.services import SchemaMapper, QueryExecutor, ResponseFormatter
from app.api.dependencies import get_mapper, get_executor
from app.models.schemas import get_schema_repository
from app.core.logging import get_logger
from app.core.exceptions import CustomerNotFoundError, LLMGenerationError

logger = get_logger(__name__)

router = APIRouter(prefix="", tags=["queries"])


def analyze_sql_for_operational_info(client_id: str, sql_query: str, schema: dict) -> QueryOperationalInfo:
    """
    Analyze SQL query to extract operational information

    Args:
        client_id: Customer identifier
        sql_query: SQL query string
        schema: Customer schema definition

    Returns:
        QueryOperationalInfo with metadata about the query
    """
    # Extract table names from FROM and JOIN clauses
    tables_pattern = r'FROM\s+(\w+)|JOIN\s+(\w+)'
    table_matches = re.findall(tables_pattern, sql_query, re.IGNORECASE)
    tables_used = list(set(t for match in table_matches for t in match if t))

    # Extract join information
    joins = []
    join_pattern = r'(LEFT|RIGHT|INNER)?\s*JOIN\s+(\w+)(?:\s+(\w+))?\s+ON\s+([^WHERE\n]+)'
    join_matches = re.findall(join_pattern, sql_query, re.IGNORECASE)

    for match in join_matches:
        join_type = match[0].upper() if match[0] else "INNER"
        table_name = match[1]
        join_condition = match[3].strip()

        # Extract columns mentioned in this join
        columns_in_join = re.findall(r'\w+\.(\w+)', join_condition)

        joins.append(TableJoinInfo(
            table_name=table_name,
            columns_used=list(set(columns_in_join)),
            join_type=join_type,
            join_condition=join_condition
        ))

    # Count total columns in SELECT
    select_pattern = r'SELECT\s+(.*?)\s+FROM'
    select_match = re.search(select_pattern, sql_query, re.IGNORECASE | re.DOTALL)
    total_columns = 0
    if select_match:
        select_clause = select_match.group(1)
        if '*' in select_clause:
            total_columns = sum(len(table.get('columns', {})) for table in schema['tables'].values())
        else:
            # Count comma-separated items
            total_columns = len([c.strip() for c in select_clause.split(',') if c.strip()])

    return QueryOperationalInfo(
        client_id=client_id,
        database=schema['connection']['database'],
        tables_used=tables_used,
        joins=joins,
        total_columns=total_columns,
        execution_time_ms=0.0,  # Will be updated after execution
        rows_returned=0,         # Will be updated after execution
        was_cached=False         # TODO: Implement caching
    )


@router.post("/query", response_model=QueryResponse)
async def query_contracts(
    request: QueryRequest,
    mapper: SchemaMapper = Depends(get_mapper),
    executor: QueryExecutor = Depends(get_executor)
):
    """
    Natural language query across customer databases

    Automatically handles schema differences using AI.

    Args:
        request: Query request with question and optional client_id
        mapper: Schema mapper service (injected)
        executor: Query executor service (injected)

    Returns:
        QueryResponse with natural language answer and metadata
    """
    # Determine which clients to query
    if request.client_ids:
        client_ids = request.client_ids
    else:
        schema_repo = get_schema_repository()
        client_ids = schema_repo.list_clients()

    all_results = []
    all_mappings = {}
    executed_queries = []
    operational_infos = []

    # Get schema repository for operational info
    schema_repo = get_schema_repository()

    async def process_client(client_id: str):
        """Process a single client query - designed for parallel execution"""
        mapping = None
        sql_query = None
        client_results = []
        client_op_info = None
        client_executed_query = None
        
        try:
            logger.info(f"Processing query for {client_id}")

            # Get AI-powered schema mapping (this may fall back to rule-based)
            mapping = await mapper.get_mapping(client_id, request.question)
            
            sql_query = mapping.get("sql_query")
            if not sql_query:
                logger.warning(f"No SQL query generated for {client_id}")
                return None

            # Always record the SQL query attempt, even if execution fails
            client_executed_query = f"{client_id}: {sql_query}"

            # Get schema for operational info
            schema = schema_repo.get_schema(client_id)

            # Analyze SQL for operational metadata
            op_info = analyze_sql_for_operational_info(client_id, sql_query, schema)

            # Execute the generated SQL and measure time
            start_time = time.time()
            results = await executor.execute_query(client_id, sql_query)
            execution_time = (time.time() - start_time) * 1000  # Convert to ms

            # Update operational info with execution results
            op_info.execution_time_ms = round(execution_time, 2)
            op_info.rows_returned = len(results)
            client_op_info = op_info

            # Add customer context to results
            for result in results:
                result["_client_id"] = client_id
                result["_semantic_note"] = mapping.get("explanation", "")
            
            client_results = results

            logger.info(
                f"Successfully queried {client_id}: {len(results)} results in {execution_time:.2f}ms"
            )
            
            return {
                "results": client_results,
                "op_info": client_op_info,
                "executed_query": client_executed_query,
                "mapping": mapping
            }

        except CustomerNotFoundError as e:
            logger.error(f"Customer not found: {e}")
            # Don't raise here - let other clients process
            return None

        except LLMGenerationError as e:
            logger.error(f"LLM generation failed for {client_id}: {e}")
            # Try to use rule-based fallback if we haven't already
            if not mapping:
                try:
                    logger.info(f"Attempting rule-based fallback for {client_id}")
                    customer_schema = schema_repo.get_schema(client_id)
                    mapping = mapper._get_rule_based_mapping(
                        client_id,
                        request.question,
                        customer_schema
                    )
                    sql_query = mapping.get("sql_query")
                    if sql_query:
                        # Always record the SQL query attempt
                        client_executed_query = f"{client_id}: {sql_query}"
                        # Try executing the fallback query
                        start_time = time.time()
                        results = await executor.execute_query(client_id, sql_query)
                        execution_time = (time.time() - start_time) * 1000
                        for result in results:
                            result["_client_id"] = client_id
                        return {
                            "results": results,
                            "op_info": None,
                            "executed_query": client_executed_query,
                            "mapping": mapping
                        }
                except Exception as fallback_error:
                    logger.error(f"Rule-based fallback also failed for {client_id}: {fallback_error}")
            return None

        except Exception as e:
            logger.exception(f"Error querying {client_id}: {e}")
            # Return mapping if we got one, even if execution failed
            if mapping:
                return {
                    "results": [],
                    "op_info": None,
                    "executed_query": None,
                    "mapping": mapping
                }
            return None

    # Process all clients in parallel for better performance
    logger.info(f"Processing queries for {len(client_ids)} clients in parallel")
    results_list = await asyncio.gather(*[process_client(client_id) for client_id in client_ids])
    
    # Aggregate results from all clients (mappings are already in process_client's return)
    for i, result_data in enumerate(results_list):
        if result_data:
            all_results.extend(result_data["results"])
            if result_data.get("executed_query"):
                executed_queries.append(result_data["executed_query"])
            if result_data.get("op_info"):
                operational_infos.append(result_data["op_info"])
            # Aggregate mappings - use index to match client_id
            if result_data.get("mapping") and i < len(client_ids):
                all_mappings[client_ids[i]] = result_data["mapping"]

    # Format natural language response
    formatter = ResponseFormatter()
    answer = formatter.format_query_response(
        request.question,
        all_results,
        all_mappings
    )

    return QueryResponse(
        answer=answer,
        sql_executed="\n".join(executed_queries) if executed_queries else None,
        client_schemas_used=client_ids,
        semantic_mappings=all_mappings,
        operational_info=operational_infos if operational_infos else None
    )
