"""
Response formatting service
Converts query results into natural language responses
"""
from typing import List, Dict, Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class ResponseFormatter:
    """
    Formats query results into user-friendly responses

    Responsibilities:
    - Convert database results to natural language
    - Group results by customer
    - Add semantic context explanations
    """

    @staticmethod
    def format_query_response(
        question: str,
        results: List[Dict[str, Any]],
        mappings: Dict[str, Any]
    ) -> str:
        """
        Format query results into natural language response

        Args:
            question: Original user question
            results: Query results from all customers
            mappings: Semantic mappings used

        Returns:
            Formatted natural language response
        """
        if not results:
            return "No matching contracts found based on your query."

        # Group results by client
        by_client = ResponseFormatter._group_by_client(results)

        # Check if this is an aggregate query (few rows per client)
        is_aggregate = all(len(rows) <= 20 for rows in by_client.values())

        # For aggregate queries with same structure, try table format
        if is_aggregate and len(by_client) > 1:
            try:
                return ResponseFormatter._format_comparison_table(
                    question, results, by_client
                )
            except:
                # Fall back to grouped format if table fails
                pass

        # Default: Build grouped response
        response_parts = [
            f"Found {len(results)} rows across "
            f"{len(by_client)} client database(s):\n"
        ]

        for client_id, client_results in by_client.items():
            response_parts.append(
                ResponseFormatter._format_client_section(
                    client_id,
                    client_results,
                    mappings.get(client_id, {})
                )
            )

        return "\n".join(response_parts)

    @staticmethod
    def _format_comparison_table(
        question: str,
        results: List[Dict[str, Any]],
        by_client: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """
        Format results as a comparison table across clients

        Args:
            question: User's question
            results: All results
            by_client: Results grouped by client

        Returns:
            Formatted table string
        """
        # Get first result to determine grouping key (e.g., region, customer, etc.)
        sample = results[0]
        clean_sample = {k: v for k, v in sample.items() if not k.startswith("_")}

        # Find the grouping key (usually the first non-numeric field)
        group_key = None
        for key, value in clean_sample.items():
            if not isinstance(value, (int, float)) or key in ['region', 'customer', 'status', 'quarter']:
                group_key = key
                break

        if not group_key:
            raise ValueError("Cannot determine grouping key")

        # Build comparison table
        lines = [f"Found {len(results)} results across {len(by_client)} clients:\n"]

        # Collect all unique group values
        all_groups = set()
        for client_results in by_client.values():
            for row in client_results:
                all_groups.add(row.get(group_key))

        # Sort groups
        sorted_groups = sorted(all_groups, key=lambda x: str(x) if x is not None else "")

        # For each group value, show comparison across clients
        for group_val in sorted_groups:
            lines.append(f"\n**{group_key.replace('_', ' ').title()}: {group_val}**")

            for client_id, client_results in by_client.items():
                # Find matching row
                matching = [r for r in client_results if r.get(group_key) == group_val]
                if matching:
                    row = matching[0]
                    clean_row = {k: v for k, v in row.items() if not k.startswith("_") and k != group_key}
                    details = ", ".join([f"{k}: {v}" for k, v in clean_row.items()])
                    lines.append(f"  • {client_id.replace('_', ' ').title()}: {details}")

        return "\n".join(lines)

    @staticmethod
    def _group_by_client(
        results: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group results by client ID

        Args:
            results: List of result dictionaries

        Returns:
            Dictionary mapping client_id to their results
        """
        by_client = {}
        for result in results:
            client_id = result.get("_client_id", "unknown")
            if client_id not in by_client:
                by_client[client_id] = []
            by_client[client_id].append(result)
        return by_client

    @staticmethod
    def _format_client_section(
        client_id: str,
        results: List[Dict[str, Any]],
        mapping: Dict[str, Any]
    ) -> str:
        """
        Format results for a single client

        Args:
            client_id: Client identifier
            results: Results for this client
            mapping: Semantic mapping for this client

        Returns:
            Formatted section string
        """
        lines = [f"\n**{client_id.replace('_', ' ').title()}:**"]

        # Format each result (limit to 10 for readability)
        for i, result in enumerate(results[:10], 1):
            # Remove internal fields
            clean_result = {
                k: v for k, v in result.items()
                if not k.startswith("_")
            }

            # Format as bullet points
            details = ", ".join([f"{k}: {v}" for k, v in clean_result.items()])
            lines.append(f"  {i}. {details}")

        if len(results) > 10:
            lines.append(f"  ... and {len(results) - 10} more")

        return "\n".join(lines)
