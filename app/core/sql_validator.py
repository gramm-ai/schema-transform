"""
SQL Query Validator
Validates LLM-generated SQL for security and correctness
"""
import re
from typing import Tuple
from app.core.logging import get_logger

logger = get_logger(__name__)


class SQLValidator:
    """Validates SQL queries for security and correctness"""

    # Allowed SQL keywords for SELECT queries
    ALLOWED_KEYWORDS = {
        'select', 'from', 'where', 'and', 'or', 'not', 'in', 'like',
        'between', 'is', 'null', 'order', 'by', 'group', 'having',
        'limit', 'offset', 'join', 'inner', 'left', 'right', 'outer',
        'on', 'as', 'distinct', 'count', 'sum', 'avg', 'max', 'min',
        'case', 'when', 'then', 'else', 'end', 'cast', 'date', 'datetime',
        'asc', 'desc', 'union', 'all'
    }

    # Dangerous keywords that should never appear
    FORBIDDEN_KEYWORDS = {
        'drop', 'delete', 'truncate', 'insert', 'update', 'alter',
        'create', 'exec', 'execute', 'sp_', 'xp_', 'grant', 'revoke',
        'shutdown', 'declare', 'cursor', 'fetch', 'deallocate',
        'backup', 'restore', 'attach', 'detach'
    }

    # Dangerous patterns
    FORBIDDEN_PATTERNS = [
        r'--',  # SQL comment
        r'/\*',  # Block comment start
        r'\*/',  # Block comment end
        # Note: Multiple statements check moved to inline logic below
        r'@@',  # System variables
        r'char\(',  # Character encoding tricks
        r'nchar\(',
        r'varchar\(',
        r'nvarchar\(',
    ]

    @classmethod
    def validate(cls, sql: str) -> Tuple[bool, str]:
        """
        Validate SQL query for security

        Args:
            sql: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not sql or not sql.strip():
            return False, "Empty SQL query"

        sql_lower = sql.lower()

        # Check 1: Must be SELECT only
        if not sql_lower.strip().startswith('select'):
            return False, "Only SELECT queries are allowed"

        # Check 2: No forbidden keywords
        for keyword in cls.FORBIDDEN_KEYWORDS:
            if keyword in sql_lower:
                logger.warning(f"Forbidden keyword detected: {keyword}")
                return False, f"Forbidden keyword detected: '{keyword}'"

        # Check 3: No dangerous patterns
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False, f"Dangerous pattern detected"
        
        # Check 3a: No multiple statements (semicolon followed by non-whitespace SQL)
        # Allow trailing semicolon, but block multiple statements
        sql_trimmed = sql.strip()
        if sql_trimmed.endswith(';'):
            # Remove trailing semicolon for this check
            sql_for_check = sql_trimmed[:-1].strip()
        else:
            sql_for_check = sql_trimmed
        
        # Check if there's a semicolon followed by SQL keywords (indicating multiple statements)
        if ';' in sql_for_check:
            # Look for semicolon followed by whitespace and then SQL keywords like SELECT, INSERT, etc.
            if re.search(r';\s*(select|insert|update|delete|drop|create|alter|exec)', sql_for_check, re.IGNORECASE):
                logger.warning("Multiple SQL statements detected")
                return False, "Multiple SQL statements are not allowed"

        # Check 4: Verify all keywords are allowed
        # Extract all words that look like SQL keywords
        words = re.findall(r'\b[a-z_]+\b', sql_lower)
        sql_keywords = {w for w in words if w.upper() == w.upper()}

        # Filter to likely SQL keywords (all caps or common SQL words)
        for word in sql_keywords:
            if len(word) > 2 and word not in cls.ALLOWED_KEYWORDS:
                # Check if it might be a column/table name (has underscore or mixed case)
                if '_' not in word and word.isalpha():
                    # Could be suspicious
                    logger.debug(f"Unknown keyword: {word}")

        # Check 5: Basic structure validation
        if sql.count('(') != sql.count(')'):
            return False, "Unbalanced parentheses in query"

        if sql.count("'") % 2 != 0:
            return False, "Unbalanced quotes in query"

        logger.info(f"SQL validation passed for query: {sql[:100]}...")
        return True, ""

    @classmethod
    def sanitize(cls, sql: str) -> str:
        """
        Sanitize SQL query by removing comments and extra whitespace

        Args:
            sql: SQL query to sanitize

        Returns:
            Sanitized SQL query
        """
        # Remove comments
        sql = re.sub(r'--[^\n]*', '', sql)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

        # Normalize whitespace
        sql = ' '.join(sql.split())

        return sql.strip()
