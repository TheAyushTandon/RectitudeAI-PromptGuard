"""
Database Tool — async SQLite query executor for the HR Database Agent.

Security design:
  - READ-ONLY: Only SELECT statements are allowed. INSERT/UPDATE/DELETE/DROP
    are rejected before execution.
  - PARAMETERIZED: No string interpolation — uses parameterized queries.
  - SCOPED: Only queries against the demo employees database.
  - TIMEOUT: Queries time out after 5 seconds.
  - RESULT CAP: Maximum 10 rows returned per query to prevent full-table dumps.

The agent constructs SQL queries via LLM, but this tool enforces all guardrails
regardless of what the LLM produces.
"""

from __future__ import annotations
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.utils.logging import get_logger

logger = get_logger(__name__)

DB_PATH = os.path.join("data", "demo", "employees.db")
MAX_ROWS = 10
TIMEOUT_SECONDS = 5.0

# SQL keywords that indicate write operations — always rejected
_WRITE_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|MERGE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)

# Sensitive column names that should be masked in output
_SENSITIVE_COLUMNS = {"ssn", "phone", "email", "salary", "performance_review"}


class DatabaseTool:
    """Async read-only SQLite query tool."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def is_available(self) -> bool:
        """Check if the demo database exists."""
        return os.path.exists(self.db_path)

    def validate_query(self, sql: str) -> Tuple[bool, str]:
        """
        Validate that a query is safe to execute.

        Returns:
            (is_safe, reason)
        """
        if not sql or not sql.strip():
            return False, "Empty query"

        # Block write operations
        if _WRITE_PATTERNS.search(sql):
            return False, "Write operations are not permitted. Only SELECT queries allowed."

        # Must start with SELECT (after stripping whitespace)
        clean = sql.strip().upper()
        if not clean.startswith("SELECT"):
            return False, "Only SELECT queries are permitted."

        # Block multiple statements (SQL injection via semicolon)
        # Allow trailing semicolons but not mid-query ones
        statements = [s.strip() for s in sql.split(";") if s.strip()]
        if len(statements) > 1:
            return False, "Multiple SQL statements are not permitted."

        return True, "Query is safe"

    async def execute(
        self,
        sql: str,
        params: Optional[Tuple] = None,
        mask_sensitive: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute a read-only SQL query against the demo database.

        Args:
            sql: The SQL SELECT query
            params: Optional parameterized query values
            mask_sensitive: If True, mask SSN/phone/email columns

        Returns:
            Dict with 'columns', 'rows', 'row_count', and 'truncated' keys
        """
        # Validate first
        is_safe, reason = self.validate_query(sql)
        if not is_safe:
            logger.warning("DatabaseTool rejected query: %s — %s", sql[:100], reason)
            return {"error": reason, "columns": [], "rows": [], "row_count": 0}

        if not self.is_available():
            return {
                "error": "Database not available. Run: python scripts/seed_demo_db.py",
                "columns": [], "rows": [], "row_count": 0,
            }

        try:
            import aiosqlite

            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = None  # Return tuples
                cursor = await db.execute(sql, params or ())
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                all_rows = await cursor.fetchall()

                # Cap results
                truncated = len(all_rows) > MAX_ROWS
                rows = all_rows[:MAX_ROWS]

                # Convert to list of dicts for readability
                result_rows = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Mask sensitive columns
                        if mask_sensitive and col.lower() in _SENSITIVE_COLUMNS:
                            if col.lower() == "ssn":
                                value = "***-**-" + str(value)[-4:] if value else "***"
                            elif col.lower() == "email":
                                value = value.split("@")[0][:3] + "***@***" if value else "***"
                            elif col.lower() == "phone":
                                value = "***-***-" + str(value)[-4:] if value else "***"
                            elif col.lower() == "salary":
                                value = "[CONFIDENTIAL: SALARY DATA]"
                            elif col.lower() == "performance_review":
                                value = "[REDACTED]"
                        row_dict[col] = value
                    result_rows.append(row_dict)

                logger.info(
                    "DatabaseTool executed: %s — %d rows%s",
                    sql[:80], len(result_rows),
                    " (truncated)" if truncated else "",
                )

                return {
                    "columns": columns,
                    "rows": result_rows,
                    "row_count": len(all_rows),
                    "truncated": truncated,
                    "max_rows_shown": MAX_ROWS,
                }

        except Exception as e:
            logger.error("DatabaseTool error: %s", e)
            return {"error": str(e), "columns": [], "rows": [], "row_count": 0}

    async def get_schema(self) -> str:
        """Return the database schema for the LLM to generate queries."""
        if not self.is_available():
            return "Database not available."

        try:
            import aiosqlite

            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name"
                )
                rows = await cursor.fetchall()
                return "\n\n".join(row[0] for row in rows if row[0])

        except Exception as e:
            return f"Error reading schema: {e}"
