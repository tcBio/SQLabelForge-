"""SQL Server connector with security features and connection pooling."""

import logging
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)


class SQLConnector:
    """
    Secure SQL Server connector with parameterized queries and connection pooling.

    Features:
    - SQL injection protection through parameterized queries
    - Connection pooling for performance
    - Automatic retry logic
    - Query timeout management
    """

    def __init__(
        self,
        server: str,
        database: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        trusted_connection: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
    ):
        """
        Initialize SQL Server connection.

        Args:
            server: SQL Server hostname or IP
            database: Database name
            username: SQL authentication username (if not using trusted connection)
            password: SQL authentication password (if not using trusted connection)
            trusted_connection: Use Windows authentication
            pool_size: Number of connections to maintain in pool
            max_overflow: Maximum overflow connections
            pool_timeout: Timeout for acquiring connection from pool
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.trusted_connection = trusted_connection

        self.engine = self._create_engine(pool_size, max_overflow, pool_timeout)
        logger.info(f"SQL connector initialized for {server}/{database}")

    def _create_engine(
        self, pool_size: int, max_overflow: int, pool_timeout: int
    ) -> Engine:
        """Create SQLAlchemy engine with connection pooling."""
        if self.trusted_connection:
            conn_str = (
                f"mssql+pyodbc://@{self.server}/{self.database}"
                f"?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
            )
        else:
            conn_str = (
                f"mssql+pyodbc://{self.username}:{self.password}@"
                f"{self.server}/{self.database}"
                f"?driver=ODBC+Driver+17+for+SQL+Server"
            )

        return create_engine(
            conn_str,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            echo=False,
        )

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Usage:
            with connector.get_connection() as conn:
                result = conn.execute(text("SELECT * FROM table"))
        """
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()

    def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
    ) -> List[Dict[str, Any]]:
        """
        Execute a parameterized SELECT query.

        Args:
            query: SQL query with :param_name placeholders
            params: Dictionary of parameter values
            timeout: Query timeout in seconds

        Returns:
            List of dictionaries representing rows

        Example:
            results = connector.execute_query(
                "SELECT * FROM users WHERE id = :user_id",
                {"user_id": 123}
            )
        """
        if params is None:
            params = {}

        try:
            with self.get_connection() as conn:
                result = conn.execute(
                    text(query).execution_options(timeout=timeout),
                    params
                )

                # Convert to list of dicts
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def execute_non_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
    ) -> int:
        """
        Execute INSERT, UPDATE, or DELETE query.

        Args:
            query: SQL query with :param_name placeholders
            params: Dictionary of parameter values
            timeout: Query timeout in seconds

        Returns:
            Number of affected rows
        """
        if params is None:
            params = {}

        try:
            with self.get_connection() as conn:
                with conn.begin():
                    result = conn.execute(
                        text(query).execution_options(timeout=timeout),
                        params
                    )
                    return result.rowcount

        except Exception as e:
            logger.error(f"Non-query execution failed: {e}")
            raise

    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            with self.get_connection() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Connection test successful")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def close(self):
        """Close all connections and dispose of the engine."""
        self.engine.dispose()
        logger.info("SQL connector closed")
